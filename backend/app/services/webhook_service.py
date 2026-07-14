"""Webhook service — business logic for processing GitHub webhook payloads.

Routes validate and delegate here; this module handles data extraction,
repository upsert, and pull request creation/update.
Per rules.md: no business logic in route handlers.
"""

import logging
from datetime import datetime

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.db.models.pull_request import PullRequest
from app.db.models.repository import Repository
from app.schemas.webhook import PullRequestWebhookPayload

logger = logging.getLogger(__name__)


def _parse_iso_datetime(value: str) -> datetime:
    """Parse a GitHub ISO-8601 timestamp into a timezone-aware datetime."""
    # GitHub uses format: 2024-01-15T10:30:00Z
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def upsert_repository(db: Session, payload: PullRequestWebhookPayload) -> Repository:
    """Find or create a Repository record from a webhook payload.

    Uses ``github_id`` for lookup. Creates on first encounter, updates
    metadata on subsequent calls.
    """
    repo_data = payload.repository
    repo = (
        db.query(Repository)
        .filter(
            Repository.github_id == repo_data.id,
        )
        .first()
    )

    if repo is None:
        repo = Repository(
            github_id=repo_data.id,
            owner=repo_data.owner.login,
            name=repo_data.name,
            full_name=repo_data.full_name,
            url=repo_data.html_url,
            is_active=True,
        )
        db.add(repo)
        db.flush()  # Assign an id before using it as FK.
        logger.info(
            "Created repository",
            extra={"repo_full_name": repo.full_name, "repo_id": repo.id},
        )
    else:
        # Update mutable fields in case they changed (e.g. repo renamed).
        repo.owner = repo_data.owner.login
        repo.name = repo_data.name
        repo.full_name = repo_data.full_name
        repo.url = repo_data.html_url
        logger.info(
            "Updated existing repository",
            extra={"repo_full_name": repo.full_name, "repo_id": repo.id},
        )

    return repo


def upsert_pull_request(
    db: Session,
    payload: PullRequestWebhookPayload,
    repository: Repository,
) -> PullRequest:
    """Create or update a PullRequest record from a webhook payload.

    Uses ``github_pr_id`` for lookup. On ``synchronize`` events the head_sha
    is updated; on ``reopened`` the status is reset to ``open``.
    """
    pr_data = payload.pull_request

    pr = (
        db.query(PullRequest)
        .filter(
            PullRequest.github_pr_id == pr_data.id,
        )
        .first()
    )

    if pr is None:
        pr = PullRequest(
            repository_id=repository.id,
            github_pr_id=pr_data.id,
            number=pr_data.number,
            title=pr_data.title,
            author=pr_data.user.login,
            status=pr_data.state,
            head_sha=pr_data.head.sha,
            base_branch=pr_data.base.ref,
            head_branch=pr_data.head.ref,
            body=pr_data.body,
            opened_at=_parse_iso_datetime(pr_data.created_at),
        )
        db.add(pr)
        logger.info(
            "Created pull request",
            extra={
                "pr_number": pr.number,
                "repo_id": repository.id,
                "action": payload.action,
            },
        )
    else:
        # Update fields that may change across events.
        pr.title = pr_data.title
        pr.status = pr_data.state
        pr.head_sha = pr_data.head.sha
        pr.body = pr_data.body
        logger.info(
            "Updated pull request",
            extra={
                "pr_number": pr.number,
                "repo_id": repository.id,
                "action": payload.action,
            },
        )

    return pr


async def run_review_agent_task(owner: str, repo: str, pull_number: int, pr_id: int) -> None:
    """Run the LangGraph Review pipeline and update the Review model."""
    from app.api.deps import get_db_session
    from app.orchestrator.graph import build_review_graph
    from app.db.models.review import Review

    try:
        graph = build_review_graph()
        initial_state = {
            "owner": owner,
            "repo": repo,
            "pull_number": pull_number,
            "pr_id": pr_id
        }
        
        results = await graph.ainvoke(initial_state)
        
        # Save results to db
        with get_db_session() as db:
            review = db.query(Review).filter(Review.pull_request_id == pr_id).first()
            if not review:
                review = Review(pull_request_id=pr_id)
                db.add(review)
                
            if results.get("error"):
                review.status = "error"
            else:
                final_review = results.get("final_review", {})
                review.status = final_review.get("status", "completed")
                review.bug_prediction_results = final_review.get("bug_probabilities")
                review.static_analysis_results = final_review.get("static_analysis")
                review.security_results = final_review.get("security_findings")
                review.explainability_results = final_review.get("explanations")
            db.commit()
    except Exception as e:
        logger.exception(f"Review pipeline failed for PR {pull_number}: {e}")
        with get_db_session() as db:
            review = db.query(Review).filter(Review.pull_request_id == pr_id).first()
            if not review:
                review = Review(pull_request_id=pr_id)
                db.add(review)
            review.status = "error"
            db.commit()


def process_pull_request_event(
    db: Session,
    payload: PullRequestWebhookPayload,
    background_tasks: BackgroundTasks,
) -> PullRequest:
    """Top-level handler: upsert repo + PR inside a single transaction.

    Per rules.md §5: use transactions for multi-step writes; roll back
    fully on failure.
    """
    try:
        repository = upsert_repository(db, payload)
        pr = upsert_pull_request(db, payload, repository)
        db.commit()
        db.refresh(pr)
        
        # Enqueue the ReviewAgent task
        background_tasks.add_task(
            run_review_agent_task,
            repository.owner,
            repository.name,
            pr.number,
            pr.id,
        )
        
        return pr
    except Exception:
        db.rollback()
        logger.exception(
            "Failed to process pull request event",
            extra={"action": payload.action},
        )
        raise

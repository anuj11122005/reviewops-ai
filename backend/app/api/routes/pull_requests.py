"""Pull Request API routes — list and detail endpoints for the dashboard.

Named ``pull_requests.py`` (not ``reviews.py``) to reserve the "reviews"
namespace for Phase 2 AI review output.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.pull_request import PullRequest
from app.schemas.pull_request import PullRequestListResponse, PullRequestResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pull-requests", tags=["pull-requests"])


@router.get(
    "",
    response_model=PullRequestListResponse,
    summary="List all pull requests",
)
def list_pull_requests(
    db: Session = Depends(get_db),
    repository_id: Annotated[
        int | None, Query(description="Filter by repository")
    ] = None,
) -> PullRequestListResponse:
    """Return all pull requests, optionally filtered by repository."""
    query = db.query(PullRequest).order_by(PullRequest.created_at.desc())
    if repository_id is not None:
        query = query.filter(PullRequest.repository_id == repository_id)
    prs = query.all()
    return PullRequestListResponse(
        items=[PullRequestResponse.model_validate(p) for p in prs],
        total=len(prs),
    )


@router.get(
    "/{pr_id}",
    response_model=PullRequestResponse,
    summary="Get a single pull request",
)
def get_pull_request(
    pr_id: int,
    db: Session = Depends(get_db),
) -> PullRequestResponse:
    """Return a single pull request by its internal id."""
    pr = db.query(PullRequest).filter(PullRequest.id == pr_id).first()
    if pr is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Pull request {pr_id} not found",
                    "details": None,
                }
            },
        )
    return PullRequestResponse.model_validate(pr)

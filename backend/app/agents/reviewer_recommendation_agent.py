"""Reviewer Recommendation Agent: Suggests human reviewers based on file history."""

import hashlib
import logging
from collections import Counter
from typing import Any

from app.agents.exceptions import AgentExecutionError
from app.integrations.github_client import GitHubClient

logger = logging.getLogger(__name__)


class ReviewerRecommendationAgent:
    """Agent that recommends a reviewer by inspecting git history of modified files."""

    def __init__(self, github_client: GitHubClient) -> None:
        self.github_client = github_client

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Suggest a human reviewer.

        Returns:
            A dict containing mutated state with 'recommended_reviewer'.
        """
        pull_number = state.get("pull_number", 0)
        owner = state.get("owner", "")
        repo = state.get("repo", "")
        valid_files = state.get("valid_files", [])

        # PR author might not be explicitly in state if we just have pull_number, but
        # normally it would be passed. We'll use a placeholder if not present.
        pr_author = state.get("pr_author", "")

        input_hash = hashlib.sha256(
            f"{pull_number}:{len(valid_files)}".encode()
        ).hexdigest()
        logger.info(
            f"[ReviewerRecommendationAgent] Starting execution for PR {pull_number} (hash: {input_hash})"
        )

        if not valid_files:
            return {"recommended_reviewer": "No valid files to check."}

        try:
            author_counts: Counter[str] = Counter()
            for file_obj in valid_files:
                file_path = file_obj.get("filename", "")
                if not file_path:
                    continue

                commits = await self.github_client.get_file_commits(
                    owner, repo, file_path
                )
                for commit in commits:
                    # 'author' can be in commit['commit']['author']['name'] or commit['author']['login']
                    author_login = ""
                    if commit.get("author") and commit["author"].get("login"):
                        author_login = commit["author"]["login"]
                    elif commit.get("commit", {}).get("author", {}).get("name"):
                        author_login = commit["commit"]["author"]["name"]

                    if author_login and author_login != pr_author:
                        author_counts[author_login] += 1

            if not author_counts:
                recommended = (
                    "Could not determine a recommended reviewer based on history."
                )
            else:
                top_author = author_counts.most_common(1)[0][0]
                recommended = f"Recommended reviewer: @{top_author} (based on past commits to these files)."

            logger.info(
                f"[ReviewerRecommendationAgent] Finished execution for PR {pull_number}."
            )
            return {"recommended_reviewer": recommended}

        except Exception as e:
            logger.exception(
                f"[ReviewerRecommendationAgent] Failed execution for PR {pull_number}"
            )
            raise AgentExecutionError(
                "ReviewerRecommendationAgent", pull_number, str(e)
            ) from e

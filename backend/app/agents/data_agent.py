"""Data Agent: Downloads PR files and metadata."""

import hashlib
import logging
from typing import Any

from app.agents.exceptions import AgentExecutionError
from app.integrations.github_client import GitHubClient

logger = logging.getLogger(__name__)


class DataAgent:
    """Agent responsible for fetching raw data from external sources."""

    def __init__(self, github_client: GitHubClient) -> None:
        self.github = github_client

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Download modified files for a PR.

        Returns:
            A dict containing mutated state with 'files'.
        """
        owner = state["owner"]
        repo = state["repo"]
        pull_number = state["pull_number"]
        input_hash = hashlib.sha256(
            f"{owner}/{repo}/{pull_number}".encode()
        ).hexdigest()
        logger.info(
            f"[DataAgent] Starting execution for PR {pull_number} (hash: {input_hash})"
        )

        try:
            files_meta = await self.github.get_pr_files(owner, repo, pull_number)

            result = []
            for f in files_meta:
                # We only care about added or modified files, not deleted ones.
                if f.get("status") in ("added", "modified", "renamed"):
                    raw_url = f.get("raw_url")
                    if raw_url:
                        content = await self.github.get_file_content(raw_url)
                        result.append(
                            {
                                "filename": f["filename"],
                                "status": f["status"],
                                "content": content,
                            }
                        )

            return {"files": result}
        except Exception as e:
            logger.exception(f"[DataAgent] Failed to fetch data for PR {pull_number}")
            raise AgentExecutionError(
                "DataAgent", pull_number, state.get("head_sha", "unknown_hash"), str(e)
            ) from e

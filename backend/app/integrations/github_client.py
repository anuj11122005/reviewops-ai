"""GitHub API client with retry and backoff logic."""

import logging
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

# Basic settings for the client. We will load tokens from config if available.
# In a real GitHub App, you'd generate a JWT to get an installation access token.
# For Phase 2, we will use a basic personal access token or unauthenticated if public.


class GitHubClientError(Exception):
    """Raised when GitHub API calls fail after retries."""

    pass


class GitHubClient:
    """Client for interacting with the GitHub API."""

    def __init__(self, token: str | None = None) -> None:
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def get_pr_files(
        self, owner: str, repo: str, pull_number: int
    ) -> list[dict[str, Any]]:
        """Fetch the list of files modified in a Pull Request."""
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pull_number}/files"
        logger.info(f"Fetching PR files from {url}")

        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()  # type: ignore

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def get_file_content(self, raw_url: str) -> str:
        """Fetch the raw content of a file."""
        logger.debug(f"Fetching raw file content from {raw_url}")

        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(raw_url)
            response.raise_for_status()
            return response.text

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def post_review_comment(
        self, owner: str, repo: str, pull_number: int, body: str
    ) -> None:
        """Post a review comment to the Pull Request."""
        url = (
            f"https://api.github.com/repos/{owner}/{repo}/issues/{pull_number}/comments"
        )
        logger.info(f"Posting review comment to {url}")

        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.post(url, json={"body": body})
            response.raise_for_status()

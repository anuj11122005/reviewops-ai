"""Pydantic request/response schemas for the PullRequest resource."""

import datetime

from pydantic import BaseModel


class PullRequestResponse(BaseModel):
    """API response for a single pull request."""

    id: int
    repository_id: int
    github_pr_id: int
    number: int
    title: str
    author: str
    status: str
    head_sha: str
    base_branch: str
    head_branch: str
    body: str | None = None
    opened_at: datetime.datetime | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class PullRequestListResponse(BaseModel):
    """API response for a list of pull requests."""

    items: list[PullRequestResponse]
    total: int

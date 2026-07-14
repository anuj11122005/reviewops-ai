"""Pydantic models for GitHub webhook payloads.

Only the fields we need for Phase 1 (PR opened/synchronize) are modelled;
extra fields are ignored via ``model_config``.
"""

from pydantic import BaseModel, Field


class WebhookUser(BaseModel):
    """Minimal GitHub user representation inside a webhook payload."""

    login: str
    id: int
    avatar_url: str = ""

    model_config = {"extra": "ignore"}


class WebhookRepository(BaseModel):
    """Repository portion of a GitHub webhook payload."""

    id: int
    name: str
    full_name: str
    html_url: str
    owner: WebhookUser

    model_config = {"extra": "ignore"}


class WebhookPullRequestHead(BaseModel):
    """Head / base ref inside a PR payload."""

    ref: str
    sha: str
    label: str = ""

    model_config = {"extra": "ignore"}


class WebhookPullRequest(BaseModel):
    """The ``pull_request`` object inside a GitHub webhook payload."""

    id: int
    number: int
    title: str
    body: str | None = None
    state: str
    user: WebhookUser
    head: WebhookPullRequestHead
    base: WebhookPullRequestHead
    created_at: str
    updated_at: str

    model_config = {"extra": "ignore"}


class PullRequestWebhookPayload(BaseModel):
    """Top-level payload for a ``pull_request`` webhook event."""

    action: str
    pull_request: WebhookPullRequest = Field(..., alias="pull_request")
    repository: WebhookRepository

    model_config = {"extra": "ignore", "populate_by_name": True}


class IgnoredActionResponse(BaseModel):
    """Response returned when a webhook action is ignored."""

    status: str = "ignored"
    action: str

"""Pydantic request/response schemas for the Repository resource."""

import datetime

from pydantic import BaseModel


class RepositoryResponse(BaseModel):
    """API response for a single repository."""

    id: int
    github_id: int
    owner: str
    name: str
    full_name: str
    url: str
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


class RepositoryListResponse(BaseModel):
    """API response for a list of repositories."""

    items: list[RepositoryResponse]
    total: int

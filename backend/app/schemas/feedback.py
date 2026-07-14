from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FeedbackCreate(BaseModel):
    pull_request_id: int
    category: str
    target_identifier: str | None = None
    accepted: bool
    comment: str | None = None


class FeedbackResponse(BaseModel):
    id: int
    pull_request_id: int
    category: str
    target_identifier: str | None
    accepted: bool
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

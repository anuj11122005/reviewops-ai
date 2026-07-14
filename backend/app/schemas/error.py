"""Standard error response schema per rules.md §5.

All API errors are returned in a consistent shape:
``{"error": {"code": "...", "message": "...", "details": ...}}``
"""

from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    """Inner error payload."""

    code: str
    message: str
    details: Any | None = None


class ErrorResponse(BaseModel):
    """Wrapper matching the rules.md error contract."""

    error: ErrorDetail

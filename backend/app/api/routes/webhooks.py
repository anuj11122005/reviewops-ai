"""GitHub webhook endpoint.

Validates the incoming payload (signature, event type, action) and delegates
data extraction + persistence to the webhook service. No business logic lives
here — per rules.md, routes validate and delegate only.
"""

import json
import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_settings
from app.core.config import Settings
from app.core.security import verify_github_signature
from app.schemas.pull_request import PullRequestResponse
from app.schemas.webhook import IgnoredActionResponse, PullRequestWebhookPayload
from app.services.webhook_service import process_pull_request_event

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


def _create_error(code: str, message: str, details: Any = None) -> dict[str, Any]:
    """Helper to create a standard error dictionary."""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        }
    }


# Actions we handle in Phase 1.
_SUPPORTED_ACTIONS = {"opened", "synchronize", "reopened"}


@router.post(
    "/github",
    response_model=PullRequestResponse | IgnoredActionResponse,
    status_code=200,
    summary="Receive GitHub webhook events",
)
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),  # noqa: B008
    settings: Settings = Depends(get_settings),  # noqa: B008
    x_hub_signature_256: str | None = Header(default=None),
    x_github_event: str | None = Header(default=None),
) -> PullRequestResponse | IgnoredActionResponse:
    """Receive and process a GitHub ``pull_request`` webhook event.

    Validates:
    1. HMAC-SHA256 signature (if a secret is configured).
    2. Event type is ``pull_request``.
    3. Action is one of: ``opened``, ``synchronize``, ``reopened``.

    Then delegates to the webhook service for data extraction and persistence.
    """
    body = await request.body()

    # ── 1. Signature verification ────────────────────────
    if settings.github_webhook_secret:
        if not x_hub_signature_256:
            logger.warning("Webhook received without signature header")
            raise HTTPException(
                status_code=401,
                detail=_create_error(
                    code="MISSING_SIGNATURE",
                    message="X-Hub-Signature-256 header is required",
                ),
            )
        if not verify_github_signature(
            body, x_hub_signature_256, settings.github_webhook_secret
        ):
            raise HTTPException(
                status_code=401,
                detail=_create_error(
                    code="INVALID_SIGNATURE",
                    message="Webhook signature verification failed",
                ),
            )

    # ── 2. Event type validation ─────────────────────────
    if x_github_event != "pull_request":
        raise HTTPException(
            status_code=400,
            detail=_create_error(
                code="UNSUPPORTED_EVENT",
                message=(
                    f"Event type '{x_github_event}' is not supported; "
                    "expected 'pull_request'"
                ),
            ),
        )

    # ── 3. Parse and validate payload ────────────────────
    try:
        raw = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=422,
            detail=_create_error(
                code="INVALID_JSON",
                message="Request body is not valid JSON",
                details=str(exc),
            ),
        ) from exc

    try:
        payload = PullRequestWebhookPayload.model_validate(raw)
    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=_create_error(
                code="INVALID_PAYLOAD",
                message="Payload does not match expected pull_request webhook schema",
                details=str(exc),
            ),
        ) from exc

    # ── 4. Action filter ─────────────────────────────────
    if payload.action not in _SUPPORTED_ACTIONS:
        logger.info(
            "Ignoring unsupported action",
            extra={"action": payload.action},
        )
        return IgnoredActionResponse(action=payload.action)

    # ── 5. Delegate to service ───────────────────────────
    logger.info(
        "Processing pull_request webhook",
        extra={
            "action": payload.action,
            "repo": payload.repository.full_name,
            "pr_number": payload.pull_request.number,
        },
    )
    pr = process_pull_request_event(db, payload, background_tasks)
    return PullRequestResponse.model_validate(pr)

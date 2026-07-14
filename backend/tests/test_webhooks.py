"""Tests for the GitHub webhook endpoint (POST /api/webhooks/github).

Covers: valid payloads, missing/invalid signatures, unsupported events,
malformed JSON, invalid payload schema, and ignored actions.
"""

import json
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.pull_request import PullRequest
from app.db.models.repository import Repository
from tests.conftest import make_signature

# ── Sample payload ───────────────────────────────────

_VALID_PAYLOAD: dict[str, Any] = {
    "action": "opened",
    "pull_request": {
        "id": 123456789,
        "number": 42,
        "title": "feat: add user authentication",
        "body": "This PR adds JWT-based auth.",
        "state": "open",
        "user": {
            "login": "testuser",
            "id": 11111,
            "avatar_url": "https://avatars.githubusercontent.com/u/11111",
        },
        "head": {
            "ref": "feat/auth",
            "sha": "abc123def456789012345678901234567890abcd",
            "label": "testuser:feat/auth",
        },
        "base": {
            "ref": "main",
            "sha": "000111222333444555666777888999aaabbbcccd",
            "label": "org:main",
        },
        "created_at": "2026-07-14T10:00:00Z",
        "updated_at": "2026-07-14T10:05:00Z",
    },
    "repository": {
        "id": 987654321,
        "name": "reviewops-ai",
        "full_name": "org/reviewops-ai",
        "html_url": "https://github.com/org/reviewops-ai",
        "owner": {
            "login": "org",
            "id": 22222,
            "avatar_url": "https://avatars.githubusercontent.com/u/22222",
        },
    },
}


def _post_webhook(
    client: TestClient,
    payload: dict[str, Any] | None = None,
    *,
    event: str = "pull_request",
    signature: str | None = "auto",
    raw_body: bytes | None = None,
) -> Any:
    """Helper to POST to the webhook endpoint with correct headers."""
    body = (
        raw_body
        if raw_body is not None
        else json.dumps(payload or _VALID_PAYLOAD).encode()
    )
    headers: dict[str, str] = {"X-GitHub-Event": event}

    if signature == "auto":
        headers["X-Hub-Signature-256"] = make_signature(body)
    elif signature is not None:
        headers["X-Hub-Signature-256"] = signature

    return client.post("/api/webhooks/github", content=body, headers=headers)


# ── Happy path ───────────────────────────────────────


class TestWebhookHappyPath:
    """Tests for valid webhook payloads that should succeed."""

    def test_pr_opened_creates_records(
        self, client: TestClient, db_session: Session
    ) -> None:
        """A valid PR-opened payload should create repo + PR records."""
        response = _post_webhook(client)
        assert response.status_code == 200

        data = response.json()
        assert data["number"] == 42
        assert data["title"] == "feat: add user authentication"
        assert data["author"] == "testuser"
        assert data["status"] == "open"

        # Verify DB records.
        repos = db_session.query(Repository).all()
        assert len(repos) == 1
        assert repos[0].full_name == "org/reviewops-ai"

        prs = db_session.query(PullRequest).all()
        assert len(prs) == 1
        assert prs[0].number == 42

    def test_pr_synchronize_updates_sha(
        self, client: TestClient, db_session: Session
    ) -> None:
        """A synchronize event should update the head_sha on an existing PR."""
        # First create the PR.
        _post_webhook(client)

        # Now send a synchronize event with a new SHA.
        updated = json.loads(json.dumps(_VALID_PAYLOAD))
        updated["action"] = "synchronize"
        updated["pull_request"]["head"]["sha"] = (
            "newsha1234567890123456789012345678901234"
        )

        response = _post_webhook(client, payload=updated)
        assert response.status_code == 200
        assert response.json()["head_sha"] == "newsha1234567890123456789012345678901234"

    def test_duplicate_pr_is_idempotent(
        self, client: TestClient, db_session: Session
    ) -> None:
        """Sending the same PR-opened payload twice should not create duplicates."""
        _post_webhook(client)
        _post_webhook(client)

        assert db_session.query(PullRequest).count() == 1
        assert db_session.query(Repository).count() == 1


# ── Signature validation ─────────────────────────────


class TestWebhookSignature:
    """Tests for HMAC signature validation."""

    def test_missing_signature_returns_401(self, client: TestClient) -> None:
        response = _post_webhook(client, signature=None)
        assert response.status_code == 401
        assert response.json()["detail"]["error"]["code"] == "MISSING_SIGNATURE"

    def test_invalid_signature_returns_401(self, client: TestClient) -> None:
        response = _post_webhook(client, signature="sha256=invalid")
        assert response.status_code == 401
        assert response.json()["detail"]["error"]["code"] == "INVALID_SIGNATURE"


# ── Event type validation ────────────────────────────


class TestWebhookEventType:
    """Tests for X-GitHub-Event header validation."""

    def test_unsupported_event_returns_400(self, client: TestClient) -> None:
        response = _post_webhook(client, event="push")
        assert response.status_code == 400
        assert response.json()["detail"]["error"]["code"] == "UNSUPPORTED_EVENT"


# ── Payload validation ───────────────────────────────


class TestWebhookPayload:
    """Tests for payload parsing and schema validation."""

    def test_malformed_json_returns_422(self, client: TestClient) -> None:
        response = _post_webhook(client, raw_body=b"not-json{{{")
        assert response.status_code == 422
        assert response.json()["detail"]["error"]["code"] == "INVALID_JSON"

    def test_missing_fields_returns_422(self, client: TestClient) -> None:
        response = _post_webhook(client, payload={"action": "opened"})
        assert response.status_code == 422
        assert response.json()["detail"]["error"]["code"] == "INVALID_PAYLOAD"

    def test_ignored_action_returns_200(self, client: TestClient) -> None:
        """Actions like 'closed' should be acknowledged but not processed."""
        payload = {**_VALID_PAYLOAD, "action": "closed"}
        response = _post_webhook(client, payload=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ignored"
        assert data["action"] == "closed"

"""Shared test fixtures for the ReviewOps AI backend.

Uses an in-memory SQLite database and a FastAPI TestClient with
dependency overrides so tests don't need PostgreSQL or Redis.
"""

import hashlib
import hmac
from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings
from app.db.models import Base
from app.db.session import get_db
from app.main import app

# ── In-memory SQLite engine ──────────────────────────
_TEST_DATABASE_URL = "sqlite:///file:testdb?mode=memory&cache=shared&uri=true"
_engine = create_engine(
    _TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)


# Enable FK support in SQLite.
@event.listens_for(_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):  # type: ignore[no-untyped-def]
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


_TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)

# ── Test settings ────────────────────────────────────
_TEST_WEBHOOK_SECRET = "test-secret-key"

_test_settings = Settings(
    database_url=_TEST_DATABASE_URL,
    redis_url="redis://localhost:6379/0",
    github_webhook_secret=_TEST_WEBHOOK_SECRET,
    debug=True,
)


def _get_test_settings() -> Settings:
    return _test_settings


def _get_test_db() -> Generator[Session, None, None]:
    db = _TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Fixtures ─────────────────────────────────────────
@pytest.fixture(autouse=True)
def _setup_db() -> Generator[None, None, None]:
    """Create all tables before each test, drop them after."""
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    """FastAPI test client with dependency overrides.

    Patches ``get_settings`` globally (including calls from ``init_engine``)
    and overrides ``get_db`` to use the test SQLite database.
    """
    app.dependency_overrides[get_db] = _get_test_db
    app.dependency_overrides[get_settings] = _get_test_settings

    # Patch the cached get_settings so lifespan's init_engine uses test settings.
    with patch("app.core.config.get_settings", return_value=_test_settings):
        with patch("app.db.session.get_settings", return_value=_test_settings):
            with TestClient(app, raise_server_exceptions=False) as c:
                yield c

    app.dependency_overrides.clear()


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Direct database session for test assertions."""
    db = _TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def make_signature(payload: bytes, secret: str = _TEST_WEBHOOK_SECRET) -> str:
    """Compute a valid X-Hub-Signature-256 header for a test payload."""
    sig = hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()
    return f"sha256={sig}"

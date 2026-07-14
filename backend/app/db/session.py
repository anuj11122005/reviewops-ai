"""SQLAlchemy engine and session factory.

Provides ``get_db()`` as a FastAPI dependency that yields a scoped session
and ensures cleanup on request completion.
"""

import logging
from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_engine: Any = None
_SessionLocal: sessionmaker[Session] | None = None


def init_engine() -> None:
    """Create the global SQLAlchemy engine and session factory.

    Called once at application startup (from the FastAPI lifespan handler).
    """
    global _engine, _SessionLocal  # noqa: PLW0603
    settings = get_settings()

    # SQLite doesn't support pool_size / max_overflow.
    engine_kwargs: dict[str, Any] = {"pool_pre_ping": True}
    if not settings.database_url.startswith("sqlite"):
        engine_kwargs["pool_size"] = 5
        engine_kwargs["max_overflow"] = 10

    _engine = create_engine(settings.database_url, **engine_kwargs)
    _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    logger.info("Database engine initialised")


def get_session_factory() -> sessionmaker[Session]:
    """Return the session factory, raising if the engine hasn't been initialised."""
    if _SessionLocal is None:
        raise RuntimeError("Database engine not initialised — call init_engine() first")
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session per request."""
    session_factory = get_session_factory()
    db = session_factory()
    try:
        yield db
    finally:
        db.close()

"""Tests for application startup and configuration."""

import pytest
from fastapi import FastAPI

from app.main import lifespan


@pytest.mark.asyncio
async def test_startup_fails_without_webhook_secret_in_prod(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Confirm the app refuses to start in production without a webhook secret."""

    # Force production mode and empty secret
    monkeypatch.setenv("DEBUG", "False")
    monkeypatch.setenv("GITHUB_WEBHOOK_SECRET", "")

    # Clear the lru_cache for get_settings so it reloads env vars
    from app.core.config import get_settings

    get_settings.cache_clear()

    test_app = FastAPI()

    # Attempting to enter the lifespan context should raise RuntimeError
    with pytest.raises(
        RuntimeError, match="GITHUB_WEBHOOK_SECRET is empty in production"
    ):
        async with lifespan(test_app):
            pass

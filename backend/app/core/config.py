"""Application settings loaded from environment variables via Pydantic BaseSettings.

All secrets and configuration values are read from .env files or environment
variables — never hardcoded. Other modules import ``get_settings()`` rather
than instantiating Settings directly.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration for the ReviewOps AI backend."""

    # ── App ──────────────────────────────────────────────
    app_name: str = "ReviewOps AI"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── Database ─────────────────────────────────────────
    database_url: str = "postgresql://reviewops:reviewops@localhost:5432/reviewops"

    # ── Redis ────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── GitHub ───────────────────────────────────────────
    github_webhook_secret: str = ""

    # ── CORS ─────────────────────────────────────────────
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (singleton per process)."""
    return Settings()

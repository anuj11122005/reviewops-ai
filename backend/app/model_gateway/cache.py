"""Redis-backed caching for the Model Gateway."""

import json
import logging
from typing import Any

import redis.asyncio as redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ModelCache:
    """Redis cache for model predictions to prevent duplicate external API calls."""

    def __init__(self) -> None:
        settings = get_settings()
        self.redis = redis.from_url(settings.redis_url, decode_responses=True)
        self.ttl = 60 * 60 * 24  # 24 hours

    async def get(self, key: str) -> Any | None:
        """Retrieve a value from the cache."""
        try:
            val = await self.redis.get(key)
            if val:
                return json.loads(val)
        except Exception:
            logger.exception(f"Failed to read from cache for key: {key}")
        return None

    async def set(self, key: str, value: Any) -> None:
        """Set a value in the cache."""
        try:
            await self.redis.set(key, json.dumps(value), ex=self.ttl)
        except Exception:
            logger.exception(f"Failed to write to cache for key: {key}")

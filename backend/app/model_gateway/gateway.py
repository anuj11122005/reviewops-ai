"""Model Gateway for routing, caching, and fallback."""

import hashlib
import logging
from typing import Any

from app.model_gateway.cache import ModelCache
from app.model_gateway.providers.huggingface import HuggingFaceProvider

logger = logging.getLogger(__name__)


class ModelGatewayError(Exception):
    """Raised when the gateway cannot fulfill a request."""
    pass


class ModelGateway:
    """Central choke point for all AI model calls."""

    def __init__(self, hf_token: str | None = None) -> None:
        self.cache = ModelCache()
        self.hf_provider = HuggingFaceProvider(token=hf_token)
        # Default model for embeddings
        self.default_embedding_model = "sentence-transformers/all-MiniLM-L6-v2"

    def _generate_cache_key(self, prefix: str, data: Any) -> str:
        """Generate a consistent cache key."""
        hashed = hashlib.sha256(str(data).encode()).hexdigest()
        return f"{prefix}:{hashed}"

    async def get_embeddings(self, texts: list[str]) -> list[list[float]] | None:
        """Get embeddings, using cache and fallback logic."""
        if not texts:
            return []

        cache_key = self._generate_cache_key("embed", texts)
        cached = await self.cache.get(cache_key)
        if cached:
            logger.debug("Embeddings found in cache.")
            return cached

        logger.info(f"Fetching embeddings from HF model {self.default_embedding_model}")
        try:
            embeddings = await self.hf_provider.get_embeddings(texts, self.default_embedding_model)
            await self.cache.set(cache_key, embeddings)
            return embeddings
        except Exception as e:
            logger.exception(f"Failed to get embeddings: {e}")
            # In Phase 2, we return None if embeddings fail rather than crashing,
            # so downstream can handle it gracefully.
            return None

    async def generate_text(self, prompt: str, model: str = "HuggingFaceH4/zephyr-7b-beta") -> str | None:
        """Generate text, using cache and fallback logic."""
        if not prompt:
            return None

        cache_key = self._generate_cache_key("text_gen", f"{model}:{prompt}")
        cached = await self.cache.get(cache_key)
        if cached:
            logger.debug("Generated text found in cache.")
            return str(cached)

        logger.info(f"Generating text from HF model {model}")
        try:
            text = await self.hf_provider.generate_text(prompt, model)
            await self.cache.set(cache_key, text)
            return text
        except Exception as e:
            logger.exception(f"Failed to generate text: {e}")
            return None

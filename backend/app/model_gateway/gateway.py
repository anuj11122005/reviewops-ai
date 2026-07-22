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
        self.default_embedding_models = [
            "sentence-transformers/all-MiniLM-L6-v2",
            "BAAI/bge-small-en-v1.5",
        ]

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
            from typing import cast

            return cast(list[list[float]], cached)

        for model in self.default_embedding_models:
            logger.info(f"Fetching embeddings from HF model {model}")
            try:
                embeddings = await self.hf_provider.get_embeddings(texts, model)
                await self.cache.set(cache_key, embeddings)
                return embeddings
            except Exception as e:
                logger.warning(
                    f"Failed to get embeddings from {model}: {e}. Trying fallback..."
                )

        logger.error("All embedding models failed.")
        return None

    async def generate_text(self, prompt: str, model: str | None = None) -> str | None:
        """Generate text, using cache and fallback logic."""
        if not prompt:
            return None

        models = ["Qwen/Qwen2.5-7B-Instruct", "mistralai/Mistral-7B-Instruct-v0.3"]
        if model and model != "HuggingFaceH4/zephyr-7b-beta":
            models = [model] + models

        for m in models:
            cache_key = self._generate_cache_key("text_gen", f"{m}:{prompt}")
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug("Generated text found in cache.")
                return str(cached)

            logger.info(f"Generating text from HF model {m}")
            try:
                text = await self.hf_provider.generate_text(prompt, m)
                await self.cache.set(cache_key, text)
                return text
            except Exception as e:
                logger.warning(
                    f"Failed to generate text from {m}: {e}. Trying fallback..."
                )

        logger.error("All text generation models failed.")
        return None

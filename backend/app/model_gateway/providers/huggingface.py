"""Hugging Face provider for the Model Gateway."""

import logging
from typing import cast

from huggingface_hub import AsyncInferenceClient
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class HuggingFaceProviderError(Exception):
    """Raised when Hugging Face API calls fail."""

    pass


class HuggingFaceProvider:
    """Client for Hugging Face Inference API."""

    def __init__(self, token: str | None = None) -> None:
        # Default client for embeddings (hf-inference provider handles feature-extraction)
        self.client = AsyncInferenceClient(token=token)
        # Pinned provider for chat_completion — 'together' is the only free-tier
        # provider that reliably serves instruct models via the Inference Providers API.
        self.chat_client = AsyncInferenceClient(token=token, provider="together")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def get_embeddings(self, texts: list[str], model: str) -> list[list[float]]:
        """Get embeddings for a list of texts."""
        try:
            import numpy as np

            response = await self.client.feature_extraction(texts, model=model)
            if isinstance(response, np.ndarray):
                return cast(list[list[float]], response.tolist())
            if not isinstance(response, list):
                raise HuggingFaceProviderError(
                    f"Unexpected response type: {type(response)}"
                )
            return cast(list[list[float]], response)
        except Exception as e:
            raise HuggingFaceProviderError(f"Failed to get embeddings: {e}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def generate_text(self, prompt: str, model: str) -> str:
        """Generate text from a Hugging Face model."""
        try:
            messages = [{"role": "user", "content": prompt}]
            response = await self.chat_client.chat_completion(
                messages=messages,
                model=model,
                max_tokens=512,
            )
            return str(response.choices[0].message.content).strip()
        except Exception as e:
            raise HuggingFaceProviderError(f"Failed to generate text: {e}") from e

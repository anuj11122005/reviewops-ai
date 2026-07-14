"""Hugging Face provider for the Model Gateway."""

import logging

import httpx
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
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def get_embeddings(self, texts: list[str], model: str) -> list[list[float]]:
        """Get embeddings for a list of texts."""
        url = (
            f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"
        )

        async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
            response = await client.post(url, json={"inputs": texts})
            response.raise_for_status()

            # Hugging Face Feature Extraction pipeline returns nested lists.
            # Usually: [[embedding1], [embedding2], ...] if multiple inputs,
            # but sometimes shape varies depending on the exact model.
            result = response.json()
            if not isinstance(result, list):
                raise HuggingFaceProviderError(
                    f"Unexpected response type: {type(result)}"
                )

            return result

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError)),
        reraise=True,
    )
    async def generate_text(self, prompt: str, model: str) -> str:
        """Generate text from a Hugging Face model."""
        url = f"https://api-inference.huggingface.co/models/{model}"

        async with httpx.AsyncClient(headers=self.headers, timeout=30.0) as client:
            response = await client.post(
                url,
                json={
                    "inputs": prompt,
                    "parameters": {"max_new_tokens": 512, "return_full_text": False},
                },
            )
            response.raise_for_status()

            result = response.json()
            if (
                isinstance(result, list)
                and len(result) > 0
                and "generated_text" in result[0]
            ):
                return str(result[0]["generated_text"]).strip()
            elif isinstance(result, dict) and "generated_text" in result:
                return str(result["generated_text"]).strip()

            raise HuggingFaceProviderError(f"Unexpected response format: {result}")

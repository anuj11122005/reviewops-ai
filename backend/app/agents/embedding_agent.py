"""Embedding Agent: Generates semantic embeddings and stores them in Qdrant."""

import hashlib
import logging
from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance

from app.agents.exceptions import AgentExecutionError
from app.core.config import get_settings
from app.model_gateway.gateway import ModelGateway

logger = logging.getLogger(__name__)


class EmbeddingAgent:
    """Agent for creating and storing vector embeddings of code."""

    def __init__(self, gateway: ModelGateway) -> None:
        self.gateway = gateway
        settings = get_settings()
        # Expect Qdrant URL in real scenario, fallback to localhost for now
        self.qdrant = AsyncQdrantClient(url="http://qdrant:6333")
        self.collection_name = "pr_files"

    async def _ensure_collection(self) -> None:
        """Ensure Qdrant collection exists."""
        try:
            if not await self.qdrant.collection_exists(self.collection_name):
                await self.qdrant.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
                )
        except Exception:
            logger.exception("Failed to create Qdrant collection")

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Generate and store embeddings for PR files.

        Returns:
            A dict containing mutated state (empty for now).
        """
        pull_number = state["pull_number"]
        valid_files = state["valid_files"]
        input_hash = hashlib.sha256(f"{pull_number}:{len(valid_files)}".encode()).hexdigest()
        logger.info(f"[EmbeddingAgent] Starting execution for PR {pull_number} (hash: {input_hash})")

        if not valid_files:
            return {}

        try:
            await self._ensure_collection()
            
            texts = [f["content"][:1000] for f in valid_files]
            embeddings = await self.gateway.get_embeddings(texts)
            if not embeddings:
                logger.warning(f"[EmbeddingAgent] Failed to retrieve embeddings for PR {pull_number}")
                return {}

            points = []
            for idx, (f, emb) in enumerate(zip(valid_files, embeddings)):
                points.append(
                    PointStruct(
                        id=idx + int(input_hash[:8], 16),
                        vector=emb,
                        payload={
                            "pr_id": pull_number,
                            "filename": f["filename"]
                        }
                    )
                )
            
            if points:
                await self.qdrant.upsert(
                    collection_name=self.collection_name,
                    points=points
                )
            
            logger.info(f"[EmbeddingAgent] Finished execution for PR {pull_number}.")
            return {}

        except Exception as e:
            logger.exception(f"[EmbeddingAgent] Failed execution for PR {pull_number}")
            raise AgentExecutionError("EmbeddingAgent", pull_number, str(e)) from e

"""Test Generation Agent: Suggests unit tests for newly added functionality."""

import hashlib
import logging
from typing import Any

from app.agents.exceptions import AgentExecutionError
from app.model_gateway.gateway import ModelGateway

logger = logging.getLogger(__name__)


class TestGenerationAgent:
    """Agent that suggests unit tests for code in a PR."""

    def __init__(self, model_gateway: ModelGateway) -> None:
        self.gateway = model_gateway

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Suggest unit tests for added/modified functionality.

        Returns:
            A dict containing mutated state with 'test_suggestions'.
        """
        pull_number = state.get("pull_number", 0)
        valid_files = state.get("valid_files", [])

        input_hash = hashlib.sha256(
            f"{pull_number}:{len(valid_files)}".encode()
        ).hexdigest()
        logger.info(
            f"[TestGenerationAgent] Starting execution for PR {pull_number} (hash: {input_hash})"
        )

        if not valid_files:
            return {"test_suggestions": ""}

        try:
            files_list = [f.get("filename", "") for f in valid_files]
            
            prompt = (
                f"You are an expert QA engineer. Suggest unit tests for the following modified files in a Pull Request:\n"
                f"{', '.join(files_list)}\n\n"
                f"Provide 2-3 specific test case scenarios or code snippets."
            )

            test_suggestions = await self.gateway.generate_text(prompt)

            logger.info(
                f"[TestGenerationAgent] Finished execution for PR {pull_number}."
            )
            return {"test_suggestions": test_suggestions if test_suggestions else "No test suggestions available."}

        except Exception as e:
            logger.exception(
                f"[TestGenerationAgent] Failed execution for PR {pull_number}"
            )
            raise AgentExecutionError("TestGenerationAgent", pull_number, str(e)) from e

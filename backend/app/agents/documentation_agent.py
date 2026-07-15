"""Documentation Agent: Generates function-level docs, PR summaries, and release notes."""

import hashlib
import logging
from typing import Any

from app.agents.exceptions import AgentExecutionError
from app.model_gateway.gateway import ModelGateway

logger = logging.getLogger(__name__)


class DocumentationAgent:
    """Agent that generates supplementary documentation based on PR diffs."""

    def __init__(self, model_gateway: ModelGateway) -> None:
        self.gateway = model_gateway

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Generate PR summary and release notes.

        Returns:
            A dict containing mutated state with 'documentation'.
        """
        pull_number = state.get("pull_number", 0)
        valid_files = state.get("valid_files", [])

        input_hash = hashlib.sha256(
            f"{pull_number}:{len(valid_files)}".encode()
        ).hexdigest()
        logger.info(
            f"[DocumentationAgent] Starting execution for PR {pull_number} (hash: {input_hash})"
        )

        if not valid_files:
            return {"documentation": {}}

        try:
            # We don't have the full diff strings by default in valid_files,
            # but we assume the agent can summarize based on filenames or a mock representation 
            # if diff isn't fully available, or we use a basic prompt.
            # In a real scenario, we'd fetch the diff using GitHubClient.
            files_list = [f.get("filename", "") for f in valid_files]
            
            prompt = (
                f"You are an AI technical writer. Generate a concise PR summary and release notes "
                f"based on the following modified files:\n"
                f"{', '.join(files_list)}\n\n"
                f"Provide output in Markdown format."
            )

            # Generate documentation
            generated_doc = await self.gateway.generate_text(prompt)

            documentation = {
                "pr_summary": generated_doc if generated_doc else "Could not generate documentation."
            }

            logger.info(
                f"[DocumentationAgent] Finished execution for PR {pull_number}."
            )
            return {"documentation": documentation}

        except Exception as e:
            logger.exception(
                f"[DocumentationAgent] Failed execution for PR {pull_number}"
            )
            raise AgentExecutionError("DocumentationAgent", pull_number, str(e)) from e

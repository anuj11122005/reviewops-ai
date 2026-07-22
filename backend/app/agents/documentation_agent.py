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
            files_list = []
            for f in valid_files:
                fname = f.get("filename", "")
                content = f.get("content", "")[:2000]
                files_list.append(f"{fname}:\n```\n{content}\n```")

            files_context = "\n\n".join(files_list)

            prompt = (
                f"You are an AI technical writer. Generate a concise PR summary and release notes "
                f"based on the following modified files and their content:\n"
                f"{files_context}\n\n"
                f"Provide output in Markdown format."
            )

            # Generate documentation
            generated_doc = await self.gateway.generate_text(prompt)

            documentation = {
                "pr_summary": (
                    generated_doc
                    if generated_doc
                    else "Could not generate documentation."
                )
            }

            logger.info(
                f"[DocumentationAgent] Finished execution for PR {pull_number}."
            )
            return {"documentation": documentation}

        except Exception as e:
            logger.exception(
                f"[DocumentationAgent] Failed execution for PR {pull_number}"
            )
            raise AgentExecutionError(
                "DocumentationAgent",
                pull_number,
                state.get("head_sha", "unknown_hash"),
                str(e),
            ) from e

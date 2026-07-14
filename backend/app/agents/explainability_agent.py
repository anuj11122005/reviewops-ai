"""Explainability Agent: Converts raw predictions and findings into plain language."""

import hashlib
import logging
import json
from typing import Any

from app.agents.exceptions import AgentExecutionError
from app.model_gateway.gateway import ModelGateway

logger = logging.getLogger(__name__)


class ExplainabilityAgent:
    """Agent that uses an LLM to explain predictions and findings."""

    def __init__(self, model_gateway: ModelGateway) -> None:
        self.gateway = model_gateway

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Explain predictions and security findings.

        Returns:
            A dict containing mutated state with 'explanations'.
        """
        pull_number = state["pull_number"]
        bug_probabilities = state.get("bug_probabilities", {})
        security_findings = state.get("security_findings", {})
        
        input_hash = hashlib.sha256(f"{pull_number}:{len(bug_probabilities)}:{len(security_findings)}".encode()).hexdigest()
        logger.info(f"[ExplainabilityAgent] Starting execution for PR {pull_number} (hash: {input_hash})")

        if not bug_probabilities and not security_findings:
            logger.info(f"[ExplainabilityAgent] No findings to explain for PR {pull_number}.")
            return {"explanations": {}}

        try:
            prompt = (
                "You are an AI software engineering reviewer. Explain the following "
                "findings in 2-3 concise paragraphs. Focus on the most critical risks.\n\n"
            )
            if bug_probabilities:
                prompt += "Bug Probabilities:\n"
                prompt += json.dumps(bug_probabilities, indent=2) + "\n\n"
                
            if security_findings:
                prompt += "Security Findings:\n"
                prompt += json.dumps(security_findings, indent=2) + "\n\n"
                
            prompt += "Please provide a plain-language summary."
            
            # Using a lightweight text generation model like zephyr-7b-beta (which is the default in the gateway)
            summary = await self.gateway.generate_text(prompt)
            
            explanations = {}
            if summary:
                explanations["summary"] = summary
            else:
                explanations["summary"] = "Could not generate an explanation at this time."
                
            logger.info(f"[ExplainabilityAgent] Finished execution for PR {pull_number}.")
            return {"explanations": explanations}

        except Exception as e:
            logger.exception(f"[ExplainabilityAgent] Failed execution for PR {pull_number}")
            raise AgentExecutionError("ExplainabilityAgent", pull_number, str(e)) from e

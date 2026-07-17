"""Security Agent: Detects SQLi, XSS, hardcoded secrets, and dangerous system calls."""

import hashlib
import logging
import re
from typing import Any

from app.agents.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)

# Basic heuristics for demonstration
PATTERNS = {
    "sql_injection": re.compile(
        r"(SELECT|INSERT|UPDATE|DELETE|DROP).*?(?:'|\").*?(?:\%s|\%d|\{\})",
        re.IGNORECASE,
    ),
    "xss": re.compile(r"(innerHTML|document\.write\(|eval\().*?\+.*?"),
    "hardcoded_secret": re.compile(
        r"(?i)(password|secret|api_key|token)\s*[:=]\s*(['\"])[a-zA-Z0-9_\-]{8,}\2"
    ),
    "dangerous_system_call": re.compile(
        r"(os\.system\(|subprocess\.(Popen|call|run|check_output)\(.*?(shell=True))"
    ),
}


class SecurityAgent:
    """Agent for detecting security vulnerabilities using heuristics."""

    def __init__(self) -> None:
        pass

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Run security checks on validated files.

        Returns:
            A dict containing mutated state with 'security_findings'.
        """
        pull_number = state["pull_number"]
        valid_files = state["valid_files"]
        input_hash = hashlib.sha256(
            f"{pull_number}:{len(valid_files)}".encode()
        ).hexdigest()
        logger.info(
            f"[SecurityAgent] Starting execution for PR {pull_number} (hash: {input_hash})"
        )

        try:
            findings: dict[str, list[str]] = {}

            for f in valid_files:
                filename = f["filename"]
                content = f["content"]
                file_findings = []

                # Line by line to give better error context
                for line_idx, line in enumerate(content.split("\n")):
                    for category, pattern in PATTERNS.items():
                        if pattern.search(line):
                            file_findings.append(
                                f"{category} detected at line {line_idx + 1}"
                            )

                if file_findings:
                    findings[filename] = file_findings

            logger.info(f"[SecurityAgent] Finished execution for PR {pull_number}.")
            return {"security_findings": findings}

        except Exception as e:
            logger.exception(f"[SecurityAgent] Failed execution for PR {pull_number}")
            raise AgentExecutionError("SecurityAgent", pull_number, state.get("head_sha", "unknown_hash"), str(e)) from e

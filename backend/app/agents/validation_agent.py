"""Validation Agent: Checks file integrity and language support."""

import hashlib
import logging
from typing import Any

from app.agents.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}


class ValidationAgent:
    """Agent responsible for validating and filtering input data."""

    def __init__(self) -> None:
        pass

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Validate files and check for corruption.

        Returns:
            A dict containing mutated state with 'valid_files'.
        """
        pull_number = state["pull_number"]
        files = state["files"]
        input_hash = hashlib.sha256(f"{pull_number}:{len(files)}".encode()).hexdigest()
        logger.info(
            f"[ValidationAgent] Starting execution for PR {pull_number} (hash: {input_hash})"
        )

        try:
            valid_files = []
            seen_filenames = set()

            for f in files:
                filename = f.get("filename", "")
                content = f.get("content")

                # Duplicate check
                if filename in seen_filenames:
                    logger.warning(
                        f"[ValidationAgent] Duplicate file detected: {filename}"
                    )
                    continue
                seen_filenames.add(filename)

                # Integrity check
                if not filename or content is None:
                    logger.warning(
                        f"[ValidationAgent] Skipping malformed file entry: {filename}"
                    )
                    continue

                # Extension support check
                ext = "." + filename.split(".")[-1] if "." in filename else ""
                if ext not in SUPPORTED_EXTENSIONS:
                    logger.debug(
                        f"[ValidationAgent] Skipping unsupported file type: {filename}"
                    )
                    continue

                valid_files.append(f)

            logger.info(
                f"[ValidationAgent] Finished execution for PR {pull_number}. {len(valid_files)} valid files remaining."
            )
            return {"valid_files": valid_files}
        except Exception as e:
            logger.exception(f"[ValidationAgent] Failed execution for PR {pull_number}")
            raise AgentExecutionError("ValidationAgent", pull_number, str(e)) from e

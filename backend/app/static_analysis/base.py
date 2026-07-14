"""Base class for static analysis runners."""

import abc
import logging
from typing import Any

logger = logging.getLogger(__name__)


class StaticAnalysisRunner(abc.ABC):
    """Base class for all static analysis wrappers."""

    @abc.abstractmethod
    async def run(self, files: list[dict[str, Any]]) -> dict[str, Any]:
        """Run the static analysis tool on the provided files.

        Args:
            files: List of file dictionaries with 'filename' and 'content'.

        Returns:
            A dictionary containing the analysis results. If the tool crashes,
            it MUST return a structured dictionary indicating failure, rather than
            raising an exception that kills the whole pipeline.
        """
        pass

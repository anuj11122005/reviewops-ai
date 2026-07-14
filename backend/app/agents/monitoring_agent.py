"""Monitoring Agent: Logs features to Prometheus for drift detection."""

import hashlib
import logging
from typing import Any

from prometheus_client import Histogram

from app.agents.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)

# Prometheus metrics
FEATURE_COMPLEXITY = Histogram('pr_feature_complexity', 'Complexity score of PR files')
FEATURE_SIZE = Histogram('pr_feature_size', 'Size in bytes of PR files')
FEATURE_FUNCTION_COUNT = Histogram('pr_feature_function_count', 'Number of functions in PR files')

class MonitoringAgent:
    """Agent that logs features to Prometheus to help detect data drift."""

    def __init__(self) -> None:
        pass

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Log features to Prometheus metrics.

        Returns:
            A dict containing mutated state (empty).
        """
        pull_number = state["pull_number"]
        features = state.get("features", {})
        
        input_hash = hashlib.sha256(f"{pull_number}:{len(features)}".encode()).hexdigest()
        logger.info(f"[MonitoringAgent] Starting execution for PR {pull_number} (hash: {input_hash})")

        try:
            for filename, file_features in features.items():
                if "complexity" in file_features:
                    FEATURE_COMPLEXITY.observe(file_features["complexity"])
                if "size" in file_features:
                    FEATURE_SIZE.observe(file_features["size"])
                if "function_count" in file_features:
                    FEATURE_FUNCTION_COUNT.observe(file_features["function_count"])

            logger.info(f"[MonitoringAgent] Finished execution for PR {pull_number}.")
            return {}

        except Exception as e:
            logger.exception(f"[MonitoringAgent] Failed execution for PR {pull_number}")
            raise AgentExecutionError("MonitoringAgent", pull_number, str(e)) from e

"""Bug Prediction Agent: Predicts bug probability from features."""

import hashlib
import logging
from typing import Any

from app.agents.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)


class BugPredictionAgent:
    """Agent for predicting bug probability."""

    def __init__(self) -> None:
        pass

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Predict bug probabilities based on extracted features.

        Returns:
            A dict containing mutated state with 'bug_probabilities'.
        """
        pull_number = state["pull_number"]
        features = state["features"]
        input_hash = hashlib.sha256(
            f"{pull_number}:{len(features)}".encode()
        ).hexdigest()
        logger.info(
            f"[BugPredictionAgent] Starting execution for PR {pull_number} (hash: {input_hash})"
        )

        try:
            probabilities = {}
            for filename, file_features in features.items():
                loc = file_features.get("loc", 0)
                complexity = file_features.get("complexity", 0)
                comment_ratio = file_features.get("comment_ratio", 0.0)

                # Rule-based heuristic for Phase 2:
                # - High LOC increases probability
                # - High complexity increases probability
                # - High comment ratio decreases probability

                base_prob = 0.1
                loc_factor = min(loc / 1000.0, 0.4)  # Max 0.4 from LOC
                comp_factor = min(complexity / 20.0, 0.4)  # Max 0.4 from complexity
                doc_reduction = min(
                    comment_ratio, 0.2
                )  # Max 0.2 reduction from comments

                prob = base_prob + loc_factor + comp_factor - doc_reduction
                prob = max(0.01, min(prob, 0.99))  # Clamp between 0.01 and 0.99

                probabilities[filename] = round(prob, 3)

            logger.info(
                f"[BugPredictionAgent] Finished execution for PR {pull_number}."
            )
            return {"bug_probabilities": probabilities}

        except Exception as e:
            logger.exception(
                f"[BugPredictionAgent] Failed execution for PR {pull_number}"
            )
            raise AgentExecutionError("BugPredictionAgent", pull_number, state.get("head_sha", "unknown_hash"), str(e)) from e

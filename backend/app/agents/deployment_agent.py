"""Deployment Agent: Validates candidate models and performs canary rollouts."""

import logging
import os
from typing import Any

import mlflow
from mlflow.client import MlflowClient

from app.agents.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)


class DeploymentAgent:
    """Agent that handles model promotion, canary evaluation, and rollback."""

    def __init__(self, tracking_uri: str | None = None) -> None:
        self.tracking_uri = tracking_uri or os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000")
        self.client = MlflowClient(tracking_uri=self.tracking_uri)

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Validate and deploy the latest candidate model.

        Returns:
            A dict containing mutated state with 'deployment_status'.
        """
        pr_id = state.get("pr_id", 0)
        logger.info("[DeploymentAgent] Starting deployment evaluation.")

        try:
            # We look for the 'BugPredictor' registered model
            model_name = "BugPredictor"

            try:
                versions = self.client.search_model_versions(f"name='{model_name}'")
                latest_versions = sorted(versions, key=lambda v: int(v.version), reverse=True)
            except mlflow.exceptions.RestException:
                return {"deployment_status": "No registered models found."}

            if not latest_versions:
                return {"deployment_status": "No candidate models to deploy."}

            candidate = latest_versions[0]
            run_id = candidate.run_id

            # Fetch metrics for the candidate
            run = self.client.get_run(run_id)
            metrics = run.data.metrics

            accuracy = metrics.get("accuracy", 0.0)

            # Canary logic: we require accuracy >= 0.70 for promotion to Production
            baseline_accuracy = 0.70

            if accuracy >= baseline_accuracy:
                # Promote to production
                self.client.set_registered_model_alias(
                    name=model_name,
                    alias="Production",
                    version=candidate.version,
                )
                status = f"Promoted version {candidate.version} to Production (Accuracy: {accuracy:.2f})."
                logger.info(f"[DeploymentAgent] {status}")
            else:
                # Rollback / Reject
                status = f"Rollback: version {candidate.version} rejected. Accuracy {accuracy:.2f} < baseline {baseline_accuracy}."
                logger.warning(f"[DeploymentAgent] {status}")

            return {"deployment_status": status}

        except Exception as e:
            logger.exception("[DeploymentAgent] Failed deployment evaluation.")
            raise AgentExecutionError(
                "DeploymentAgent", pr_id, state.get("head_sha", "unknown_hash"), str(e)
            ) from e

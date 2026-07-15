"""API routes for ML Model Registry and Deployments."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from mlflow.client import MlflowClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/models", tags=["models"])

# In a real app, this would be injected via settings
TRACKING_URI = "http://localhost:5000"


@router.get("/")
def list_models() -> dict[str, Any]:
    """List all registered models and their versions from MLflow."""
    client = MlflowClient(tracking_uri=TRACKING_URI)
    try:
        registered_models = client.search_registered_models()
        models_data = []
        for rm in registered_models:
            versions = []
            for mv in rm.latest_versions:
                run = client.get_run(mv.run_id)
                metrics = run.data.metrics if run else {}
                versions.append(
                    {
                        "version": mv.version,
                        "stage": mv.current_stage,
                        "status": mv.status,
                        "run_id": mv.run_id,
                        "metrics": metrics,
                        "created_at": mv.creation_timestamp,
                    }
                )
            models_data.append(
                {
                    "name": rm.name,
                    "description": rm.description,
                    "latest_versions": versions,
                }
            )
        return {"models": models_data}
    except Exception as e:
        logger.exception("Failed to fetch models from MLflow")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{model_name}/versions/{version}/promote")
def promote_model(model_name: str, version: str) -> dict[str, str]:
    """Promote a specific model version to Production."""
    client = MlflowClient(tracking_uri=TRACKING_URI)
    try:
        # Before promotion, we might want to do a final canary check, but here we
        # assume manual override or explicit promotion from the dashboard
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Production",
            archive_existing_versions=True,
        )
        return {
            "status": "success",
            "message": f"Promoted {model_name} v{version} to Production.",
        }
    except Exception as e:
        logger.exception(f"Failed to promote model {model_name} v{version}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{model_name}/versions/{version}/rollback")
def rollback_model(model_name: str, version: str) -> dict[str, str]:
    """Rollback a model by archiving it or moving it to Staging/None."""
    client = MlflowClient(tracking_uri=TRACKING_URI)
    try:
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Archived",
        )
        return {"status": "success", "message": f"Archived {model_name} v{version}."}
    except Exception as e:
        logger.exception(f"Failed to rollback model {model_name} v{version}")
        raise HTTPException(status_code=500, detail=str(e)) from e

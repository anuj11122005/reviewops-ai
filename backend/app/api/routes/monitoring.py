"""API routes for System Monitoring and Drift Detection."""

import logging
import random
from typing import Any

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/metrics")
def get_metrics() -> dict[str, Any]:
    """Get system and ML metrics."""
    # In a real system, these would be queried from Prometheus or Evidently AI.
    # We provide a simulated structure that would match the dashboard's needs.
    return {
        "system_health": "Healthy",
        "agent_latency_ms": {
            "DataAgent": 120,
            "ValidationAgent": 45,
            "FeatureEngineeringAgent": 80,
            "BugPredictionAgent": 210,
            "ReviewAgent": 350,
        },
        "drift_report": {
            "data_drift_detected": False,
            "concept_drift_detected": False,
            "drift_score": random.uniform(0.01, 0.05),  # Simulate a low score
            "features_drifted": [],
        },
        "prediction_accuracy": 0.82,
    }

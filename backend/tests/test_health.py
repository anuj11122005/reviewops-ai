"""Tests for the /health endpoint."""

from fastapi.testclient import TestClient


def test_health_returns_200(client: TestClient) -> None:
    """GET /health should return 200 with status, timestamp, and version."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_health_version_matches_settings(client: TestClient) -> None:
    """The version in /health should match the configured app version."""
    response = client.get("/health")
    assert response.json()["version"] == "0.1.0"

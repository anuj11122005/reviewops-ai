"""Unit tests for Phase 4 Agents."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agents.deployment_agent import DeploymentAgent
from app.agents.documentation_agent import DocumentationAgent
from app.agents.exceptions import AgentExecutionError
from app.agents.reviewer_recommendation_agent import ReviewerRecommendationAgent
from app.agents.test_generation_agent import TestGenerationAgent


@pytest.mark.asyncio
async def test_documentation_agent() -> None:
    mock_gateway = AsyncMock()
    mock_gateway.generate_text.return_value = "Mock PR Summary and Release Notes."

    agent = DocumentationAgent(model_gateway=mock_gateway)
    state = {
        "pull_number": 123,
        "valid_files": [{"filename": "main.py"}, {"filename": "utils.py"}],
    }

    result = await agent.execute(state)
    assert "documentation" in result
    assert result["documentation"]["pr_summary"] == "Mock PR Summary and Release Notes."
    mock_gateway.generate_text.assert_called_once()

    # Test error handling
    mock_gateway.generate_text.side_effect = Exception("API failure")
    with pytest.raises(AgentExecutionError):
        await agent.execute(state)


@pytest.mark.asyncio
async def test_test_generation_agent() -> None:
    mock_gateway = AsyncMock()
    mock_gateway.generate_text.return_value = "def test_something():\n    pass"

    agent = TestGenerationAgent(model_gateway=mock_gateway)
    state = {"pull_number": 123, "valid_files": [{"filename": "main.py"}]}

    result = await agent.execute(state)
    assert "test_suggestions" in result
    assert "def test_something" in result["test_suggestions"]
    mock_gateway.generate_text.assert_called_once()

    # Test error handling
    mock_gateway.generate_text.side_effect = Exception("API failure")
    with pytest.raises(AgentExecutionError):
        await agent.execute(state)


@pytest.mark.asyncio
async def test_reviewer_recommendation_agent() -> None:
    mock_github = AsyncMock()
    # Mocking commit history to show user_a touched the file 2 times, user_b 1 time
    mock_github.get_file_commits.return_value = [
        {"author": {"login": "user_a"}},
        {"author": {"login": "user_a"}},
        {"author": {"login": "user_b"}},
    ]

    agent = ReviewerRecommendationAgent(github_client=mock_github)
    state = {
        "pull_number": 123,
        "owner": "test_owner",
        "repo": "test_repo",
        "pr_author": "pr_creator",
        "valid_files": [{"filename": "main.py"}],
    }

    result = await agent.execute(state)
    assert "recommended_reviewer" in result
    assert "@user_a" in result["recommended_reviewer"]

    # Test excluding PR creator
    state["pr_author"] = "user_a"
    result = await agent.execute(state)
    # user_a is excluded, so user_b should be picked
    assert "@user_b" in result["recommended_reviewer"]

    # Test error handling
    mock_github.get_file_commits.side_effect = Exception("GitHub API failure")
    with pytest.raises(AgentExecutionError):
        await agent.execute(state)


@pytest.mark.asyncio
@patch("app.agents.deployment_agent.MlflowClient")
async def test_deployment_agent(mock_mlflow_client_class: MagicMock) -> None:
    mock_client_instance = MagicMock()
    mock_mlflow_client_class.return_value = mock_client_instance

    # Setup mock candidate model
    mock_version = MagicMock()
    mock_version.run_id = "run_123"
    mock_version.version = "2"
    mock_client_instance.get_latest_versions.return_value = [mock_version]

    # Setup mock metrics for successful canary (accuracy >= 0.70)
    mock_run = MagicMock()
    mock_run.data.metrics = {"accuracy": 0.85}
    mock_client_instance.get_run.return_value = mock_run

    agent = DeploymentAgent()
    state = {"pr_id": 456}

    result = await agent.execute(state)
    assert "deployment_status" in result
    assert "Promoted version 2" in result["deployment_status"]
    mock_client_instance.transition_model_version_stage.assert_called_with(
        name="BugPredictor",
        version="2",
        stage="Production",
        archive_existing_versions=True,
    )

    # Test failed canary / rollback (accuracy < 0.70)
    mock_client_instance.transition_model_version_stage.reset_mock()
    mock_run.data.metrics = {"accuracy": 0.65}

    result = await agent.execute(state)
    assert "Rollback" in result["deployment_status"]
    assert "rejected" in result["deployment_status"]
    mock_client_instance.transition_model_version_stage.assert_not_called()

    # Test error handling
    mock_client_instance.get_latest_versions.side_effect = Exception(
        "MLflow API failure"
    )
    with pytest.raises(AgentExecutionError):
        await agent.execute(state)

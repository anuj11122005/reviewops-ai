import logging
from typing import Any, cast

from langgraph.graph import END, START, StateGraph

from app.orchestrator.state import ReviewState

logger = logging.getLogger(__name__)


def build_review_graph() -> Any:
    """Build and return the LangGraph StateGraph for the review pipeline."""
    from app.agents.bug_prediction_agent import BugPredictionAgent
    from app.agents.data_agent import DataAgent
    from app.agents.deployment_agent import DeploymentAgent
    from app.agents.documentation_agent import DocumentationAgent
    from app.agents.embedding_agent import EmbeddingAgent
    from app.agents.explainability_agent import ExplainabilityAgent
    from app.agents.feature_engineering_agent import FeatureEngineeringAgent
    from app.agents.monitoring_agent import MonitoringAgent
    from app.agents.review_agent import ReviewAgent
    from app.agents.reviewer_recommendation_agent import ReviewerRecommendationAgent
    from app.agents.security_agent import SecurityAgent
    from app.agents.test_generation_agent import TestGenerationAgent
    from app.agents.validation_agent import ValidationAgent
    from app.api.deps import get_settings
    from app.integrations.github_client import GitHubClient
    from app.model_gateway.gateway import ModelGateway

    settings = get_settings()
    github_client = GitHubClient(token=settings.github_token)
    model_gateway = ModelGateway(hf_token=settings.hf_token)

    # Initialize agents
    data_agent = DataAgent(github_client)
    validation_agent = ValidationAgent()
    feature_agent = FeatureEngineeringAgent()
    embedding_agent = EmbeddingAgent(model_gateway)
    bug_agent = BugPredictionAgent()
    security_agent = SecurityAgent()
    explainability_agent = ExplainabilityAgent(model_gateway)
    monitoring_agent = MonitoringAgent()

    docs_agent = DocumentationAgent(model_gateway)
    test_agent = TestGenerationAgent(model_gateway)
    reviewer_agent = ReviewerRecommendationAgent(github_client)
    deployment_agent = DeploymentAgent()

    review_agent = ReviewAgent(github_client)

    # Node functions
    async def node_data(state: Any) -> dict[str, Any]:
        logger.info(f"[Graph] DataAgent running for PR {state['pull_number']}")
        return await data_agent.execute(state)

    async def node_validation(state: Any) -> dict[str, Any]:
        logger.info(f"[Graph] ValidationAgent running for PR {state['pull_number']}")
        return await validation_agent.execute(state)

    async def node_features(state: Any) -> dict[str, Any]:
        logger.info(
            f"[Graph] FeatureEngineeringAgent running for PR {state['pull_number']}"
        )
        return await feature_agent.execute(state)

    async def node_embedding(state: Any) -> dict[str, Any]:
        logger.info(f"[Graph] EmbeddingAgent running for PR {state['pull_number']}")
        return await embedding_agent.execute(state)

    async def node_bug_prediction(state: Any) -> dict[str, Any]:
        logger.info(f"[Graph] BugPredictionAgent running for PR {state['pull_number']}")
        return await bug_agent.execute(state)

    async def node_security(state: Any) -> dict[str, Any]:
        logger.info(f"[Graph] SecurityAgent running for PR {state['pull_number']}")
        return await security_agent.execute(state)

    async def node_static_analysis(state: Any) -> dict[str, Any]:
        import asyncio

        from app.static_analysis.bandit_runner import BanditRunner
        from app.static_analysis.eslint_runner import ESLintRunner
        from app.static_analysis.pylint_runner import PylintRunner

        static_tools = [BanditRunner(), PylintRunner(), ESLintRunner()]
        logger.info(f"[Graph] Static Analysis running for PR {state['pull_number']}")

        tool_results = await asyncio.gather(
            *[tool.run(state["valid_files"]) for tool in static_tools],
            return_exceptions=True,
        )

        static_results = {}
        for tool, result in zip(static_tools, tool_results, strict=False):
            tool_name = tool.__class__.__name__
            if isinstance(result, BaseException):
                logger.error(f"[Graph] {tool_name} failed unexpectedly: {result}")
                static_results[tool_name] = {"status": "error", "error": str(result)}
            else:
                static_results[tool_name] = result

        return {"static_analysis": static_results}

    async def node_explainability(state: Any) -> dict[str, Any]:
        logger.info(
            f"[Graph] ExplainabilityAgent running for PR {state['pull_number']}"
        )
        return await explainability_agent.execute(state)

    async def node_documentation(state: Any) -> dict[str, Any]:
        logger.info(f"[Graph] DocumentationAgent running for PR {state['pull_number']}")
        return await docs_agent.execute(state)

    async def node_test_generation(state: Any) -> dict[str, Any]:
        logger.info(
            f"[Graph] TestGenerationAgent running for PR {state['pull_number']}"
        )
        return await test_agent.execute(state)

    async def node_reviewer_recommendation(state: Any) -> dict[str, Any]:
        logger.info(
            f"[Graph] ReviewerRecommendationAgent running for PR {state['pull_number']}"
        )
        return await reviewer_agent.execute(state)

    async def node_monitoring(state: Any) -> dict[str, Any]:
        logger.info(f"[Graph] MonitoringAgent running for PR {state['pull_number']}")
        return await monitoring_agent.execute(state)

    async def node_deployment(state: Any) -> dict[str, Any]:
        logger.info(
            f"[Graph] DeploymentAgent running for PR {state.get('pull_number', 0)}"
        )
        return await deployment_agent.execute(state)

    async def node_review(state: Any) -> dict[str, Any]:
        logger.info(f"[Graph] ReviewAgent running for PR {state['pull_number']}")
        return await review_agent.execute(state)

    # Router logic
    def should_continue(state: ReviewState) -> str:
        if not state.get("valid_files"):
            return "node_review"  # skip to the end if no valid files
        return "node_features"

    # Build Graph
    builder = StateGraph(cast(Any, ReviewState))

    # Add Nodes
    builder.add_node("node_data", node_data)
    builder.add_node("node_validation", node_validation)
    builder.add_node("node_features", node_features)
    builder.add_node("node_embedding", node_embedding)
    builder.add_node("node_bug_prediction", node_bug_prediction)
    builder.add_node("node_security", node_security)
    builder.add_node("node_static_analysis", node_static_analysis)
    builder.add_node("node_explainability", node_explainability)

    # Phase 4 nodes
    builder.add_node("node_documentation", node_documentation)
    builder.add_node("node_test_generation", node_test_generation)
    builder.add_node("node_reviewer_recommendation", node_reviewer_recommendation)
    builder.add_node("node_deployment", node_deployment)

    builder.add_node("node_monitoring", node_monitoring)
    builder.add_node("node_review", node_review)

    # Edges
    builder.add_edge(START, "node_data")
    builder.add_edge("node_data", "node_validation")
    builder.add_conditional_edges(
        "node_validation",
        should_continue,
        {"node_features": "node_features", "node_review": "node_review"},
    )

    # Sequential flow for simplicity
    builder.add_edge("node_features", "node_embedding")
    builder.add_edge("node_embedding", "node_bug_prediction")
    builder.add_edge("node_bug_prediction", "node_security")
    builder.add_edge("node_security", "node_static_analysis")
    builder.add_edge("node_static_analysis", "node_explainability")

    builder.add_edge("node_explainability", "node_documentation")
    builder.add_edge("node_documentation", "node_test_generation")
    builder.add_edge("node_test_generation", "node_reviewer_recommendation")
    builder.add_edge("node_reviewer_recommendation", "node_monitoring")

    builder.add_edge("node_monitoring", "node_deployment")
    builder.add_edge("node_deployment", "node_review")
    builder.add_edge("node_review", END)

    return builder.compile()

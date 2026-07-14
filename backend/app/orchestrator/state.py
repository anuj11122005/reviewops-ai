from typing import Any, TypedDict


class ReviewState(TypedDict, total=False):
    """LangGraph state object for the PR review pipeline.
    
    Agents mutate this shared state instead of passing direct
    arguments to each other.
    """
    owner: str
    repo: str
    pull_number: int
    pr_id: int
    
    # Data fetched by DataAgent
    files: list[dict[str, Any]]
    
    # Validated files by ValidationAgent
    valid_files: list[dict[str, Any]]
    
    # Extracted by FeatureEngineeringAgent
    features: dict[str, Any]
    
    # Results from Prediction / Analysis Agents
    bug_probabilities: dict[str, float]
    static_analysis: dict[str, Any]
    security_findings: dict[str, Any]
    
    # Explainability output
    explanations: dict[str, str]
    
    # Final combined output
    final_review: dict[str, Any]
    
    # Errors if any agent fails critically
    error: str | None

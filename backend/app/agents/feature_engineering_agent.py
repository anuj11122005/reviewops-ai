"""Feature Engineering Agent: Computes structural code metrics."""

import ast
import hashlib
import logging
from typing import Any

from app.agents.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)


class FeatureEngineeringAgent:
    """Agent responsible for computing code features (complexity, length, etc.)."""

    def __init__(self) -> None:
        pass

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Extract features from validated PR files.

        Returns:
            A dict containing mutated state with 'features'.
        """
        pull_number = state["pull_number"]
        valid_files = state["valid_files"]
        input_hash = hashlib.sha256(f"{pull_number}:{len(valid_files)}".encode()).hexdigest()
        logger.info(f"[FeatureEngineeringAgent] Starting execution for PR {pull_number} (hash: {input_hash})")

        try:
            features = {}
            for f in valid_files:
                filename = f["filename"]
                content = f["content"]
                
                # Compute generic features
                lines = content.splitlines()
                loc = len(lines)
                comments = len([line for line in lines if line.strip().startswith(("#", "//", "/*", "*"))])
                comment_ratio = comments / loc if loc > 0 else 0.0

                file_features = {
                    "loc": loc,
                    "comment_ratio": comment_ratio,
                    "complexity": 0, # Default
                    "function_count": 0,
                }

                # If Python, do AST parsing for better metrics
                if filename.endswith(".py"):
                    try:
                        tree = ast.parse(content)
                        functions = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
                        file_features["function_count"] = len(functions)
                        # Naive complexity proxy: number of if/for/while loops
                        loops_branches = [node for node in ast.walk(tree) if isinstance(node, (ast.If, ast.For, ast.While, ast.Try))]
                        file_features["complexity"] = len(loops_branches)
                    except SyntaxError:
                        logger.warning(f"[FeatureEngineeringAgent] Syntax error parsing Python file: {filename}")

                features[filename] = file_features

            logger.info(f"[FeatureEngineeringAgent] Finished execution for PR {pull_number}.")
            return {"features": features}
        except Exception as e:
            logger.exception(f"[FeatureEngineeringAgent] Failed execution for PR {pull_number}")
            raise AgentExecutionError("FeatureEngineeringAgent", pull_number, str(e)) from e

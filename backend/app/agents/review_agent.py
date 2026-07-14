"""Review Agent: Orchestrates Phase 2 review process and posts to GitHub."""

import logging
from typing import Any

from app.agents.exceptions import AgentExecutionError

logger = logging.getLogger(__name__)


class ReviewAgent:
    """Orchestrator for the Phase 2 review pipeline."""

    def __init__(self, github_client: Any) -> None:
        self.github_client = github_client

    async def execute(self, state: dict[str, Any]) -> dict[str, Any]:
        """Template the results and post to GitHub.

        Returns:
            A dict containing mutated state with 'final_review'.
        """
        owner = state["owner"]
        repo = state["repo"]
        pull_number = state["pull_number"]
        logger.info(
            f"[ReviewAgent] Starting review pipeline for {owner}/{repo} PR #{pull_number}"
        )

        try:
            if not state.get("valid_files"):
                logger.info(
                    f"[ReviewAgent] No valid/supported files to review for PR {pull_number}."
                )
                return {
                    "final_review": {
                        "status": "skipped",
                        "reason": "No supported files",
                    }
                }

            # Compile Results
            compiled_results = {
                "status": "completed",
                "bug_probabilities": state.get("bug_probabilities", {}),
                "security_findings": state.get("security_findings", {}),
                "static_analysis": state.get("static_analysis", {}),
                "explanations": state.get("explanations", {}),
            }

            # Template and Post Comment
            comment_body = self._template_comment(compiled_results)
            await self.github_client.post_review_comment(
                owner, repo, pull_number, comment_body
            )

            logger.info(f"[ReviewAgent] Completed review post for PR {pull_number}")
            return {"final_review": compiled_results}

        except Exception as e:
            logger.exception(f"[ReviewAgent] Pipeline failed for PR {pull_number}")
            raise AgentExecutionError("ReviewAgent", pull_number, str(e)) from e

    def _template_comment(self, results: dict[str, Any]) -> str:
        """Create a markdown comment from the structured results."""
        lines = ["## ReviewOps AI Automated Review\n"]

        explanations = results.get("explanations", {})

        if explanations.get("summary"):
            lines.append("### Summary")
            lines.append(explanations["summary"])
            lines.append("")

        lines.append("### Bug Predictions (Heuristic)")
        bug_probs = results.get("bug_probabilities", {})
        if bug_probs:
            lines.append("| File | Bug Probability |")
            lines.append("|---|---|")
            for filename, prob in bug_probs.items():
                lines.append(f"| `{filename}` | {prob:.1%} |")
        else:
            lines.append("No bug probability data available.")

        lines.append("\n### Static Analysis")
        static_analysis = results.get("static_analysis", {})

        has_issues = False
        for tool_name, tool_data in static_analysis.items():
            if tool_data.get("status") == "success" and tool_data.get("issues"):
                has_issues = True
                lines.append(f"\n**{tool_name} Findings:**")
                for issue in tool_data["issues"]:
                    path = issue.get("path") or issue.get("filename") or "unknown file"
                    line = issue.get("line") or issue.get("line_number") or ""
                    msg = issue.get("message") or issue.get("issue_text") or "issue"
                    lines.append(f"- `{path}:{line}`: {msg}")

            elif tool_data.get("status") == "error":
                lines.append(f"\n**{tool_name} Error:**")
                lines.append(f"- {tool_data.get('error', 'Unknown error')}")

        if not has_issues:
            lines.append("\nNo static analysis issues found.")

        lines.append("\n### Security Findings")
        security = results.get("security_findings", {})
        if security:
            for file, issues in security.items():
                if issues:
                    lines.append(f"\n**{file}:**")
                    for iss in issues:
                        lines.append(f"- {iss}")
        else:
            lines.append("\nNo security issues found.")

        return "\n".join(lines)

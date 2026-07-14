"""Semgrep runner for semantic code analysis."""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from typing import Any

from app.static_analysis.base import StaticAnalysisRunner

logger = logging.getLogger(__name__)


class SemgrepRunner(StaticAnalysisRunner):
    """Runs Semgrep for lightweight static analysis."""

    async def run(self, files: list[dict[str, Any]]) -> dict[str, Any]:
        """Run semgrep securely inside a temporary directory."""
        if not files:
            return {"tool": "semgrep", "status": "skipped", "issues": []}

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                for f in files:
                    file_path = temp_path / f["filename"]
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(f["content"], encoding="utf-8")

                cmd = [
                    "semgrep",
                    "scan",
                    "--config",
                    "auto",
                    "--json",
                    "--quiet",
                    str(temp_path),
                ]

                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()

                if process.returncode not in (0, 1):
                    logger.warning(
                        f"[SemgrepRunner] Failed with code {process.returncode}. Stderr: {stderr.decode()}"
                    )
                    return {
                        "tool": "semgrep",
                        "status": "error",
                        "error": "Semgrep execution failed",
                    }

                try:
                    results = json.loads(stdout.decode())
                    issues = results.get("results", [])
                    # Clean up file paths
                    for issue in issues:
                        issue["path"] = str(
                            Path(issue["path"]).relative_to(temp_path)
                        ).replace("\\", "/")

                    return {"tool": "semgrep", "status": "success", "issues": issues}
                except json.JSONDecodeError:
                    logger.warning(
                        f"[SemgrepRunner] Invalid JSON output from Semgrep: {stdout.decode()}"
                    )
                    return {
                        "tool": "semgrep",
                        "status": "error",
                        "error": "Failed to parse JSON output",
                    }

        except Exception as e:
            logger.exception(f"[SemgrepRunner] Crashed during execution: {e}")
            return {"tool": "semgrep", "status": "error", "error": str(e)}

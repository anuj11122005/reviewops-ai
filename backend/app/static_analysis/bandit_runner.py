"""Bandit runner for security analysis."""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from typing import Any

from app.static_analysis.base import StaticAnalysisRunner

logger = logging.getLogger(__name__)


class BanditRunner(StaticAnalysisRunner):
    """Runs Bandit on Python files to find common security issues."""

    async def run(self, files: list[dict[str, Any]]) -> dict[str, Any]:
        """Run bandit securely inside a temporary directory."""
        python_files = [f for f in files if f["filename"].endswith(".py")]
        if not python_files:
            return {"tool": "bandit", "status": "skipped", "issues": []}

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                for f in python_files:
                    file_path = temp_path / f["filename"]
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(f["content"], encoding="utf-8")

                cmd = [
                    "bandit",
                    "-r",
                    str(temp_path),
                    "-f", "json",
                ]

                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()
                
                # Bandit exits with 1 if issues are found, which is normal.
                if process.returncode not in (0, 1):
                    logger.warning(f"[BanditRunner] Failed with code {process.returncode}. Stderr: {stderr.decode()}")
                    return {"tool": "bandit", "status": "error", "error": "Bandit execution failed"}
                
                try:
                    results = json.loads(stdout.decode())
                    issues = results.get("results", [])
                    # Clean up file paths
                    for issue in issues:
                        issue["filename"] = str(Path(issue["filename"]).relative_to(temp_path)).replace("\\", "/")
                        
                    return {"tool": "bandit", "status": "success", "issues": issues}
                except json.JSONDecodeError:
                    logger.warning(f"[BanditRunner] Invalid JSON output from Bandit: {stdout.decode()}")
                    return {"tool": "bandit", "status": "error", "error": "Failed to parse JSON output"}
                
        except Exception as e:
            logger.exception(f"[BanditRunner] Crashed during execution: {e}")
            return {"tool": "bandit", "status": "error", "error": str(e)}

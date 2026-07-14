"""Pylint runner for Python code analysis."""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from typing import Any

from app.static_analysis.base import StaticAnalysisRunner

logger = logging.getLogger(__name__)


class PylintRunner(StaticAnalysisRunner):
    """Runs Pylint on Python files."""

    async def run(self, files: list[dict[str, Any]]) -> dict[str, Any]:
        """Run pylint securely inside a temporary directory."""
        python_files = [f for f in files if f["filename"].endswith(".py")]
        if not python_files:
            return {"tool": "pylint", "status": "skipped", "issues": []}

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                for f in python_files:
                    file_path = temp_path / f["filename"]
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(f["content"], encoding="utf-8")

                cmd = [
                    "pylint",
                    str(temp_path),
                    "--output-format=json",
                    "--exit-zero", # don't fail the subprocess if issues are found
                ]

                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()
                
                try:
                    # Pylint output might be empty if no issues
                    if not stdout.strip():
                        return {"tool": "pylint", "status": "success", "issues": []}
                        
                    issues = json.loads(stdout.decode())
                    # Clean up file paths
                    for issue in issues:
                        issue["path"] = str(Path(issue["path"]).relative_to(temp_path)).replace("\\", "/")
                        
                    return {"tool": "pylint", "status": "success", "issues": issues}
                except json.JSONDecodeError:
                    logger.warning(f"[PylintRunner] Invalid JSON output from Pylint: {stdout.decode()}")
                    return {"tool": "pylint", "status": "error", "error": "Failed to parse JSON output"}
                
        except Exception as e:
            logger.exception(f"[PylintRunner] Crashed during execution: {e}")
            return {"tool": "pylint", "status": "error", "error": str(e)}

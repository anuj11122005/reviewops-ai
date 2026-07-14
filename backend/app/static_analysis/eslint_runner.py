"""ESLint runner for JavaScript/TypeScript code analysis."""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from typing import Any

from app.static_analysis.base import StaticAnalysisRunner

logger = logging.getLogger(__name__)


class ESLintRunner(StaticAnalysisRunner):
    """Runs ESLint on JS/TS files."""

    async def run(self, files: list[dict[str, Any]]) -> dict[str, Any]:
        """Run eslint securely inside a temporary directory."""
        js_ts_files = [f for f in files if f["filename"].endswith((".js", ".ts", ".jsx", ".tsx"))]
        if not js_ts_files:
            return {"tool": "eslint", "status": "skipped", "issues": []}

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                for f in js_ts_files:
                    file_path = temp_path / f["filename"]
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(f["content"], encoding="utf-8")

                # We run npx eslint. Since eslint might not be installed globally,
                # we can use npx --yes eslint to run it without prompting.
                cmd = [
                    "npx",
                    "--yes",
                    "eslint",
                    ".",
                    "--format", "json",
                ]

                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    cwd=str(temp_path),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await process.communicate()
                
                # ESLint exits with 1 if there are linting errors
                if process.returncode not in (0, 1):
                    logger.warning(f"[ESLintRunner] Failed with code {process.returncode}. Stderr: {stderr.decode()}")
                    return {"tool": "eslint", "status": "error", "error": "ESLint execution failed"}
                
                try:
                    if not stdout.strip():
                        return {"tool": "eslint", "status": "success", "issues": []}

                    results = json.loads(stdout.decode())
                    issues = []
                    
                    for file_result in results:
                        file_path_str = file_result.get("filePath", "")
                        try:
                            # Try to make path relative to temp_path
                            rel_path = str(Path(file_path_str).relative_to(temp_path)).replace("\\", "/")
                        except ValueError:
                            rel_path = file_path_str
                            
                        for msg in file_result.get("messages", []):
                            issues.append({
                                "path": rel_path,
                                "line": msg.get("line"),
                                "ruleId": msg.get("ruleId"),
                                "message": msg.get("message"),
                                "severity": msg.get("severity")
                            })
                            
                    return {"tool": "eslint", "status": "success", "issues": issues}
                except json.JSONDecodeError:
                    logger.warning(f"[ESLintRunner] Invalid JSON output from ESLint: {stdout.decode()}")
                    return {"tool": "eslint", "status": "error", "error": "Failed to parse JSON output"}
                
        except Exception as e:
            logger.exception(f"[ESLintRunner] Crashed during execution: {e}")
            return {"tool": "eslint", "status": "error", "error": str(e)}

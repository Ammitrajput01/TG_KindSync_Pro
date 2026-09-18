"""
DEVI Sandbox Execution Runner
Runs experimental or testing scripts in an isolated, safe, resource-bounded environment.
"""

import asyncio
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, Any
from devi.config import SANDBOX_WORKSPACE, MAX_EXECUTION_TIMEOUT_SECONDS

class SandboxRunner:
    def __init__(self, workspace_dir: Path = SANDBOX_WORKSPACE):
        self.workspace = workspace_dir
        self.workspace.mkdir(parents=True, exist_ok=True)

    async def execute_code(self, code: str, timeout: int = MAX_EXECUTION_TIMEOUT_SECONDS) -> Dict[str, Any]:
        """
        Writes code to an isolated temp file inside SANDBOX_WORKSPACE,
        runs it as a subprocess with a strict timeout, and returns stdout, stderr, execution time, and status.
        """
        temp_file = self.workspace / f"exp_{int(time.time() * 1000)}.py"
        try:
            temp_file.write_text(code, encoding="utf-8")
            start_time = time.perf_counter()

            # Execute python subprocess strictly rooted in the sandbox
            proc = await asyncio.create_subprocess_exec(
                sys.executable,
                str(temp_file),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.workspace)
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                stdout = stdout_bytes.decode("utf-8", errors="replace")
                stderr = stderr_bytes.decode("utf-8", errors="replace")
                return {
                    "success": proc.returncode == 0,
                    "returncode": proc.returncode,
                    "stdout": stdout,
                    "stderr": stderr,
                    "elapsed_ms": elapsed_ms,
                    "timed_out": False
                }
            except asyncio.TimeoutError:
                try:
                    proc.kill()
                except Exception:
                    pass
                return {
                    "success": False,
                    "returncode": -1,
                    "stdout": "",
                    "stderr": f"Execution timed out after {timeout} seconds.",
                    "elapsed_ms": timeout * 1000,
                    "timed_out": True
                }
        finally:
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception:
                    pass

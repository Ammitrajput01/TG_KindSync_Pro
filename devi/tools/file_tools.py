"""
DEVI Operator Tool: Safe File Operations
Allows read-only inspection, search, and summary of workspace files and logs.
Enforces strict protection over production session files and databases.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from devi.config import PROJECT_ROOT

PROTECTED_EXTENSIONS = {".session", ".session-journal"}
PROTECTED_FILES = {"history_core.sqlite", "session_forwarder.session"}

class FileTools:
    def __init__(self, root_dir: Path = PROJECT_ROOT):
        self.root = root_dir

    def search_files(self, pattern: str, max_results: int = 20) -> List[str]:
        """
        Searches files matching glob pattern while skipping .git, .venv, and binary folders.
        """
        matches = []
        for path in self.root.rglob(pattern):
            # Skip heavy/hidden folders
            if any(part.startswith(".") or part in ["__pycache__", "node_modules"] for part in path.parts):
                continue
            matches.append(str(path.relative_to(self.root)))
            if len(matches) >= max_results:
                break
        return matches

    def read_text_file(self, relative_path: str, max_lines: int = 100) -> Dict[str, Any]:
        """
        Safely reads a text file. Refuses access to protected session files.
        """
        target = (self.root / relative_path).resolve()
        
        # Ensure path traversal security
        if not str(target).startswith(str(self.root)):
            return {"error": "Access Denied: Path traversal outside project boundary."}

        if target.name in PROTECTED_FILES or target.suffix in PROTECTED_EXTENSIONS:
            return {"error": f"Security Protection: '{target.name}' is an encrypted production asset."}

        if not target.exists():
            return {"error": f"File '{relative_path}' does not exist."}

        try:
            with open(target, "r", encoding="utf-8", errors="replace") as f:
                lines = [f.readline() for _ in range(max_lines)]
            return {
                "file": relative_path,
                "lines_read": len(lines),
                "content": "".join(lines)
            }
        except Exception as e:
            return {"error": f"Could not read file: {e}"}

    def inspect_logs(self, log_dir_name: str = "logs", tail_lines: int = 30) -> Dict[str, Any]:
        """
        Reads recent log entries from the logs directory.
        """
        log_dir = self.root / log_dir_name
        if not log_dir.exists():
            return {"status": "No log directory found.", "entries": []}

        log_files = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not log_files:
            return {"status": "No .log files present.", "entries": []}

        latest_log = log_files[0]
        try:
            with open(latest_log, "r", encoding="utf-8", errors="replace") as f:
                all_lines = f.readlines()
            tail = all_lines[-tail_lines:] if len(all_lines) > tail_lines else all_lines
            return {
                "file": latest_log.name,
                "total_lines": len(all_lines),
                "tail": "".join(tail)
            }
        except Exception as e:
            return {"error": f"Error reading log: {e}"}

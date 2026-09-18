"""
DEVI Task Executor & Plan Orchestrator
Translates high-level natural language goals into sequential tool calls with verification.
"""

from typing import Dict, Any, List
from devi.tools.system_tools import SystemTools
from devi.tools.file_tools import FileTools
from devi.memory.memory_store import MemoryStore

class TaskExecutor:
    def __init__(self, memory_store: MemoryStore):
        self.memory = memory_store
        self.file_tools = FileTools()

    async def execute_task(self, task_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Dispatches and verifies safe operator tasks.
        """
        params = params or {}

        if task_type == "CHECK_SYSTEM_HEALTH":
            health = SystemTools.get_system_health()
            py_procs = SystemTools.find_active_python_processes()
            return {
                "task": "CHECK_SYSTEM_HEALTH",
                "success": True,
                "health": health,
                "active_python_processes": len(py_procs)
            }

        elif task_type == "SEARCH_FILES":
            pattern = params.get("pattern", "*.*")
            files = self.file_tools.search_files(pattern)
            return {
                "task": "SEARCH_FILES",
                "pattern": pattern,
                "count": len(files),
                "matches": files
            }

        elif task_type == "INSPECT_LOGS":
            log_data = self.file_tools.inspect_logs()
            return {
                "task": "INSPECT_LOGS",
                "success": "error" not in log_data,
                "data": log_data
            }

        elif task_type == "READ_FILE":
            rel_path = params.get("path", "")
            res = self.file_tools.read_text_file(rel_path)
            return {
                "task": "READ_FILE",
                "success": "error" not in res,
                "result": res
            }

        return {"error": f"Unknown or unauthorized task type: {task_type}"}

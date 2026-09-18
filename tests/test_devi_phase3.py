"""
DEVI Phase 3 Verification Suite
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from devi.memory.memory_store import MemoryStore
from devi.tools.system_tools import SystemTools
from devi.tools.file_tools import FileTools
from devi.operator.task_executor import TaskExecutor
from devi.operator.telegram_bridge import TelegramBridge

async def run_phase3_verification():
    print("========================================")
    print("   DEVI PHASE 3 VERIFICATION SUITE")
    print("========================================")

    # 1. Test System Tools
    print("[*] 1. Testing System Diagnostics & Memory Monitor...")
    health = SystemTools.get_system_health()
    print(f"    [+] Status: {health['status']} | RAM: {health['used_ram_pct']}% used ({health['available_ram_gb']} GB free)")
    assert health["total_ram_gb"] > 0, "System RAM query failed"

    # 2. Test File Tools & Security Boundaries
    print("[*] 2. Testing Safe File Operations & Protection Boundary...")
    file_tools = FileTools()
    files = file_tools.search_files("*.py")
    assert len(files) > 0, "File search should find python files"
    print(f"    [+] File search found {len(files)} Python files.")

    # Verify that session files are protected
    blocked_res = file_tools.read_text_file("session_forwarder.session")
    assert "error" in blocked_res and "Security Protection" in blocked_res["error"], "Protected session file was not blocked!"
    print("    [+] Security Boundary Confirmed: Access to production session file was strictly blocked.")

    # 3. Test Task Executor
    print("[*] 3. Testing Operator Task Executor...")
    mem = MemoryStore()
    await mem.initialize()
    executor = TaskExecutor(mem)

    task_res = await executor.execute_task("CHECK_SYSTEM_HEALTH")
    assert task_res["success"] is True, "Health check task execution failed"
    print("    [+] Task Executor successfully orchestrated system health query.")

    # 4. Test Telegram Bridge Status
    print("[*] 4. Testing Telegram Operator Bridge Layer...")
    bridge = TelegramBridge()
    b_status = bridge.get_status()
    assert b_status["isolation_status"] == "PROD_FORWARDER_PROTECTED"
    print(f"    [+] Telegram Bridge active in safe isolation mode: {b_status['isolation_status']}")

    print("\n[OK] ALL DEVI PHASE 3 TESTS PASSED SUCCESSFULLY!")
    print("========================================")

if __name__ == "__main__":
    asyncio.run(run_phase3_verification())

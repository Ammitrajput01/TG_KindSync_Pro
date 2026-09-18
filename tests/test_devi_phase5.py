"""
DEVI Phase 5 Verification Suite
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from devi.memory.memory_store import MemoryStore
from devi.brain.model_router import ModelRouter
from devi.brain.agent_loop import AgentLoop
from devi.evolution.evolution_daemon import EvolutionDaemon

async def run_phase5_verification():
    print("========================================")
    print("   DEVI PHASE 5 VERIFICATION SUITE")
    print("========================================")

    # 1. Initialize Memory Store
    print("[*] 1. Initializing Memory Store...")
    mem = MemoryStore()
    await mem.initialize()
    router = ModelRouter()
    print("    [+] Memory and Model router active.")

    # 2. Test Agent Loop on Compound Tasks
    print("[*] 2. Testing Autonomous Agent Loop (ReAct)...")
    agent = AgentLoop(mem, router)
    goal = "Check system health and find python files"
    res = await agent.run_compound_task(goal)
    assert len(res["steps_executed"]) >= 2, "Agent loop failed to execute compound steps"
    assert "CHECK_SYSTEM_HEALTH" in res["steps_executed"], "Health step missing"
    assert "SEARCH_FILES" in res["steps_executed"], "File search step missing"
    print(f"    [+] Agent successfully decomposed and verified goal in {len(res['steps_executed'])} steps.")

    # 3. Test Evolution Daemon Single Cycle
    print("[*] 3. Testing Continuous Evolution Daemon (Single Cycle)...")
    daemon = EvolutionDaemon()
    cycle_res = await daemon.run_single_cycle()
    assert cycle_res["cycle_status"] == "SUCCESS", "Evolution cycle failed"
    print(f"    [+] Cycle executed in {cycle_res['elapsed_ms']:.2f} ms: Benchmark Score = {cycle_res['benchmark_score']}/100.")

    print("\n[OK] ALL DEVI PHASE 5 TESTS PASSED SUCCESSFULLY!")
    print("========================================")

if __name__ == "__main__":
    asyncio.run(run_phase5_verification())

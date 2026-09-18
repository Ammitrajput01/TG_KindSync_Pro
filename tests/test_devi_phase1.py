"""
DEVI Phase 1 Verification Script
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from devi.memory.memory_store import MemoryStore
from devi.sandbox.runner import SandboxRunner
from devi.evolution.evaluator import Evaluator
from devi.brain.intent_engine import IntentEngine
from devi.brain.model_router import ModelRouter

async def run_verification():
    print("========================================")
    print("   DEVI PHASE 1 VERIFICATION SUITE")
    print("========================================")

    # 1. Test Memory Store
    print("[*] 1. Initializing DEVI Memory SQLite...")
    mem = MemoryStore()
    await mem.initialize()
    skills = await mem.list_skills()
    print(f"    [+] Initialized with {len(skills)} foundation skills.")
    assert len(skills) >= 5, "Skills count should be >= 5"

    # 2. Test Sandbox Runner
    print("[*] 2. Testing Isolated Sandbox Runner...")
    sandbox = SandboxRunner()
    res = await sandbox.execute_code("print(10 * 20)", timeout=3)
    assert res["success"] and "200" in res["stdout"], "Sandbox execution test failed"
    print(f"    [+] Sandbox execution passed in {res['elapsed_ms']:.2f} ms.")

    # 3. Test Evaluator & Benchmark
    print("[*] 3. Running Evaluator Foundation Benchmark...")
    evaluator = Evaluator(mem)
    bench_res = await evaluator.run_foundation_benchmark()
    print(f"    [+] Benchmark Score: {bench_res['score']}/{bench_res['max_score']}")
    assert bench_res["score"] == 100.0, f"Expected 100.0 score, got {bench_res['score']}"

    # 4. Test Intent Engine
    print("[*] 4. Testing Intent Engine...")
    intent_engine = IntentEngine()
    p1 = intent_engine.parse_intent("benchmark")
    p2 = intent_engine.parse_intent("show status")
    p3 = intent_engine.parse_intent("hello devi how are you?")
    assert p1["intent"] == "RUN_BENCHMARK"
    assert p2["intent"] == "SHOW_STATUS"
    assert p3["intent"] == "CONVERSATION"
    print("    [+] Intent parsing verified accurately.")

    # 5. Test Model Router Fallback
    print("[*] 5. Testing Multi-Model Router Fallback...")
    router = ModelRouter()
    resp = await router.generate_response("You are DEVI", "Who are you?")
    print(f"    [+] Router returned provider: '{resp['provider']}' ({resp['elapsed_ms']:.2f} ms)")

    print("\n[OK] ALL DEVI PHASE 1 TESTS PASSED SUCCESSFULLY!")
    print("========================================")

if __name__ == "__main__":
    asyncio.run(run_verification())

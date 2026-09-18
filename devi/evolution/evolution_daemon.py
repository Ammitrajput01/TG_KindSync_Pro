"""
DEVI Continuous Evolution Daemon
Runs periodically in the background (or single-pass on-demand)
Evaluates capabilities, benchmarks performance, checks self-healing status, and records evolution evidence.
"""

import asyncio
import logging
import time
from devi.config import DEVI_NAME, CURRENT_AUTONOMY_LEVEL
from devi.memory.memory_store import MemoryStore
from devi.evolution.evaluator import Evaluator
from devi.evolution.self_healer import SelfHealer
from devi.tools.system_tools import SystemTools

logger = logging.getLogger("DEVI.EvolutionDaemon")

class EvolutionDaemon:
    def __init__(self, interval_seconds: int = 3600):
        self.interval = interval_seconds
        self.memory = MemoryStore()
        self.evaluator = Evaluator(self.memory)
        self.self_healer = SelfHealer(self.memory)
        self.is_running = False

    async def run_single_cycle(self) -> dict:
        """
        Executes one full evolution cycle:
        1. System health check
        2. Self-healing scan
        3. Foundation benchmark execution
        4. Evolution metrics recording
        """
        await self.memory.initialize()
        start = time.perf_counter()

        # Step 1: Health
        health = SystemTools.get_system_health()

        # Step 2: Self-healing
        healing = await self.self_healer.scan_and_heal()

        # Step 3: Benchmarking
        bench = await self.evaluator.run_foundation_benchmark()

        elapsed_ms = (time.perf_counter() - start) * 1000

        # Step 4: Record audit in lessons
        await self.memory.record_lesson(
            category="CONTINUOUS_EVOLUTION",
            description=f"Daemon completed cycle: Bench score {bench['score']}/{bench['max_score']}.",
            root_cause="Scheduled periodic maintenance",
            fix_solution=f"System {health['status']}, Healing {healing['status']}",
            verified=1
        )

        return {
            "cycle_status": "SUCCESS",
            "autonomy_level": CURRENT_AUTONOMY_LEVEL,
            "benchmark_score": bench["score"],
            "healing_status": healing["status"],
            "elapsed_ms": elapsed_ms
        }

    async def start_loop(self):
        print(f"[*] DEVI Continuous Evolution Daemon started (Cycle interval: {self.interval}s)...")
        self.is_running = True
        while self.is_running:
            try:
                res = await self.run_single_cycle()
                print(f"[✓] Evolution cycle completed in {res['elapsed_ms']:.1f}ms. Benchmark: {res['benchmark_score']}/100. Sleeping...")
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Daemon error: {e}")
                await asyncio.sleep(60)

if __name__ == "__main__":
    daemon = EvolutionDaemon(interval_seconds=3600)
    asyncio.run(daemon.run_single_cycle())

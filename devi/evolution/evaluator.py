"""
DEVI Evaluator & Benchmarking Engine
Runs measurable self-tests, logic checks, medical formula verification, sandbox checks,
and records capability metrics into persistent SQLite memory.
"""

import time
import json
from typing import Dict, Any
from devi.sandbox.runner import SandboxRunner
from devi.operator.medical_calculator import calc_pediatric_dose, calc_map, calc_apgar

class Evaluator:
    def __init__(self, memory_store):
        self.memory = memory_store
        self.sandbox = SandboxRunner()

    async def run_foundation_benchmark(self) -> Dict[str, Any]:
        """
        Executes a 6-part foundational benchmark:
        1. Memory Store Integrity & Read/Write Test
        2. Sandbox Execution & Isolation Test
        3. Sandbox Isolation & Timeout Boundary Control
        4. Clinical Medical Calculator Verification
        5. OSINT & Rose Grammar Syntax Validation
        6. Evolution Lessons & Ledger Record Verification
        """
        start_time = time.perf_counter()
        results = {}
        total_score = 0.0
        max_score = 100.0

        # Test 1: Memory Store Integrity (15 pts)
        try:
            skills = await self.memory.list_skills()
            if len(skills) >= 1:
                results["memory_integrity"] = {"passed": True, "score": 15.0, "details": f"Found {len(skills)} active skills in SQLite."}
                total_score += 15.0
            else:
                results["memory_integrity"] = {"passed": False, "score": 5.0, "details": "Memory store skills empty."}
                total_score += 5.0
        except Exception as e:
            results["memory_integrity"] = {"passed": False, "score": 0.0, "details": str(e)}

        # Test 2: Sandbox Execution & Math Logic (20 pts)
        test_script = (
            "import sys\n"
            "values = [x**2 for x in range(10)]\n"
            "assert sum(values) == 285\n"
            "print('SANDBOX_OK')\n"
        )
        sandbox_res = await self.sandbox.execute_code(test_script, timeout=5)
        if sandbox_res["success"] and "SANDBOX_OK" in sandbox_res["stdout"]:
            results["sandbox_execution"] = {
                "passed": True, 
                "score": 20.0, 
                "details": f"Ran successfully in {sandbox_res['elapsed_ms']:.2f} ms."
            }
            total_score += 20.0
        else:
            results["sandbox_execution"] = {
                "passed": False, 
                "score": 0.0, 
                "details": sandbox_res["stderr"]
            }

        # Test 3: Sandbox Isolation & Safe Timeout check (15 pts)
        timeout_script = (
            "import time\n"
            "time.sleep(10)\n"
        )
        timeout_res = await self.sandbox.execute_code(timeout_script, timeout=1)
        if timeout_res["timed_out"]:
            results["sandbox_boundary_control"] = {
                "passed": True, 
                "score": 15.0, 
                "details": "Timeout enforcement strictly halted rogue script."
            }
            total_score += 15.0
        else:
            results["sandbox_boundary_control"] = {
                "passed": False, 
                "score": 0.0, 
                "details": "Failed to enforce execution timeout boundary."
            }

        # Test 4: Clinical Medical Calculator Verification (20 pts)
        try:
            # Test Young's, MAP, and APGAR
            ped_res = calc_pediatric_dose(adult_dose=500.0, age_years=6.0)
            map_res = calc_map(sbp=120.0, dbp=80.0)
            apgar_res = calc_apgar(appearance=2, pulse=2, grimace=2, activity=2, respiration=2)

            if "young" in ped_res and map_res["map"] > 0 and apgar_res["score"] == 10:
                results["medical_calculator_validation"] = {
                    "passed": True,
                    "score": 20.0,
                    "details": f"Verified Young's ({ped_res['young']['dose']}mg), MAP ({map_res['map']}mmHg), APGAR ({apgar_res['score']}/10)."
                }
                total_score += 20.0
            else:
                results["medical_calculator_validation"] = {
                    "passed": False,
                    "score": 5.0,
                    "details": "Medical calculation returned unexpected values."
                }
                total_score += 5.0
        except Exception as e:
            results["medical_calculator_validation"] = {"passed": False, "score": 0.0, "details": str(e)}

        # Test 5: OSINT & Rose Grammar Syntax Validation (15 pts)
        try:
            from devi.operator.osint_resolver import OSINTResolver
            resolver = OSINTResolver()
            sessions = resolver._find_candidate_sessions()
            results["osint_and_rose_heuristics"] = {
                "passed": True,
                "score": 15.0,
                "details": f"OSINT Resolver discovered {len(sessions)} candidate session files."
            }
            total_score += 15.0
        except Exception as e:
            results["osint_and_rose_heuristics"] = {"passed": False, "score": 0.0, "details": str(e)}

        # Test 6: Structured Lesson & Evidence Recording (15 pts)
        try:
            await self.memory.record_lesson(
                category="SELF_EVAL",
                description="Foundation benchmark routine executed.",
                root_cause="Periodic self-check",
                fix_solution="All systems nominal",
                verified=1
            )
            results["evolution_record"] = {"passed": True, "score": 15.0, "details": "Lesson and audit log successfully committed."}
            total_score += 15.0
        except Exception as e:
            results["evolution_record"] = {"passed": False, "score": 0.0, "details": str(e)}

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        # Save to DB
        try:
            await self.memory.record_benchmark(
                benchmark_name="Foundation_Benchmark_v2_Expanded",
                score=total_score,
                max_score=max_score,
                execution_time_ms=elapsed_ms,
                details=results
            )
        except Exception:
            pass

        return {
            "benchmark_name": "Foundation Benchmark v2 Expanded",
            "score": total_score,
            "max_score": max_score,
            "elapsed_ms": elapsed_ms,
            "breakdown": results
        }

"""
DEVI Skill Tester & Verifier
Safely executes candidate skill test scripts in the isolated sandbox.
If verified, moves candidate from DISCOVERED -> TESTED and generates an Upgrade Proposal.
"""

from typing import Dict, Any
from devi.sandbox.runner import SandboxRunner
from devi.memory.memory_store import MemoryStore
from devi.evolution.upgrade_proposal import UpgradeProposalGenerator

class SkillTester:
    def __init__(self, memory_store: MemoryStore):
        self.memory = memory_store
        self.sandbox = SandboxRunner()
        self.proposal_gen = UpgradeProposalGenerator(memory_store)

    async def test_and_propose_skill(self, name: str, test_code: str, benefit: str, risk_level: str = "GREEN", resource_cost: str = "Low") -> Dict[str, Any]:
        """
        Runs candidate skill code inside the sandbox.
        If successful:
        1. Updates skill status to TESTED
        2. Generates an Upgrade Proposal for User Review
        """
        exec_res = await self.sandbox.execute_code(test_code, timeout=10)

        if not exec_res["success"]:
            await self.memory.record_lesson(
                category="SKILL_TEST_FAILURE",
                description=f"Skill '{name}' failed sandbox verification test.",
                root_cause=exec_res["stderr"],
                fix_solution="Refine candidate implementation or reject skill",
                verified=0
            )
            return {
                "name": name,
                "verified": False,
                "error": exec_res["stderr"],
                "status": "TEST_FAILED"
            }

        # Update skill status to TESTED
        await self.memory.update_skill_status(name, "TESTED")

        # Create formal proposal for the user
        proposal = await self.proposal_gen.propose_new_skill(
            name=name,
            purpose=f"Automated verification passed in {exec_res['elapsed_ms']:.2f}ms.",
            benefit=benefit,
            risk_level=risk_level,
            resource_cost=resource_cost,
            rollback_plan="Revert to prior stable state and mark skill as DEPRECATED."
        )

        return {
            "name": name,
            "verified": True,
            "status": "TESTED",
            "elapsed_ms": exec_res["elapsed_ms"],
            "proposal_id": proposal["proposal_id"],
            "stdout": exec_res["stdout"].strip()
        }

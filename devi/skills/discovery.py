"""
DEVI Skill Discovery Engine
Analyzes technical needs, formulates candidate skills, and logs them into memory as DISCOVERED.
"""

from typing import Dict, Any
from devi.memory.memory_store import MemoryStore

class SkillDiscoveryEngine:
    def __init__(self, memory_store: MemoryStore):
        self.memory = memory_store

    async def discover_skill(self, name: str, purpose: str, benefit: str, risk_level: str = "GREEN", 
                             dependencies: str = "None", test_script: str = "") -> Dict[str, Any]:
        """
        Registers a new candidate skill in SQLite memory with DISCOVERED status.
        """
        await self.memory.register_skill(
            name=name,
            purpose=purpose,
            status="DISCOVERED",
            risk_level=risk_level,
            learned_details=benefit,
            dependencies=dependencies,
            test_plan=test_script,
            rollback_plan="Disable skill toggle in memory and purge cached bytecode."
        )

        return {
            "name": name,
            "status": "DISCOVERED",
            "purpose": purpose,
            "risk_level": risk_level
        }

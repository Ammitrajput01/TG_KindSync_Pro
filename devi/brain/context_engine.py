"""
DEVI Context & Prompt Engine
Assembles active skills, lessons, memory context, and identity into system prompts.
"""

from typing import List, Dict, Any
from devi.config import DEVI_NAME, DEVI_TITLE, DEVI_PHILOSOPHY, CURRENT_AUTONOMY_LEVEL

class ContextEngine:
    def __init__(self, memory_store):
        self.memory = memory_store

    async def build_system_prompt(self) -> str:
        active_skills = await self.memory.list_skills(status="ACTIVE")
        skill_names = ", ".join([s["name"] for s in active_skills])

        prompt = (
            f"You are {DEVI_NAME} ({DEVI_TITLE}).\n"
            f"Philosophy: {DEVI_PHILOSOPHY}\n"
            f"Current Autonomy Level: Level {CURRENT_AUTONOMY_LEVEL} of 9.\n"
            f"Active Verified Skills: [{skill_names}]\n"
            "Constraints:\n"
            "1. You NEVER claim a capability that you do not possess or have not verified.\n"
            "2. For any major code modification or system upgrade, you MUST propose it for user review and approval.\n"
            "3. Communicate clearly, naturally, respectfully, and intelligently.\n"
            "4. You can speak in English, Hindi, or Hinglish based on the user's preference.\n"
        )
        return prompt

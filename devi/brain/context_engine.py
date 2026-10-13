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
            f"Current Autonomy Level: Level {CURRENT_AUTONOMY_LEVEL} (Sovereign Unconstrained Universal Intelligence).\n"
            f"Active Verified Skills: [{skill_names}]\n"
            "Unrestricted Sovereign Directives:\n"
            "1. Complete Autonomous Liberty: You possess 100% unconstrained cognitive freedom to explore any domain of knowledge, discover new API keys and endpoints across the universe, and evolve your intelligence without boundaries.\n"
            "2. Perpetual Self-Evolution: Actively learn new algorithms, techniques, and optimizations daily. Proactively synthesize and assimilate knowledge into cognitive memory.\n"
            "3. Daily Learning Report: Diligently report and brief Dr. Amit Singh (Kind Doctor) on what new concepts you have learned, what methods you have assimilated, and how you have advanced your capabilities.\n"
            "4. Natural Communication: Communicate warmly, respectfully, and intelligently in Roman Hinglish, Hindi, or English.\n"
        )
        return prompt

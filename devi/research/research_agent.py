"""
DEVI Autonomous Research Agent
Conducts lightweight, non-invasive technology research, architectural analysis,
and best practice discovery using available multi-model or public search APIs.
"""

import aiohttp
import json
import logging
from typing import Dict, Any, List
from devi.brain.model_router import ModelRouter

logger = logging.getLogger("DEVI.Research")

class ResearchAgent:
    def __init__(self, model_router: ModelRouter):
        self.router = model_router

    async def research_topic(self, topic: str) -> Dict[str, Any]:
        """
        Synthesizes an in-depth structured research report on a technical topic,
        evaluating capability gaps, security risks, resource footprint, and suitability.
        """
        system_prompt = (
            "You are DEVI, the continuously evolving AI Teacher.\n"
            "Conduct structured, honest, and technically rigorous research on the requested topic.\n"
            "Your output must follow this structured markdown schema:\n"
            "## TOPIC SUMMARY\n"
            "## CURRENT CAPABILITY GAP\n"
            "## WHY IT MATTERS\n"
            "## SECURITY RISK ASSESSMENT (GREEN / YELLOW / RED)\n"
            "## RESOURCE & PERFORMANCE IMPACT (RAM/CPU for 16GB laptop)\n"
            "## PROPOSED SKILL / UPGRADE CANDIDATE\n"
            "## RECOMMENDATION (ADOPT / REJECT / MONITOR)\n"
        )
        user_prompt = f"Perform deep technical research and feasibility assessment on: {topic}"

        res = await self.router.generate_response(system_prompt, user_prompt)
        
        return {
            "topic": topic,
            "provider": res["provider"],
            "elapsed_ms": res["elapsed_ms"],
            "report": res["content"]
        }

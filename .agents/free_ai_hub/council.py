"""
AI Council Module: Parallel multi-model consensus and debate synthesis.
"""

import asyncio
from typing import Dict, List, Optional, Any
from .client import FreeAIClient, FreeAIResponse
from .config import HubConfig, load_config
from .providers import PROVIDER_REGISTRY

class AICouncil:
    def __init__(self, client: Optional[FreeAIClient] = None):
        self.client = client or FreeAIClient()
        self.config = self.client.config

    async def debate(
        self,
        question: str,
        providers: Optional[List[str]] = None,
        synthesize: bool = True
    ) -> Dict[str, Any]:
        """
        Query multiple free models simultaneously and synthesize a consensus.
        """
        active_providers = [p.name for p in self.config.get_active_providers()]
        if not active_providers:
            raise RuntimeError("No active free AI providers found. Please set at least one key.")

        # Pick top active providers
        target_providers = []
        if providers:
            target_providers = [p for p in providers if p in active_providers]
        else:
            # Pick diverse providers (e.g. Groq, Gemini, SambaNova, OpenRouter, Mistral)
            priority = ["groq", "sambanova", "gemini", "openrouter", "cerebras", "siliconflow", "mistral"]
            for p in priority:
                if p in active_providers:
                    target_providers.append(p)
                if len(target_providers) >= 3:
                    break
            
            # If still less than 3, add any remaining
            for p in active_providers:
                if p not in target_providers:
                    target_providers.append(p)
                if len(target_providers) >= 3:
                    break

        if not target_providers:
            target_providers = active_providers[:1]

        # Execute parallel queries
        tasks = []
        for prov_name in target_providers:
            tasks.append(
                self.client.query(
                    prompt=question,
                    provider=prov_name,
                    system_prompt="You are an expert AI advisor in an AI Council. Provide a precise, well-reasoned, and rigorous answer."
                )
            )

        responses: List[Any] = await asyncio.gather(*tasks, return_exceptions=True)
        
        council_opinions = []
        valid_responses = []

        for prov_name, res in zip(target_providers, responses):
            spec = PROVIDER_REGISTRY[prov_name]
            if isinstance(res, Exception):
                council_opinions.append({
                    "provider": prov_name,
                    "display_name": spec.display_name,
                    "status": "failed",
                    "error": str(res)
                })
            else:
                valid_responses.append(res)
                council_opinions.append({
                    "provider": prov_name,
                    "display_name": spec.display_name,
                    "model": res.model,
                    "latency_ms": res.latency_ms,
                    "response": res.text
                })

        synthesis_text = ""
        if synthesize and len(valid_responses) > 1:
            try:
                synthesis_prompt = (
                    f"Question: {question}\n\n"
                    f"Here are independent perspectives from different AI models:\n\n"
                )
                for i, r in enumerate(valid_responses, 1):
                    synthesis_prompt += f"--- Perspective {i} ({r.provider} - {r.model}) ---\n{r.text}\n\n"

                synthesis_prompt += (
                    "Synthesize these perspectives into a unified, definitive consensus. "
                    "Highlight agreements, resolve differences, and present the single best recommended solution."
                )

                synthesis_res = await self.client.query(
                    prompt=synthesis_prompt,
                    category="reasoning",
                    system_prompt="You are the Lead Chair of the AI Council. Synthesize multi-model perspectives into the definitive best answer."
                )
                synthesis_text = synthesis_res.text
            except Exception as e:
                synthesis_text = f"Synthesis skipped due to: {str(e)}"
        elif len(valid_responses) == 1:
            synthesis_text = valid_responses[0].text

        return {
            "question": question,
            "participating_models_count": len(valid_responses),
            "council_opinions": council_opinions,
            "synthesis": synthesis_text
        }

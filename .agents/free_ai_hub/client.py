"""
Unified Async Free AI Client with Smart Failover and Load-Balancing.
"""

import time
import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
import aiohttp

from .config import load_config, HubConfig
from .providers import PROVIDER_REGISTRY, CATEGORY_FALLBACK_ORDER, default_auth_header, ProviderSpec

class FreeAIResponse:
    def __init__(
        self,
        text: str,
        provider: str,
        model: str,
        latency_ms: float,
        usage: Optional[Dict[str, Any]] = None,
        raw: Optional[Dict[str, Any]] = None
    ):
        self.text = text
        self.provider = provider
        self.model = model
        self.latency_ms = latency_ms
        self.usage = usage or {}
        self.raw = raw or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "provider": self.provider,
            "model": self.model,
            "latency_ms": round(self.latency_ms, 2),
            "usage": self.usage
        }

class FreeAIClient:
    def __init__(self, config: Optional[HubConfig] = None):
        self.config = config or load_config()

    async def _send_chat_request(
        self,
        session: aiohttp.ClientSession,
        spec: ProviderSpec,
        api_key: str,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2048,
        timeout_seconds: float = 45.0
    ) -> FreeAIResponse:
        start_time = time.perf_counter()
        
        # Build headers
        if spec.headers_factory:
            headers = spec.headers_factory(api_key)
        else:
            headers = default_auth_header(api_key)

        url = f"{spec.base_url.rstrip('/')}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        timeout = aiohttp.ClientTimeout(total=timeout_seconds)
        async with session.post(url, json=payload, headers=headers, timeout=timeout) as response:
            latency = (time.perf_counter() - start_time) * 1000.0
            
            if response.status != 200:
                err_body = await response.text()
                raise RuntimeError(
                    f"Provider {spec.name} ({model}) returned HTTP {response.status}: {err_body[:300]}"
                )

            data = await response.json()
            choices = data.get("choices", [])
            if not choices:
                raise RuntimeError(f"No choices returned from {spec.name} for model {model}")

            text = choices[0].get("message", {}).get("content", "")
            usage = data.get("usage", {})
            
            return FreeAIResponse(
                text=text,
                provider=spec.name,
                model=model,
                latency_ms=latency,
                usage=usage,
                raw=data
            )

    async def query(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        category: str = "general",
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> FreeAIResponse:
        """
        Query a free AI model with smart fallback across available active providers.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        # If specific provider requested
        if provider:
            spec = PROVIDER_REGISTRY.get(provider.lower())
            if not spec:
                raise ValueError(f"Unknown provider: {provider}")
            api_key = self.config.get_api_key(spec.name)
            if not api_key:
                raise ValueError(f"Provider {spec.display_name} has no API key configured. Set {spec.env_key}.")

            target_model = model or spec.default_model
            async with aiohttp.ClientSession() as session:
                return await self._send_chat_request(
                    session=session,
                    spec=spec,
                    api_key=api_key,
                    model=target_model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

        # Automatic category-based routing with failover chain
        fallback_order = CATEGORY_FALLBACK_ORDER.get(category.lower(), CATEGORY_FALLBACK_ORDER["general"])
        
        # Add any remaining active providers to fallback list
        active_names = [p.name for p in self.config.get_active_providers()]
        candidate_providers = [p for p in fallback_order if p in active_names]
        for p in active_names:
            if p not in candidate_providers:
                candidate_providers.append(p)

        if not candidate_providers:
            raise RuntimeError(
                "No Free AI Providers are currently configured with an API key.\n"
                "Please add at least one free API key in free_ai_keys.env or .env "
                "(e.g. GROQ_API_KEY, GEMINI_API_KEY, OPENROUTER_API_KEY, SAMBANOVA_API_KEY)."
            )

        errors = []
        async with aiohttp.ClientSession() as session:
            for prov_name in candidate_providers:
                spec = PROVIDER_REGISTRY[prov_name]
                api_key = self.config.get_api_key(prov_name)
                target_model = model if (model and model in spec.models) else spec.default_model
                
                try:
                    res = await self._send_chat_request(
                        session=session,
                        spec=spec,
                        api_key=api_key,
                        model=target_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        timeout_seconds=20.0
                    )
                    return res
                except Exception as e:
                    errors.append(f"[{spec.display_name}] {str(e)}")
                    # Continue to next fallback provider
                    continue

        raise RuntimeError(f"All configured free providers failed.\nErrors:\n" + "\n".join(errors))

    async def benchmark_provider(self, provider_name: str) -> Dict[str, Any]:
        """Test provider connectivity and return latency."""
        spec = PROVIDER_REGISTRY.get(provider_name.lower())
        if not spec:
            return {"provider": provider_name, "status": "unknown_provider"}

        api_key = self.config.get_api_key(provider_name)
        if not api_key:
            return {
                "provider": spec.name,
                "display_name": spec.display_name,
                "status": "missing_key",
                "env_key": spec.env_key,
                "doc_url": spec.doc_url
            }

        try:
            res = await self.query(
                prompt="Respond with 'PONG' and nothing else.",
                provider=spec.name,
                model=spec.default_model,
                max_tokens=10
            )
            return {
                "provider": spec.name,
                "display_name": spec.display_name,
                "status": "online",
                "model": res.model,
                "latency_ms": res.latency_ms,
                "sample_response": res.text.strip()
            }
        except Exception as e:
            return {
                "provider": spec.name,
                "display_name": spec.display_name,
                "status": "error",
                "error": str(e)
            }

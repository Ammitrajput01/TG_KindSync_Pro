"""
Provider definitions and free model catalogs for Universal Free AI Hub.
All providers listed here offer genuine free tiers or free trial access without mandatory paid setup.
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class ProviderSpec:
    name: str
    display_name: str
    base_url: str
    env_key: str
    models: List[str]
    default_model: str
    categories: List[str]  # e.g. ["fast", "reasoning", "coding", "general"]
    doc_url: str
    free_tier_info: str
    headers_factory: Any = None

def default_auth_header(api_key: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def openrouter_auth_header(api_key: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://antigravity.google.com",
        "X-Title": "Antigravity Free AI Hub"
    }

def gemini_auth_header(api_key: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def huggingface_auth_header(api_key: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

# Comprehensive registry of 100% Free / Generous Free Tier providers
PROVIDER_REGISTRY: Dict[str, ProviderSpec] = {
    "groq": ProviderSpec(
        name="groq",
        display_name="Groq (LPU Ultra-Fast)",
        base_url="https://api.groq.com/openai/v1",
        env_key="GROQ_API_KEY",
        models=[
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.6-27b",
            "qwen/qwen3.8-27b",
            "groq/compound",
            "groq/compound-mini",
            "whisper-large-v3-turbo"
        ],
        default_model="openai/gpt-oss-120b",
        categories=["fast", "coding", "general", "reasoning"],
        doc_url="https://console.groq.com/keys",
        free_tier_info="Free tier: 30 RPM / 14,400 RPD, ~500 tokens/sec speed (No Credit Card required)"
    ),
    "cerebras": ProviderSpec(
        name="cerebras",
        display_name="Cerebras (Wafer-Scale Fast)",
        base_url="https://api.cerebras.ai/v1",
        env_key="CEREBRAS_API_KEY",
        models=[
            "qwen-3.8-27b",
            "gpt-oss-120b",
            "gemma-4-31b"
        ],
        default_model="qwen-3.8-27b",
        categories=["fast", "general", "coding"],
        doc_url="https://cloud.cerebras.ai",
        free_tier_info="Free tier: 30 RPM / 1,000,000 TPM with ultra-low latency"
    ),
    "sambanova": ProviderSpec(
        name="sambanova",
        display_name="SambaNova Systems Cloud",
        base_url="https://api.sambanova.ai/v1",
        env_key="SAMBANOVA_API_KEY",
        models=[
            "DeepSeek-V3.2",
            "DeepSeek-V3.1",
            "gpt-oss-120b",
            "MiniMax-M3",
            "MiniMax-M2.7",
            "gemma-4-31B-it",
            "Meta-Llama-3.3-70B-Instruct"
        ],
        default_model="DeepSeek-V3.2",
        categories=["reasoning", "general", "coding", "fast"],
        doc_url="https://cloud.sambanova.ai/apis",
        free_tier_info="Free tier: High concurrency free access to DeepSeek V3.2, MiniMax M3 & Llama"
    ),
    "openrouter": ProviderSpec(
        name="openrouter",
        display_name="OpenRouter (Free Aggregator)",
        base_url="https://openrouter.ai/api/v1",
        env_key="OPENROUTER_API_KEY",
        models=[
            "nvidia/nemotron-3.5-lightning:free",
            "minimax/minimax-m3:free",
            "cohere/north-mini-code:free",
            "liquid/lfm-2.5-2.6b:free",
            "z-ai/glm-5.2:free",
            "google/gemma-4-26b-a4b-it:free"
        ],
        default_model="nvidia/nemotron-3.5-lightning:free",
        categories=["reasoning", "general", "coding"],
        doc_url="https://openrouter.ai/keys",
        free_tier_info="Free tier: 20+ completely free models with ':free' suffix",
        headers_factory=openrouter_auth_header
    ),
    "gemini": ProviderSpec(
        name="gemini",
        display_name="Google Gemini API (AI Studio)",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai",
        env_key="GEMINI_API_KEY",
        models=[
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-flash-latest",
            "gemini-pro-latest",
            "gemma-4-31b-it",
            "gemini-2.5-flash-lite"
        ],
        default_model="gemini-2.5-flash",
        categories=["general", "coding", "reasoning", "fast"],
        doc_url="https://aistudio.google.com/app/apikey",
        free_tier_info="Free tier: 15 RPM / 1,500 RPD for 2.5 Flash with 1M token context (No CC required)"
    ),
    "siliconflow": ProviderSpec(
        name="siliconflow",
        display_name="SiliconFlow (SiliconCloud)",
        base_url="https://api.siliconflow.cn/v1",
        env_key="SILICONFLOW_API_KEY",
        models=[
            "deepseek-ai/DeepSeek-V3",
            "deepseek-ai/DeepSeek-R1",
            "Qwen/Qwen2.5-72B-Instruct",
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "THUDM/glm-4-9b-chat"
        ],
        default_model="deepseek-ai/DeepSeek-V3",
        categories=["reasoning", "coding", "general"],
        doc_url="https://cloud.siliconflow.cn/account/ak",
        free_tier_info="Free tier: Generous free credits & free models on signup"
    ),
    "mistral": ProviderSpec(
        name="mistral",
        display_name="Mistral AI (La Plateforme)",
        base_url="https://api.mistral.ai/v1",
        env_key="MISTRAL_API_KEY",
        models=[
            "codestral-latest",
            "mistral-small-latest",
            "pixtral-12b-2409",
            "open-mistral-nemo"
        ],
        default_model="codestral-latest",
        categories=["coding", "general", "reasoning"],
        doc_url="https://console.mistral.ai/api-keys",
        free_tier_info="Free tier: Free experimental & API access for developers"
    ),
    "deepseek": ProviderSpec(
        name="deepseek",
        display_name="DeepSeek Direct API",
        base_url="https://api.deepseek.com/v1",
        env_key="DEEPSEEK_API_KEY",
        models=[
            "deepseek-chat",
            "deepseek-reasoner"
        ],
        default_model="deepseek-reasoner",
        categories=["reasoning", "coding", "general"],
        doc_url="https://platform.deepseek.com/api_keys",
        free_tier_info="Free trial credits on signup / ultra-low cost"
    ),
    "nvidia": ProviderSpec(
        name="nvidia",
        display_name="NVIDIA NIM (Cloud Endpoints)",
        base_url="https://integrate.api.nvidia.com/v1",
        env_key="NVIDIA_API_KEY",
        models=[
            "meta/llama-3.3-70b-instruct",
            "nvidia/llama-3.1-nemotron-70b-instruct",
            "deepseek-ai/deepseek-r1",
            "qwen/qwen2.5-coder-32b-instruct",
            "mistralai/mistral-large-2-instruct"
        ],
        default_model="meta/llama-3.3-70b-instruct",
        categories=["reasoning", "general", "fast", "coding"],
        doc_url="https://build.nvidia.com",
        free_tier_info="Free tier: 1000 free build credits for NIM cloud inference"
    ),
    "freellmapi": ProviderSpec(
        name="freellmapi",
        display_name="FreeLLMAPI (34 Providers / 635 Free Endpoints)",
        base_url="http://localhost:8000/v1",
        env_key="FREELLMAPI_API_KEY",
        models=[
            "auto",
            "deepseek/deepseek-r1",
            "deepseek/deepseek-chat",
            "qwen/qwen-2.5-72b-instruct",
            "meta-llama/llama-3.3-70b-instruct",
            "mistralai/mistral-large"
        ],
        default_model="auto",
        categories=["general", "coding", "reasoning", "fast"],
        doc_url="https://github.com/tashfeenahmed/freellmapi",
        free_tier_info="Free tier: Aggregates 34 free providers, ~7.4 Billion free tokens/mo"
    ),
    "huggingface": ProviderSpec(
        name="huggingface",
        display_name="Hugging Face Serverless Inference",
        base_url="https://api-inference.huggingface.co/v1",
        env_key="HUGGINGFACE_API_KEY",
        models=[
            "Qwen/Qwen2.5-Coder-32B-Instruct",
            "meta-llama/Llama-3.2-3B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3"
        ],
        default_model="Qwen/Qwen2.5-Coder-32B-Instruct",
        categories=["coding", "general"],
        doc_url="https://huggingface.co/settings/tokens",
        free_tier_info="Free tier: Serverless inference API for open models"
    ),
    "cloudflare": ProviderSpec(
        name="cloudflare",
        display_name="Cloudflare Workers AI",
        base_url="https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1",
        env_key="CLOUDFLARE_API_KEY",
        models=[
            "@cf/meta/llama-3.3-70b-instruct",
            "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b",
            "@cf/mistral/mistral-7b-instruct-v0.1"
        ],
        default_model="@cf/meta/llama-3.3-70b-instruct",
        categories=["fast", "general", "reasoning"],
        doc_url="https://dash.cloudflare.com",
        free_tier_info="Free tier: 10,000 neurons per day (~100k tokens free daily)"
    )
}

# Category prioritization order for automatic fallback routing
CATEGORY_FALLBACK_ORDER: Dict[str, List[str]] = {
    "fast": ["groq", "cerebras", "sambanova", "gemini", "nvidia", "freellmapi", "openrouter"],
    "reasoning": ["sambanova", "nvidia", "openrouter", "deepseek", "siliconflow", "gemini", "groq", "freellmapi"],
    "coding": ["groq", "mistral", "nvidia", "sambanova", "siliconflow", "gemini", "huggingface", "freellmapi", "openrouter"],
    "general": ["gemini", "groq", "sambanova", "nvidia", "cerebras", "openrouter", "mistral", "siliconflow", "freellmapi"]
}

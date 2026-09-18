"""
Universal Free AI Model Hub
High-performance, zero-cost AI router with multi-provider failover and Antigravity MCP integration.
"""

from .config import HubConfig, load_config
from .client import FreeAIClient
from .providers import PROVIDER_REGISTRY

__version__ = "1.0.0"
__all__ = ["HubConfig", "load_config", "FreeAIClient", "PROVIDER_REGISTRY"]

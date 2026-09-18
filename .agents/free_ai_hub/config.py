"""
Configuration and Environment loader for Universal Free AI Hub.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

from .providers import PROVIDER_REGISTRY, ProviderSpec

class HubConfig:
    def __init__(self, env_files: Optional[List[str]] = None):
        cur_file = Path(__file__).resolve()
        # Find root workspace by looking up for .env or .git
        ws = cur_file.parent.parent
        if cur_file.parent.parent.name == ".agents":
            ws = cur_file.parent.parent.parent
        self.workspace_dir = ws
        self.agents_dir = ws / ".agents"
        self.env_files = env_files or [
            str(self.workspace_dir / ".env"),
            str(self.agents_dir / "free_ai_keys.env"),
            str(self.workspace_dir / "free_ai_keys.env")
        ]
        self.reload()

    def reload(self):
        """Reload environment variables from known locations without overwriting non-empty with empty."""
        from dotenv import dotenv_values
        self._cached_keys = {}
        # First load OS environment
        for k, v in os.environ.items():
            if v and v.strip():
                self._cached_keys[k] = v.strip().strip("'\"")

        # Then load from env files (later files override if non-empty)
        for env_path in self.env_files:
            if os.path.exists(env_path):
                vals = dotenv_values(env_path)
                for k, v in vals.items():
                    if v and v.strip():
                        self._cached_keys[k] = v.strip().strip("'\"")

    def get_api_key(self, provider_name: str) -> Optional[str]:
        spec = PROVIDER_REGISTRY.get(provider_name.lower())
        if not spec:
            return None
        val = self._cached_keys.get(spec.env_key) or os.getenv(spec.env_key)
        if val and val.strip():
            clean = val.strip().strip("'\"")
            if clean:
                return clean
        return None

    def get_active_providers(self) -> List[ProviderSpec]:
        """Return list of providers that have an API key configured."""
        active = []
        for name, spec in PROVIDER_REGISTRY.items():
            key = self.get_api_key(name)
            if key:
                active.append(spec)
        return active

    def is_provider_active(self, provider_name: str) -> bool:
        return self.get_api_key(provider_name) is not None

    def get_status_summary(self) -> Dict[str, Any]:
        """Get summary of all providers and their key status."""
        active_list = []
        inactive_list = []
        for name, spec in PROVIDER_REGISTRY.items():
            has_key = self.is_provider_active(name)
            info = {
                "name": spec.name,
                "display_name": spec.display_name,
                "env_key": spec.env_key,
                "has_key": has_key,
                "default_model": spec.default_model,
                "models_count": len(spec.models),
                "doc_url": spec.doc_url,
                "free_tier_info": spec.free_tier_info
            }
            if has_key:
                active_list.append(info)
            else:
                inactive_list.append(info)

        return {
            "total_providers": len(PROVIDER_REGISTRY),
            "active_count": len(active_list),
            "inactive_count": len(inactive_list),
            "active_providers": active_list,
            "inactive_providers": inactive_list
        }

_CONFIG_INSTANCE: Optional[HubConfig] = None

def load_config(reload: bool = False) -> HubConfig:
    global _CONFIG_INSTANCE
    if _CONFIG_INSTANCE is None or reload:
        _CONFIG_INSTANCE = HubConfig()
    return _CONFIG_INSTANCE

"""
DEVI Live Global Telegram OSINT & Entity Resolution Engine
Resolves ANY Telegram username, numerical ID, phone number or entity across global Telegram MTProto infrastructure.
"""

import asyncio
import os
import json
import logging
from typing import Optional, Dict, Any
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest

logger = logging.getLogger("DEVI.OSINTResolver")

class GlobalOSINTResolver:
    def __init__(self):
        self.api_id = int(os.getenv("API_ID", "0"))
        self.api_hash = os.getenv("API_HASH", "")
        self.session_names = ["session_scanner", "session_account_9081"]
        self._client: Optional[TelegramClient] = None
        self._lock = asyncio.Lock()

    async def _get_client(self) -> Optional[TelegramClient]:
        if self._client and self._client.is_connected():
            return self._client
        for s_name in self.session_names:
            try:
                c = TelegramClient(s_name, self.api_id, self.api_hash)
                await c.connect()
                if await c.is_user_authorized():
                    self._client = c
                    return self._client
                await c.disconnect()
            except Exception as e:
                logger.warning(f"Failed connecting to session {s_name}: {e}")
        return None

    async def resolve_entity(self, target: str) -> Optional[Dict[str, Any]]:
        """
        Resolves ANY username (@username), phone (+91...), or user_id globally.
        Returns full OSINT metadata or None.
        """
        async with self._lock:
            client = await self._get_client()
            if not client:
                return None
            try:
                query = str(target).strip()
                if query.isdigit():
                    query = int(query)
                elif not query.startswith("@") and not query.startswith("+") and not str(query).isdigit():
                    query = f"@{query}"

                user = await client.get_entity(query)
                if not user:
                    return None

                full_user = None
                try:
                    full = await client(GetFullUserRequest(user))
                    full_user = full.full_user
                except Exception:
                    pass

                fn = getattr(user, "first_name", "") or ""
                ln = getattr(user, "last_name", "") or ""
                full_name = f"{fn} {ln}".strip() or "Anonymous"
                bio = getattr(full_user, "about", None) if full_user else None
                common_chats = getattr(full_user, "common_chats_count", 0) if full_user else 0

                photo_obj = getattr(user, "photo", None)
                dc_id = getattr(photo_obj, "dc_id", None) if photo_obj else None

                return {
                    "user_id": user.id,
                    "first_name": fn,
                    "last_name": ln,
                    "full_name": full_name,
                    "username": getattr(user, "username", "") or "",
                    "phone": getattr(user, "phone", None) or "Not Shared",
                    "is_premium": getattr(user, "premium", False),
                    "is_bot": getattr(user, "bot", False),
                    "is_verified": getattr(user, "verified", False),
                    "is_scam": getattr(user, "scam", False),
                    "is_fake": getattr(user, "fake", False),
                    "is_restricted": getattr(user, "restricted", False),
                    "bio": bio,
                    "common_chats_count": common_chats,
                    "dc_id": dc_id
                }
            except Exception as ex:
                logger.warning(f"Error resolving global entity '{target}': {ex}")
                return None

# Global Singleton Instance
osint_resolver = GlobalOSINTResolver()

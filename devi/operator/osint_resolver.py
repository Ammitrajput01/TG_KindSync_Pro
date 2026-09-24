"""
DEVI Live Global Telegram OSINT & Entity Resolution Engine
Resolves ANY Telegram username, numerical ID, phone number or entity across global Telegram MTProto infrastructure.
Seamlessly intercepts live SangMata (@SangMata_beta_bot / @sangmata_bot) biometric history timelines,
persists multi-year records in SQLite cache, and builds deep forensic intelligence dossiers.
"""

import asyncio
import os
import glob
import json
import logging
import sqlite3
import re
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from contextlib import suppress

from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest

logger = logging.getLogger("DEVI.OSINTResolver")

BASE_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_PROJECT_DIR / "history_core.sqlite"


def get_db_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 30000")
    # Initialize sangmata cache table if not present
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sangmata_osint_cache (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            raw_response TEXT,
            names_json TEXT,
            usernames_json TEXT,
            total_shifts INTEGER DEFAULT 0,
            cached_at REAL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sangmata_uname ON sangmata_osint_cache(username);")
    conn.commit()
    return conn


class GlobalOSINTResolver:
    def __init__(self):
        self.api_id = int(os.getenv("API_ID", "0"))
        self.api_hash = os.getenv("API_HASH", "")
        self._client: Optional[TelegramClient] = None
        self._lock = asyncio.Lock()

    def get_candidate_sessions(self) -> List[str]:
        """Dynamically finds all valid .session files in the workspace root."""
        candidates = [
            "session_bot_scanner",
            "session_forwarder",
            "session_account2",
            "session_account3",
            "session_scanner",
            "session_account_9081"
        ]
        found = []
        for c in candidates:
            if (BASE_PROJECT_DIR / f"{c}.session").exists():
                found.append(c)

        for p in BASE_PROJECT_DIR.glob("*.session"):
            stem = p.stem
            if stem not in found:
                found.append(stem)
        return found if found else ["session_bot_scanner", "session_forwarder"]

    def _find_candidate_sessions(self) -> List[str]:
        """Internal helper for test backward-compatibility."""
        return self.get_candidate_sessions()

    async def _get_client(self, require_user: bool = False) -> Optional[TelegramClient]:
        if self._client and self._client.is_connected():
            try:
                if await self._client.is_user_authorized():
                    if require_user:
                        me = await self._client.get_me()
                        if not me.bot:
                            return self._client
                    else:
                        return self._client
            except Exception:
                pass

        if not self.api_id or not self.api_hash:
            return None

        for s_name in self.get_candidate_sessions():
            s_path = str(BASE_PROJECT_DIR / s_name)
            try:
                c = TelegramClient(s_path, self.api_id, self.api_hash)
                await c.connect()
                if await c.is_user_authorized():
                    me = await c.get_me()
                    if require_user and me.bot:
                        await c.disconnect()
                        continue
                    self._client = c
                    logger.info(f"Connected to MTProto OSINT session: '{s_name}' (bot={me.bot})")
                    return self._client
                await c.disconnect()
            except Exception as e:
                logger.debug(f"Could not use session '{s_name}': {e}")
        return None

    async def resolve_entity(self, target: str) -> Optional[Dict[str, Any]]:
        """
        Resolves ANY username (@username), phone (+91...), or user_id globally.
        Returns full OSINT metadata or falls back to local dossier.
        """
        query_str = str(target).strip()
        
        # 1. Try Live MTProto Resolution via Active Session
        async with self._lock:
            client = await self._get_client(require_user=False)
            if client:
                try:
                    query = query_str
                    if query.isdigit():
                        query = int(query)
                    elif not query.startswith("@") and not query.startswith("+") and not str(query).isdigit():
                        query = f"@{query}"

                    user = await client.get_entity(query)
                    if user:
                        full_user = None
                        with suppress(Exception):
                            full = await client(GetFullUserRequest(user))
                            full_user = full.full_user

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
                            "dc_id": dc_id,
                            "source": "live_mtproto"
                        }
                except Exception as ex:
                    logger.debug(f"Live MTProto entity resolution fallback for '{target}': {ex}")

        # 2. Fallback to Local SQLite Dossier
        return self.resolve_from_local_db(query_str)

    def resolve_from_local_db(self, target: str) -> Optional[Dict[str, Any]]:
        """Resolves user entity metadata from local SQLite database."""
        clean_target = str(target).strip().lstrip("@")
        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                row = None
                if clean_target.isdigit():
                    row = conn.execute(
                        "SELECT * FROM telegram_users_dossier WHERE user_id = ?",
                        (int(clean_target),)
                    ).fetchone()
                else:
                    row = conn.execute(
                        "SELECT * FROM telegram_users_dossier WHERE username = ? COLLATE NOCASE",
                        (clean_target,)
                    ).fetchone()
                    if not row:
                        name_row = conn.execute(
                            "SELECT user_id FROM member_name_changes WHERE old_username = ? OR new_username = ? COLLATE NOCASE LIMIT 1",
                            (clean_target, clean_target)
                        ).fetchone()
                        if name_row:
                            row = conn.execute(
                                "SELECT * FROM telegram_users_dossier WHERE user_id = ?",
                                (name_row["user_id"],)
                            ).fetchone()

                if row:
                    fn = row["first_name"] or ""
                    ln = row["last_name"] or ""
                    full_name = f"{fn} {ln}".strip() or "Anonymous"
                    return {
                        "user_id": row["user_id"],
                        "first_name": fn,
                        "last_name": ln,
                        "full_name": full_name,
                        "username": row["username"] or "",
                        "phone": row["phone_number"] or "Not Shared",
                        "is_premium": bool(row["is_premium"]),
                        "is_bot": False,
                        "is_verified": False,
                        "is_scam": False,
                        "is_fake": False,
                        "is_restricted": False,
                        "bio": None,
                        "common_chats_count": 0,
                        "dc_id": None,
                        "source": "local_sqlite_dossier"
                    }
        except Exception as e:
            logger.warning(f"Error querying local SQLite dossier: {e}")
        return None

    @staticmethod
    def parse_sangmata_raw_text(raw_text: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        """
        Parses raw text returned from @SangMata_beta_bot into structured name & username timelines.
        Extracts entries with format:
          1. [DD/MM/YY HH:MM:SS] Name / @Username
        """
        names_list = []
        usernames_list = []

        if not raw_text:
            return names_list, usernames_list

        text = raw_text.replace("\r\n", "\n")
        
        # Split into Names section and Usernames section
        names_part = ""
        usernames_part = ""

        if "Usernames" in text:
            parts = text.split("Usernames", 1)
            names_part = parts[0]
            usernames_part = parts[1]
        elif "Names" in text:
            names_part = text
        else:
            names_part = text

        # Regex pattern for numbered timestamped line:
        # e.g., 1. [09/09/26 17:56:30] Dr. NSC 🩺
        pattern = r"(\d+)\.\s*\[([\d\/\:\s\-]+)\]\s*(.*?)(?=\n\s*\d+\.|\n\s*Usernames|\n\s*\n|\Z)"

        if names_part:
            matches = re.findall(pattern, names_part, re.DOTALL)
            for num, ts, val in matches:
                clean_val = val.strip()
                if clean_val:
                    names_list.append({
                        "num": int(num),
                        "changed_at": ts.strip(),
                        "name": clean_val
                    })

        if usernames_part:
            matches = re.findall(pattern, usernames_part, re.DOTALL)
            for num, ts, val in matches:
                clean_val = val.strip()
                if clean_val:
                    usernames_list.append({
                        "num": int(num),
                        "changed_at": ts.strip(),
                        "username": clean_val
                    })

        return names_list, usernames_list

    async def fetch_live_sangmata_history(self, target: str | int) -> Dict[str, Any]:
        """
        Fetches full multi-year change timeline:
        1. Checks local SQLite cache (sangmata_osint_cache).
        2. If cache miss, queries real @SangMata_beta_bot / @sangmata_bot via MTProto.
        3. Parses response, persists to cache, and returns complete A-to-Z historical timeline.
        """
        target_str = str(target).strip()
        user_id = int(target_str) if target_str.isdigit() else None
        username = target_str.lstrip("@") if not target_str.isdigit() else None

        # 1. Check local SQLite SangMata Cache
        cached_data = self._get_cached_sangmata(user_id=user_id, username=username)
        if cached_data and cached_data.get("names"):
            return cached_data

        # 2. Try Live MTProto query to @SangMata_beta_bot using human user session
        live_result = await self._query_sangmata_bot(target_str)
        if live_result and (live_result.get("names") or live_result.get("usernames")):
            self._save_cached_sangmata(live_result)
            return live_result

        # 3. Fallback to local SQLite member_name_changes and dossier
        if user_id:
            fallback = self.get_sangmata_history(user_id)
            return {
                "user_id": user_id,
                "names": fallback.get("name_history", []),
                "usernames": fallback.get("username_history", []),
                "total_shifts": fallback.get("total_shifts", 0),
                "source": "local_sqlite_fallback"
            }

        return {
            "user_id": user_id,
            "names": [],
            "usernames": [],
            "total_shifts": 0,
            "source": "empty"
        }

    async def _query_sangmata_bot(self, target_query: str) -> Optional[Dict[str, Any]]:
        """Queries @SangMata_beta_bot / @sangmata_bot / @SangMataInfo_bot via MTProto conversation using an authorized user session."""
        async with self._lock:
            client = await self._get_client(require_user=True)
            if not client:
                return None

            bots_to_try = [
                "@SangMata_beta_bot", 
                "@sangmata_bot", 
                "@SangMataInfo_bot", 
                "@Sangmatainfobot",
                "@SangMata_robot"
            ]
            for bot_handle in bots_to_try:
                try:
                    async with client.conversation(bot_handle, timeout=10.0) as conv:
                        await conv.send_message(target_query)
                        resp = await conv.get_response()
                        if resp and resp.text:
                            text = resp.text
                            if "Invalid ID" in text or "Send \"help\"" in text or "No data" in text:
                                continue
                            names, usernames = self.parse_sangmata_raw_text(text)
                            uid_match = re.search(r"History for (\d+)", text)
                            extracted_id = int(uid_match.group(1)) if uid_match else (int(target_query) if target_query.isdigit() else None)
                            
                            return {
                                "user_id": extracted_id,
                                "username": target_query.lstrip("@") if not target_query.isdigit() else "",
                                "names": names,
                                "usernames": usernames,
                                "raw_response": text,
                                "total_shifts": len(names) + len(usernames),
                                "source": "sangmata_live_mtproto"
                            }
                except Exception as e:
                    logger.debug(f"SangMata query to {bot_handle} failed: {e}")
            return None

    def _get_cached_sangmata(self, user_id: Optional[int] = None, username: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Retrieves cached SangMata history from SQLite."""
        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                row = None
                if user_id:
                    row = conn.execute("SELECT * FROM sangmata_osint_cache WHERE user_id = ?", (user_id,)).fetchone()
                elif username:
                    row = conn.execute("SELECT * FROM sangmata_osint_cache WHERE username = ? COLLATE NOCASE", (username,)).fetchone()

                if row:
                    names = json.loads(row["names_json"] or "[]")
                    usernames = json.loads(row["usernames_json"] or "[]")
                    return {
                        "user_id": row["user_id"],
                        "username": row["username"],
                        "full_name": row["full_name"],
                        "names": names,
                        "usernames": usernames,
                        "raw_response": row["raw_response"],
                        "total_shifts": row["total_shifts"],
                        "cached_at": row["cached_at"],
                        "source": "sangmata_sqlite_cache"
                    }
        except Exception as e:
            logger.debug(f"Error fetching cached sangmata: {e}")
        return None

    def _save_cached_sangmata(self, data: Dict[str, Any]):
        """Saves parsed SangMata timeline to SQLite cache."""
        try:
            user_id = data.get("user_id")
            if not user_id:
                return
            with get_db_conn() as conn:
                conn.execute("""
                    INSERT INTO sangmata_osint_cache (user_id, username, full_name, raw_response, names_json, usernames_json, total_shifts, cached_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(user_id) DO UPDATE SET
                        username = excluded.username,
                        full_name = excluded.full_name,
                        raw_response = excluded.raw_response,
                        names_json = excluded.names_json,
                        usernames_json = excluded.usernames_json,
                        total_shifts = excluded.total_shifts,
                        cached_at = excluded.cached_at,
                        updated_at = CURRENT_TIMESTAMP;
                """, (
                    user_id,
                    data.get("username", ""),
                    data.get("full_name", ""),
                    data.get("raw_response", ""),
                    json.dumps(data.get("names", [])),
                    json.dumps(data.get("usernames", [])),
                    data.get("total_shifts", 0),
                    time.time()
                ))
                conn.commit()
        except Exception as e:
            logger.warning(f"Error saving sangmata cache: {e}")

    def get_sangmata_history(self, user_id: int) -> Dict[str, Any]:
        """Fetches full name and username change timeline from local event history."""
        name_history = []
        username_history = []
        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                # 1. From sangmata_osint_cache if available
                cached = conn.execute("SELECT * FROM sangmata_osint_cache WHERE user_id = ?", (user_id,)).fetchone()
                if cached:
                    try:
                        return {
                            "user_id": user_id,
                            "name_history": json.loads(cached["names_json"] or "[]"),
                            "username_history": json.loads(cached["usernames_json"] or "[]"),
                            "total_shifts": cached["total_shifts"]
                        }
                    except Exception:
                        pass

                # 2. From member_name_changes table
                rows = conn.execute(
                    "SELECT * FROM member_name_changes WHERE user_id = ? ORDER BY changed_at ASC",
                    (user_id,)
                ).fetchall()
                for r in rows:
                    if r["old_name"] and r["new_name"] and r["old_name"] != r["new_name"]:
                        name_history.append({"name": r["old_name"], "changed_at": r["changed_at"]})
                    if r["old_username"] and r["new_username"] and r["old_username"] != r["new_username"]:
                        username_history.append({"username": r["old_username"], "changed_at": r["changed_at"]})

                # 3. From telegram_users_dossier JSON columns
                dossier = conn.execute(
                    "SELECT name_history, username_history FROM telegram_users_dossier WHERE user_id = ?",
                    (user_id,)
                ).fetchone()
                if dossier:
                    try:
                        raw_nh = json.loads(dossier["name_history"] or "[]")
                        for item in raw_nh:
                            if item not in name_history:
                                name_history.append(item)
                    except Exception:
                        pass
                    try:
                        raw_uh = json.loads(dossier["username_history"] or "[]")
                        for item in raw_uh:
                            if item not in username_history:
                                username_history.append(item)
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"Error fetching SangMata history for user {user_id}: {e}")

        return {
            "user_id": user_id,
            "name_history": name_history,
            "username_history": username_history,
            "total_shifts": len(name_history) + len(username_history)
        }


# Global Singleton Instance
osint_resolver = GlobalOSINTResolver()

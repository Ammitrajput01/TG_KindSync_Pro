#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kind Doctor Universal Telethon Session Vault
Provides lock-free, concurrent MTProto access across multiple background daemons
using in-memory StringSession architecture to completely prevent SQLite database locks.
"""

import os
import sys
import asyncio
import shutil
from pathlib import Path
from typing import Tuple, Optional
from contextlib import suppress
from dotenv import load_dotenv, set_key

from telethon import TelegramClient
from telethon.sessions import StringSession

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

API_ID = int(os.getenv("API_ID", "36193727") or 36193727)
API_HASH = os.getenv("API_HASH", "fef19b9b1434a3e66b009fd31053200b").strip()
BOT_TOKEN = os.getenv("DEVI_TELEGRAM_BOT_TOKEN", "").strip().strip("'").strip('"')

SESSION_STRING_FILE = ROOT_DIR / "data" / "session_string.txt"

def get_persisted_session_string() -> Optional[str]:
    """Retrieves cached StringSession from environment or data directory."""
    s_env = os.getenv("TELEGRAM_STRING_SESSION", "").strip()
    if s_env and len(s_env) > 50:
        return s_env
    if SESSION_STRING_FILE.exists():
        try:
            val = SESSION_STRING_FILE.read_text(encoding="utf-8").strip()
            if len(val) > 50:
                return val
        except Exception:
            pass
    return None

def save_persisted_session_string(s_str: str):
    """Saves valid StringSession string to .env and data directory for permanent cross-process use."""
    if not s_str or len(s_str) < 50:
        return
    SESSION_STRING_FILE.parent.mkdir(parents=True, exist_ok=True)
    with suppress(Exception):
        SESSION_STRING_FILE.write_text(s_str.strip(), encoding="utf-8")
    env_path = ROOT_DIR / ".env"
    if env_path.exists():
        with suppress(Exception):
            set_key(str(env_path), "TELEGRAM_STRING_SESSION", s_str.strip())
    os.environ["TELEGRAM_STRING_SESSION"] = s_str.strip()

async def export_session_file_to_string(session_file_path: Path) -> Optional[str]:
    """Extracts base64 StringSession from an existing SQLite .session file with lock-free ephemeral isolation."""
    if not session_file_path.exists() or session_file_path.stat().st_size == 0:
        return None
    
    stem = session_file_path.stem
    temp_stem = f"temp_vault_export_{stem}_{os.getpid()}_{int(asyncio.get_event_loop().time()*1000) if asyncio.get_event_loop().is_running() else os.getpid()}"
    temp_sess = ROOT_DIR / f"{temp_stem}.session"
    try:
        shutil.copy2(session_file_path, temp_sess)
        for ext in ["-journal", "-wal", "-shm"]:
            j_file = ROOT_DIR / f"{stem}.session{ext}"
            if j_file.exists():
                with suppress(Exception):
                    shutil.copy2(j_file, ROOT_DIR / f"{temp_stem}.session{ext}")
        
        client = TelegramClient(str(ROOT_DIR / temp_stem), API_ID, API_HASH)
        await client.connect()
        if await client.is_user_authorized():
            s_str = StringSession.save(client.session)
            await client.disconnect()
            save_persisted_session_string(s_str)
            return s_str
        await client.disconnect()
    except Exception as e:
        print(f"[!] Session Vault export error: {e}")
    finally:
        with suppress(Exception):
            temp_sess.unlink(missing_ok=True)
            for ext in ["-journal", "-wal", "-shm"]:
                (ROOT_DIR / f"{temp_stem}.session{ext}").unlink(missing_ok=True)
    return None

async def get_vault_client(preferred_type: str = "user") -> Tuple[TelegramClient, str]:
    """
    Returns a fully authorized TelegramClient.
    Uses pure in-memory StringSession for zero file-lock collision across any number of processes.
    """
    # 1. Try existing persisted StringSession
    s_str = get_persisted_session_string()
    if s_str:
        try:
            client = TelegramClient(StringSession(s_str), API_ID, API_HASH)
            await client.connect()
            if await client.is_user_authorized():
                return client, "user"
            await client.disconnect()
        except Exception as e:
            print(f"[!] StringSession connect warning: {e}")

    # 2. Extract from candidate session files on disk
    candidate_sessions = [
        "session_forwarder",
        "session_scanner",
        "session_account_9081",
        "session_user"
    ]
    for sess_stem in candidate_sessions:
        f_path = ROOT_DIR / f"{sess_stem}.session"
        if f_path.exists() and f_path.stat().st_size > 0:
            extracted_str = await export_session_file_to_string(f_path)
            if extracted_str:
                try:
                    client = TelegramClient(StringSession(extracted_str), API_ID, API_HASH)
                    await client.connect()
                    if await client.is_user_authorized():
                        return client, "user"
                    await client.disconnect()
                except Exception:
                    pass

    # 3. Fallback to Bot Token
    print("[*] Initializing lock-free Bot Token Client...")
    bot_client = TelegramClient(StringSession(), API_ID, API_HASH)
    await bot_client.start(bot_token=BOT_TOKEN)
    return bot_client, "bot"

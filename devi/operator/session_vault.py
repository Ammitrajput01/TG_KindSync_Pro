#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kind Doctor Universal Telethon Session Vault
Provides lock-free, concurrent MTProto access across multiple background daemons
using in-memory StringSession architecture and Fernet-encrypted multi-tenant storage.
"""

import os
import sys
import asyncio
import shutil
import sqlite3
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict, List
from contextlib import suppress
from dotenv import load_dotenv, set_key

from telethon import TelegramClient
from telethon.sessions import StringSession

try:
    from cryptography.fernet import Fernet
    _HAS_FERNET = True
except ImportError:
    Fernet = None
    _HAS_FERNET = False

logger = logging.getLogger("SessionVault")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

API_ID = int(os.getenv("API_ID", "36193727") or 36193727)
API_HASH = os.getenv("API_HASH", "fef19b9b1434a3e66b009fd31053200b").strip()
BOT_TOKEN = os.getenv("DEVI_TELEGRAM_BOT_TOKEN", "").strip().strip("'").strip('"')

SESSION_STRING_FILE = ROOT_DIR / "data" / "session_string.txt"
DB_PATH = ROOT_DIR / "history_core.sqlite"

# In-memory registry of active user clients and running jobs for graceful cancellation upon disconnect
_active_user_clients: Dict[int, List[TelegramClient]] = {}
_running_user_jobs: Dict[int, List[asyncio.Task]] = {}

# ---------------------------------------------------------------------------
# Fernet Encryption & Key Management
# ---------------------------------------------------------------------------

def get_fernet_cipher():
    """Retrieves or auto-generates a persistent Fernet encryption key from .env."""
    if not _HAS_FERNET:
        return None
    key = os.getenv("FERNET_KEY") or os.getenv("ENCRYPTION_KEY")
    if not key or len(key.strip()) < 32:
        key = Fernet.generate_key().decode("utf-8")
        env_path = ROOT_DIR / ".env"
        if env_path.exists():
            with suppress(Exception):
                set_key(str(env_path), "FERNET_KEY", key)
        os.environ["FERNET_KEY"] = key
    else:
        key = key.strip()
    return Fernet(key.encode("utf-8") if isinstance(key, str) else key)

def encrypt_session_string(raw_session: str) -> str:
    """Encrypts raw StringSession to Fernet ciphertext token."""
    if not raw_session:
        return ""
    if _HAS_FERNET:
        cipher = get_fernet_cipher()
        if cipher:
            return cipher.encrypt(raw_session.strip().encode("utf-8")).decode("utf-8")
    # Base64 fallback if cryptography is not installed
    import base64
    return "b64:" + base64.b64encode(raw_session.strip().encode("utf-8")).decode("utf-8")

def decrypt_session_string(encrypted_token: str) -> Optional[str]:
    """Decrypts Fernet ciphertext token back to raw StringSession."""
    if not encrypted_token:
        return None
    if encrypted_token.startswith("b64:"):
        import base64
        try:
            return base64.b64decode(encrypted_token[4:].encode("utf-8")).decode("utf-8")
        except Exception:
            return None
    if _HAS_FERNET:
        try:
            cipher = get_fernet_cipher()
            if cipher:
                return cipher.decrypt(encrypted_token.strip().encode("utf-8")).decode("utf-8")
        except Exception:
            pass
    # Fallback for legacy unencrypted session strings if any exist
    if len(encrypted_token) > 50 and not encrypted_token.startswith("gAAAAA"):
        return encrypted_token.strip()
    return None

def mask_phone_number(phone: str) -> str:
    """Masks phone number for safe logging (e.g. +91*****3210)."""
    if not phone:
        return "***"
    phone_clean = phone.strip()
    if len(phone_clean) >= 8:
        return f"{phone_clean[:3]}*****{phone_clean[-4:]}"
    return "***"

# ---------------------------------------------------------------------------
# Global Master Session Management
# ---------------------------------------------------------------------------

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
        logger.warning(f"[!] Session Vault export error: {e}")
    finally:
        with suppress(Exception):
            temp_sess.unlink(missing_ok=True)
            for ext in ["-journal", "-wal", "-shm"]:
                (ROOT_DIR / f"{temp_stem}.session{ext}").unlink(missing_ok=True)
    return None

# ---------------------------------------------------------------------------
# Multi-Tenant SQLite Database Storage (Encrypted at Rest)
# ---------------------------------------------------------------------------

def init_linked_sessions_table():
    """Initializes the multi-tenant encrypted session table with full schema migrations."""
    try:
        with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS telegram_linked_sessions (
                    user_id INTEGER PRIMARY KEY,
                    phone_number TEXT,
                    account_name TEXT,
                    username TEXT,
                    session_string TEXT,
                    is_active INTEGER DEFAULT 1,
                    connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Schema self-healing for legacy tables missing connected_at
            try:
                conn.execute("ALTER TABLE telegram_linked_sessions ADD COLUMN connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
            except Exception:
                pass
            conn.commit()
    except Exception as e:
        logger.warning(f"[!] Warning initializing telegram_linked_sessions: {e}")

init_linked_sessions_table()

def get_user_linked_session(user_id: int) -> Optional[str]:
    """Retrieves and decrypts active StringSession strictly for a specific Telegram User ID."""
    try:
        with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
            row = conn.execute(
                "SELECT session_string FROM telegram_linked_sessions WHERE user_id = ? AND is_active = 1", 
                (user_id,)
            ).fetchone()
            if row and row[0]:
                return decrypt_session_string(row[0])
    except Exception as e:
        logger.error(f"[!] Error retrieving linked session for user {user_id}: {e}")
    return None

def save_linked_user_session(user_id: int, phone: str, session_str: str, name: str = "", username: str = "") -> bool:
    """Encrypts with Fernet and saves linked user session in SQLite database."""
    if not session_str or len(session_str) < 50:
        return False
    try:
        encrypted_token = encrypt_session_string(session_str)
        with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO telegram_linked_sessions 
                (user_id, phone_number, account_name, username, session_string, is_active, connected_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (user_id, phone.strip(), name.strip(), username.strip(), encrypted_token))
            conn.commit()
            logger.info(f"✅ Securely saved encrypted session for user {user_id} ({mask_phone_number(phone)})")
            return True
    except Exception as e:
        logger.error(f"[!] Error saving encrypted session for {user_id}: {e}")
        return False

def delete_linked_user_session(user_id: int) -> bool:
    """
    Deletes user session from database, disconnects any active clients,
    and cancels running jobs gracefully.
    """
    # 1. Disconnect active Telethon client instances for this user
    active_clients = _active_user_clients.pop(user_id, [])
    for c in active_clients:
        if c.is_connected():
            with suppress(Exception):
                asyncio.create_task(c.disconnect())

    # 2. Stop running jobs for this user gracefully
    running_tasks = _running_user_jobs.pop(user_id, [])
    for task in running_tasks:
        if not task.done():
            task.cancel()

    # 3. Remove row from database
    try:
        with sqlite3.connect(DB_PATH, timeout=30.0) as conn:
            conn.execute("DELETE FROM telegram_linked_sessions WHERE user_id = ?", (user_id,))
            conn.commit()
            logger.info(f"🗑️ Successfully deleted session and disconnected client for user {user_id}")
            return True
    except Exception as e:
        logger.error(f"[!] Error unlinking session for {user_id}: {e}")
        return False

def register_user_job_task(user_id: int, task: asyncio.Task):
    """Registers a background scan/clone task for graceful lifecycle management."""
    if user_id not in _running_user_jobs:
        _running_user_jobs[user_id] = []
    _running_user_jobs[user_id].append(task)

def get_all_active_linked_sessions() -> list:
    """Returns all active linked user sessions (metadata only, session decrypted on demand)."""
    try:
        with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT user_id, phone_number, account_name, username, connected_at FROM telegram_linked_sessions WHERE is_active = 1"
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception:
        return []

# ---------------------------------------------------------------------------
# Strict Isolation Telethon Client Builder
# ---------------------------------------------------------------------------

async def get_user_client(telegram_user_id: int) -> Optional[TelegramClient]:
    """
    Builds and returns an authorized Telethon client STRICTLY AND ONLY for the specified telegram_user_id.
    
    ISOLATION GUARANTEE:
    - Never falls back to another user's session.
    - Never allows another user or admin to borrow this session.
    - If unauthorized or expired, marks is_active = 0.
    """
    s_user = get_user_linked_session(telegram_user_id)
    if not s_user:
        return None

    try:
        c = TelegramClient(StringSession(s_user), API_ID, API_HASH)
        await c.connect()
        if await c.is_user_authorized():
            # Track active client for lifecycle management
            if telegram_user_id not in _active_user_clients:
                _active_user_clients[telegram_user_id] = []
            _active_user_clients[telegram_user_id].append(c)
            return c
        await c.disconnect()
        # Mark inactive if revoked in Telegram app
        with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
            conn.execute("UPDATE telegram_linked_sessions SET is_active = 0 WHERE user_id = ?", (telegram_user_id,))
            conn.commit()
    except Exception as e:
        logger.warning(f"Error connecting isolated user client for {telegram_user_id}: {e}")
    return None

async def get_vault_client_for_target(preferred_user_id: Optional[int] = None) -> Tuple[TelegramClient, str]:
    """
    Resolves an authorized MTProto Client.
    - If preferred_user_id is provided, strictly checks that user's linked account.
    - If preferred_user_id is None or failed, falls back ONLY to global system Master Session or Bot Token.
    - NEVER cross-shares arbitrary third-party user sessions.
    """
    # 1. Check preferred user's isolated session
    if preferred_user_id:
        user_c = await get_user_client(preferred_user_id)
        if user_c:
            return user_c, "user"

    # 2. Check global System Master StringSession
    s_str = get_persisted_session_string()
    if s_str:
        try:
            client = TelegramClient(StringSession(s_str), API_ID, API_HASH)
            await client.connect()
            if await client.is_user_authorized():
                return client, "user"
            await client.disconnect()
        except Exception as e:
            logger.warning(f"[!] Master StringSession connect warning: {e}")

    # 3. Extract from candidate system session files on disk
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

    # 4. Fallback to Bot Token Client
    bot_client = TelegramClient(StringSession(), API_ID, API_HASH)
    await bot_client.start(bot_token=BOT_TOKEN)
    return bot_client, "bot"

async def get_vault_client(preferred_type: str = "user") -> Tuple[TelegramClient, str]:
    """Default vault client resolver."""
    return await get_vault_client_for_target()

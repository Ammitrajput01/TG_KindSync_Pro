#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kind Doctor Autonomous Group & Topic Scanner Engine
Automatically scans all forum topics, individual topics, lectures, videos, and PDFs in any Telegram supergroup
and populates history_core.sqlite for instant /mainindex, /topicindex, and /find search!
"""

import os
import sys
import asyncio
import sqlite3
import shutil
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import suppress
from dotenv import load_dotenv

if hasattr(sys.stdout, "reconfigure"):
    with suppress(Exception):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    with suppress(Exception):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")
DB_PATH = ROOT_DIR / "history_core.sqlite"

API_ID = int(os.getenv("API_ID", "36193727") or 36193727)
API_HASH = os.getenv("API_HASH", "fef19b9b1434a3e66b009fd31053200b").strip()
BOT_TOKEN = os.getenv("DEVI_TELEGRAM_BOT_TOKEN", "").strip().strip("'").strip('"')

def get_db_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA busy_timeout=60000;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    return conn

def normalize_supergroup_chat_id(cid) -> int:
    """Converts any chat/channel entity ID or numeric string to Bot API supergroup ID (-100 prefix)."""
    try:
        raw_val = int(str(cid).strip())
    except (ValueError, TypeError):
        return 0
    s = str(abs(raw_val))
    if s.startswith("100"):
        return int(f"-{s}")
    else:
        return int(f"-100{s}")

def init_tables(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS telegram_group_topics (
            chat_id INTEGER,
            topic_id INTEGER,
            topic_title TEXT,
            topic_icon TEXT DEFAULT '📖',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(chat_id, topic_id)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS telegram_topic_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            topic_id INTEGER,
            item_order INTEGER DEFAULT 0,
            msg_id INTEGER,
            custom_link TEXT,
            title TEXT,
            item_type TEXT DEFAULT 'video',
            icon TEXT DEFAULT '🎬',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(chat_id, topic_id, msg_id)
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_topic_items_chat_topic ON telegram_topic_items(chat_id, topic_id)
    """)
    conn.commit()

async def get_authorized_client(preferred_user_id: Optional[int] = None):
    """Finds first available authorized user session via lock-free StringSession, linked sessions, or fallback."""
    try:
        from devi.operator.session_vault import get_vault_client_for_target
        client, client_type = await get_vault_client_for_target(preferred_user_id=preferred_user_id)
        return client, client_type, None
    except Exception as e:
        print(f"[!] Warning connecting to session vault: {e}. Fallback to bot token...")
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        bot_client = TelegramClient(StringSession(), API_ID, API_HASH)
        await bot_client.start(bot_token=BOT_TOKEN)
        return bot_client, "bot", None

def get_topic_icon(title: str) -> str:
    t_lower = title.lower()
    if "surgery" in t_lower:
        return "🔪"
    elif "prep" in t_lower or "notes" in t_lower or "pdf" in t_lower:
        return "📑"
    elif "sir" in t_lower or "dr" in t_lower:
        return "👨‍⚕️"
    elif "pharma" in t_lower or "med" in t_lower:
        return "💊"
    elif "micro" in t_lower or "patho" in t_lower:
        return "🔬"
    elif "cardio" in t_lower:
        return "❤️"
    elif "pedia" in t_lower or "obg" in t_lower:
        return "👶"
    elif "radio" in t_lower:
        return "🩻"
    elif "derma" in t_lower:
        return "🧴"
    elif "ophthal" in t_lower or "ent" in t_lower:
        return "👁️"
    return "📖"

async def scan_single_topic(client, peer, target_chat_id: int, topic_id: int, topic_title: Optional[str] = None) -> int:
    """Fast-harvests all media and notes under a single specific topic."""
    for attempt in range(5):
        try:
            with get_db_conn() as conn:
                init_tables(conn)
                
                # Register topic metadata if not present
                if topic_title:
                    icon = get_topic_icon(topic_title)
                    conn.execute("""
                        INSERT OR REPLACE INTO telegram_group_topics (chat_id, topic_id, topic_title, topic_icon, updated_at)
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (target_chat_id, topic_id, topic_title, icon))
                    conn.commit()

                topic_items_count = 0
                BOT_IGNORE_MARKERS = (
                    "auto-scan", "auto-pinned", "kind doctor", "topic study index", 
                    "topic index (part", "table of contents", "master topic directory", 
                    "index items add", "study index card", "auto-pin", "1-click auto-scan",
                    "topic #", "ke media files auto-scan"
                )
                try:
                    iter_kwargs = {"limit": None}
                    if topic_id and topic_id > 1:
                        iter_kwargs["reply_to"] = topic_id
                    async for msg in client.iter_messages(peer, **iter_kwargs):
                        if getattr(msg.sender, 'bot', False) or getattr(msg, 'via_bot_id', None):
                            continue

                        msg_text = (msg.message or "").strip()
                        if any(m in msg_text.lower() for m in BOT_IGNORE_MARKERS):
                            continue

                        title = None
                        icon = "🎬"
                        item_type = "video"

                        if msg.video:
                            title = msg.file.name if (msg.file and msg.file.name) else (msg_text.split("\n")[0] if msg_text else f"Lecture Video #{msg.id}")
                            icon = "🎬"
                            item_type = "video"
                        elif msg.document:
                            title = msg.file.name if (msg.file and msg.file.name) else (msg_text.split("\n")[0] if msg_text else f"Lecture Notes #{msg.id}")
                            icon = "📑"
                            item_type = "document"
                        elif msg.audio:
                            title = msg.file.name if (msg.file and msg.file.name) else (msg_text.split("\n")[0] if msg_text else f"Audio #{msg.id}")
                            icon = "🎧"
                            item_type = "audio"
                        elif msg_text and len(msg_text) > 3:
                            first_line = msg_text.split("\n")[0].strip()
                            if not first_line.startswith("/") and len(first_line) < 120:
                                if not any(m in first_line.lower() for m in BOT_IGNORE_MARKERS):
                                    title = first_line
                                    icon = "📌"
                                    item_type = "note"

                        if title:
                            clean = title
                            for ext in [".mp4", ".pdf", ".mkv", ".m4a", ".mp3", ".avi", ".epub"]:
                                clean = clean.replace(ext, "").replace(ext.upper(), "")
                            clean = clean.strip()
                            if any(m in clean.lower() for m in BOT_IGNORE_MARKERS):
                                continue
                            if clean:
                                conn.execute("""
                                    INSERT OR REPLACE INTO telegram_topic_items 
                                    (chat_id, topic_id, msg_id, title, icon, item_type)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, (target_chat_id, topic_id, msg.id, clean[:100], icon, item_type))
                                topic_items_count += 1
                                if topic_items_count % 50 == 0:
                                    conn.commit()

                    conn.commit()
                    print(f"[+] Harvested {topic_items_count} media items in Topic #{topic_id}")
                    return topic_items_count
                except Exception as ex:
                    conn.commit()
                    print(f"[!] Error scanning topic #{topic_id}: {ex}")
                    return topic_items_count
        except sqlite3.OperationalError as oe:
            if "locked" in str(oe).lower() and attempt < 4:
                await asyncio.sleep(1.0 + attempt * 0.5)
                continue
            print(f"[!] SQLite error on Topic #{topic_id}: {oe}")
            return 0
    return 0

async def harvest_all_messages(client, peer, target_chat_id: int) -> int:
    """Universally harvests all topics and media messages in a single continuous stream."""
    from telethon.tl.types import MessageActionTopicCreate, MessageActionTopicEdit
    BOT_IGNORE_MARKERS = (
        "auto-scan", "auto-pinned", "kind doctor", "topic study index", 
        "topic index (part", "table of contents", "master topic directory", 
        "index items add", "study index card", "auto-pin", "1-click auto-scan",
        "topic #", "ke media files auto-scan"
    )
    harvested_count = 0
    known_topics = {}
    
    # Load known topics from DB
    try:
        with get_db_conn() as conn:
            init_tables(conn)
            rows = conn.execute("SELECT topic_id, topic_title FROM telegram_group_topics WHERE chat_id = ?", (target_chat_id,)).fetchall()
            for r in rows:
                known_topics[r[0]] = r[1]
    except Exception as e:
        print(f"[!] Error loading topics: {e}")

    batch_items = []
    
    try:
        async for msg in client.iter_messages(peer, limit=None):
            # 1. Discover Forum Topics from action messages
            if getattr(msg, 'action', None):
                if isinstance(msg.action, MessageActionTopicCreate):
                    t_title = msg.action.title.strip()
                    known_topics[msg.id] = t_title
                    with get_db_conn() as conn:
                        conn.execute("""
                            INSERT OR REPLACE INTO telegram_group_topics (chat_id, topic_id, topic_title, topic_icon, updated_at)
                            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                        """, (target_chat_id, msg.id, t_title, get_topic_icon(t_title)))
                        conn.commit()
                elif isinstance(msg.action, MessageActionTopicEdit):
                    if getattr(msg.action, 'title', None):
                        t_title = msg.action.title.strip()
                        known_topics[msg.id] = t_title
                        with get_db_conn() as conn:
                            conn.execute("""
                                UPDATE telegram_group_topics SET topic_title = ?, topic_icon = ?, updated_at = CURRENT_TIMESTAMP
                                WHERE chat_id = ? AND topic_id = ?
                            """, (t_title, get_topic_icon(t_title), target_chat_id, msg.id))
                            conn.commit()

            # Skip bot messages or status notifications
            if getattr(msg.sender, 'bot', False) or getattr(msg, 'via_bot_id', None):
                continue

            msg_text = (msg.message or "").strip()
            if any(m in msg_text.lower() for m in BOT_IGNORE_MARKERS):
                continue

            title = None
            icon = "🎬"
            item_type = "video"

            if msg.video:
                title = msg.file.name if (msg.file and msg.file.name) else (msg_text.split("\n")[0] if msg_text else f"Lecture Video #{msg.id}")
                icon = "🎬"
                item_type = "video"
            elif msg.document:
                title = msg.file.name if (msg.file and msg.file.name) else (msg_text.split("\n")[0] if msg_text else f"Lecture Notes #{msg.id}")
                icon = "📑"
                item_type = "document"
            elif msg.audio:
                title = msg.file.name if (msg.file and msg.file.name) else (msg_text.split("\n")[0] if msg_text else f"Audio #{msg.id}")
                icon = "🎧"
                item_type = "audio"
            elif msg_text and len(msg_text) > 3:
                first_line = msg_text.split("\n")[0].strip()
                if not first_line.startswith("/") and len(first_line) < 120:
                    if not any(m in first_line.lower() for m in BOT_IGNORE_MARKERS):
                        title = first_line
                        icon = "📌"
                        item_type = "note"

            if title:
                clean = title
                for ext in [".mp4", ".pdf", ".mkv", ".m4a", ".mp3", ".avi", ".epub"]:
                    clean = clean.replace(ext, "").replace(ext.upper(), "")
                clean = clean.strip()
                if any(m in clean.lower() for m in BOT_IGNORE_MARKERS):
                    continue
                if clean:
                    # Resolve topic ID from reply header
                    msg_topic_id = getattr(msg.reply_to, 'reply_to_top_id', None) or getattr(msg.reply_to, 'reply_to_msg_id', None) or 1
                    
                    # Ensure topic exists in DB
                    if msg_topic_id not in known_topics:
                        t_name = f"Topic #{msg_topic_id}" if msg_topic_id > 1 else "General Study Materials"
                        known_topics[msg_topic_id] = t_name
                        with get_db_conn() as conn:
                            conn.execute("""
                                INSERT OR IGNORE INTO telegram_group_topics (chat_id, topic_id, topic_title, topic_icon, updated_at)
                                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                            """, (target_chat_id, msg_topic_id, t_name, get_topic_icon(t_name)))
                            conn.commit()

                    batch_items.append((target_chat_id, msg_topic_id, msg.id, clean[:100], icon, item_type))
                    harvested_count += 1
                    
                    if len(batch_items) >= 50:
                        with get_db_conn() as conn:
                            conn.executemany("""
                                INSERT OR REPLACE INTO telegram_topic_items 
                                (chat_id, topic_id, msg_id, title, icon, item_type)
                                VALUES (?, ?, ?, ?, ?, ?)
                            """, batch_items)
                            conn.commit()
                        batch_items = []

        if batch_items:
            with get_db_conn() as conn:
                conn.executemany("""
                    INSERT OR REPLACE INTO telegram_topic_items 
                    (chat_id, topic_id, msg_id, title, icon, item_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, batch_items)
                conn.commit()
    except Exception as ex:
        print(f"[!] Warning during full harvest stream: {ex}")

    print(f"[+] Total harvested {harvested_count} media items in group {target_chat_id}")
    return harvested_count

def extract_telegram_target(target_input: str):
    """Extracts invite hash, username, or numeric chat ID from input string."""
    raw = str(target_input).strip()
    m_inv = re.search(r'(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me)/(?:\+|joinchat/)([a-zA-Z0-9_-]+)', raw)
    if m_inv:
        return {"type": "invite_hash", "value": m_inv.group(1)}
    
    m_url = re.search(r'(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me)/([a-zA-Z0-9_]{4,})', raw)
    if m_url:
        return {"type": "username", "value": m_url.group(1)}
    
    if raw.startswith("@"):
        return {"type": "username", "value": raw.lstrip("@")}
        
    try:
        val = int(raw)
        return {"type": "chat_id", "value": val}
    except ValueError:
        return {"type": "raw", "value": raw}

async def scan_group(target_input, target_topic_id: Optional[int] = None, scan_messages: bool = True, preferred_user_id: Optional[int] = None):
    from telethon.tl.functions.messages import GetForumTopicsRequest, ImportChatInviteRequest, CheckChatInviteRequest
    from telethon.tl.functions.channels import JoinChannelRequest
    from telethon.errors import UserAlreadyParticipantError, InviteHashExpiredError, InviteHashInvalidError

    client, client_type, temp_sess_file = await get_authorized_client(preferred_user_id=preferred_user_id)
    try:
        target_info = extract_telegram_target(str(target_input))
        peer = None
        target_chat_id = None

        # 1. Handle Invite Links via User Client
        if target_info["type"] == "invite_hash":
            h_val = target_info["value"]
            if client_type == "user":
                try:
                    updates = await client(ImportChatInviteRequest(h_val))
                    if hasattr(updates, 'chats') and updates.chats:
                        target_chat_id = normalize_supergroup_chat_id(updates.chats[0].id)
                        peer = updates.chats[0]
                except UserAlreadyParticipantError:
                    pass
                except Exception as e:
                    print(f"[!] ImportChatInviteRequest error: {e}")

            if not peer:
                try:
                    check_res = await client(CheckChatInviteRequest(h_val))
                    chat_obj = getattr(check_res, 'chat', None)
                    if chat_obj:
                        target_chat_id = normalize_supergroup_chat_id(chat_obj.id)
                        peer = await client.get_input_entity(target_chat_id)
                except Exception as ex:
                    print(f"[!] CheckChatInviteRequest error: {ex}")

        # 2. Handle Username / Public links
        elif target_info["type"] == "username":
            u_val = target_info["value"]
            try:
                ent = await client.get_entity(u_val)
                peer = ent
                target_chat_id = normalize_supergroup_chat_id(ent.id)
            except Exception as e:
                print(f"[!] Username entity resolution error: {e}")

        # 3. Handle Numeric Chat IDs
        elif target_info["type"] == "chat_id":
            target_chat_id = normalize_supergroup_chat_id(target_info["value"])
            try:
                peer = await client.get_input_entity(target_chat_id)
            except Exception:
                pass

            if not peer:
                search_ids = [target_chat_id]
                raw_id = abs(target_chat_id)
                search_ids.extend([raw_id, -raw_id])
                s_raw = str(raw_id)
                if s_raw.startswith("100"):
                    with suppress(Exception):
                        short_id = int(s_raw[3:])
                        search_ids.extend([short_id, -short_id, int(f"-100{short_id}")])
                elif not str(target_chat_id).startswith("-100"):
                    with suppress(Exception):
                        search_ids.append(int(f"-100{raw_id}"))

                for sid in search_ids:
                    try:
                        peer = await client.get_input_entity(sid)
                        if peer: 
                            target_chat_id = normalize_supergroup_chat_id(sid)
                            break
                    except Exception:
                        pass
                    try:
                        ent = await client.get_entity(sid)
                        if ent:
                            peer = ent
                            target_chat_id = normalize_supergroup_chat_id(sid)
                            break
                    except Exception:
                        pass

            if not peer:
                try:
                    async for dialog in client.iter_dialogs(limit=None):
                        d_id = abs(dialog.id)
                        d_ent_id = abs(getattr(dialog.entity, 'id', 0))
                        if d_id in search_ids or d_ent_id in search_ids:
                            peer = dialog.input_entity
                            target_chat_id = normalize_supergroup_chat_id(dialog.id)
                            break
                except Exception:
                    pass

        if not peer and target_chat_id:
            try:
                peer = await client.get_entity(target_chat_id)
            except Exception as e:
                print(f"[!] Warning: Could not resolve peer for {target_chat_id}: {e}")
                return

        if not peer:
            print(f"[!] Fatal: Could not resolve peer for input '{target_input}'")
            return

        target_chat_id = normalize_supergroup_chat_id(target_chat_id)

        # Case 1: Targeted Single-Topic Scan (Lightning fast for /topicindex)
        if target_topic_id:
            print(f"[*] Scanning specific topic #{target_topic_id} in chat {target_chat_id}...")
            topic_title = None
            if client_type == "user":
                with suppress(Exception):
                    res = await client(GetForumTopicsRequest(
                        peer=peer,
                        offset_date=None,
                        offset_id=0,
                        offset_topic=0,
                        limit=100
                    ))
                    for t in getattr(res, 'topics', []):
                        if getattr(t, 'id', 0) == target_topic_id:
                            topic_title = getattr(t, 'title', None)
                            break
            count = await scan_single_topic(client, peer, target_chat_id, target_topic_id, topic_title=topic_title)
            print(f"SUCCESS: Scanned topic #{target_topic_id} ({count} items found)")
            return

        # Case 2: Full Group Scan
        total_items = await harvest_all_messages(client, peer, target_chat_id)
        print(f"SUCCESS: Scanned group {target_chat_id} ({total_items} items indexed)")
        return

    finally:
        with suppress(Exception):
            await client.disconnect()
        if temp_sess_file and Path(temp_sess_file).exists():
            with suppress(Exception):
                Path(temp_sess_file).unlink(missing_ok=True)

if __name__ == "__main__":
    raw_arg1 = sys.argv[1] if len(sys.argv) > 1 else "-1003912970546"
    target_topic = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else None
    preferred_user = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else None
    
    try:
        target_chat = int(raw_arg1)
    except ValueError:
        target_chat = raw_arg1

    asyncio.run(scan_group(target_chat, target_topic_id=target_topic, preferred_user_id=preferred_user))

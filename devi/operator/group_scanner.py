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
from pathlib import Path
from typing import Optional, List
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
                            # Also skip if clean text matches bot notification pattern
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

import re

def extract_telegram_target(target_input: str):
    """Extracts invite hash, username, or numeric chat ID from input string."""
    raw = str(target_input).strip()
    # Invite link (e.g. https://t.me/+hash or https://t.me/joinchat/hash)
    m_inv = re.search(r'(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me)/(?:\+|joinchat/)([a-zA-Z0-9_-]+)', raw)
    if m_inv:
        return {"type": "invite_hash", "value": m_inv.group(1)}
    
    # Public channel / group link (e.g. https://t.me/channel_name)
    m_url = re.search(r'(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me)/([a-zA-Z0-9_]{4,})', raw)
    if m_url:
        return {"type": "username", "value": m_url.group(1)}
    
    # Direct username (e.g. @channel_name)
    if raw.startswith("@"):
        return {"type": "username", "value": raw.lstrip("@")}
        
    # Numeric ID
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
                        ent = updates.chats[0]
                        peer = ent
                        target_chat_id = normalize_supergroup_chat_id(ent.id)
                        print(f"[+] Successfully joined group via invite link: id={target_chat_id}")
                except UserAlreadyParticipantError:
                    pass
                except Exception as e:
                    print(f"[!] Invite link join error: {e}")

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
            # Ensure proper supergroup prefix if needed
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

        # Ensure normalized negative ID for supergroups
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
        topics_list = []
        if client_type == "user":
            try:
                offset_topic = 0
                while True:
                    res = await client(GetForumTopicsRequest(
                        peer=peer,
                        offset_date=None,
                        offset_id=0,
                        offset_topic=offset_topic,
                        limit=100
                    ))
                    batch = getattr(res, 'topics', []) or []
                    if not batch:
                        break
                    topics_list.extend(batch)
                    if len(batch) < 100:
                        break
                    offset_topic = batch[-1].id
            except Exception as e:
                print(f"[!] Warning: GetForumTopicsRequest failed ({e})")

        with get_db_conn() as conn:
            init_tables(conn)

            # If topics_list was retrieved via MTProto user API
            if topics_list:
                for t in topics_list:
                    topic_title = getattr(t, 'title', None) or f"Topic #{t.id}"
                    topic_icon = get_topic_icon(topic_title)
                    conn.execute("""
                        INSERT OR REPLACE INTO telegram_group_topics (chat_id, topic_id, topic_title, topic_icon, updated_at)
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (target_chat_id, t.id, topic_title, topic_icon))
                conn.commit()
                print(f"STAGE 1 COMPLETE: {len(topics_list)} topics registered to DB!")

            # If topics_list is empty (e.g. running under bot token), read existing topics from DB
            if not topics_list:
                rows = conn.execute("SELECT topic_id, topic_title FROM telegram_group_topics WHERE chat_id = ?", (target_chat_id,)).fetchall()
                topics_list = [{"id": r[0], "title": r[1]} for r in rows]

        # STAGE 2: HARVEST MESSAGES (outside master connection to avoid long locks)
        if scan_messages:
            if not topics_list:
                # Normal group (no forum topics) - Register root topic 0 and harvest all messages
                default_title = "General Study Materials & Notes"
                with get_db_conn() as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO telegram_group_topics (chat_id, topic_id, topic_title, topic_icon, updated_at)
                        VALUES (?, 0, ?, '📚', CURRENT_TIMESTAMP)
                    """, (target_chat_id, default_title))
                    conn.commit()
                cnt = await scan_single_topic(client, peer, target_chat_id, 0, default_title)
                print(f"STAGE 2 COMPLETE: {cnt} items indexed in General Study Group!")
            else:
                total_harvested = 0
                for t in topics_list:
                    t_id = t.id if hasattr(t, 'id') else t["id"]
                    t_title = getattr(t, 'title', None) or (t.get("title") if isinstance(t, dict) else f"Topic #{t_id}")
                    if t_id == 1 and len(topics_list) > 1:
                        continue  # Skip root general topic if specific topics exist
                    cnt = await scan_single_topic(client, peer, target_chat_id, t_id, t_title)
                    total_harvested += cnt

                print(f"STAGE 2 COMPLETE: {total_harvested} total media items indexed across all topics!")

        print(f"SUCCESS: Scanned group {target_chat_id}")

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
    
    # Determine if arg1 is numeric or string (url/username)
    try:
        target_chat = int(raw_arg1)
    except ValueError:
        target_chat = raw_arg1

    asyncio.run(scan_group(target_chat, target_topic_id=target_topic, preferred_user_id=preferred_user))

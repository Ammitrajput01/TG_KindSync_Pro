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

def init_tables(conn: sqlite3.Connection):
    conn.execute("PRAGMA journal_mode=WAL;")
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

async def get_authorized_client():
    """Finds first available authorized user session (with lock bypass) or falls back to bot token."""
    from telethon import TelegramClient

    candidate_sessions = [
        "session_forwarder",
        "session_scanner",
        "session_account_9081",
        "session_account2",
        "session_account3",
        "session_user"
    ]
    # Add any other session files present in directory
    for p in ROOT_DIR.glob("*.session"):
        sname = p.stem
        if "bot" not in sname and "temp_scan" not in sname and sname not in candidate_sessions:
            candidate_sessions.append(sname)

    for sess_stem in candidate_sessions:
        sess_file = ROOT_DIR / f"{sess_stem}.session"
        if sess_file.exists() and sess_file.stat().st_size > 0:
            # 1. First try direct connect
            try:
                client = TelegramClient(str(ROOT_DIR / sess_stem), API_ID, API_HASH)
                await client.connect()
                if await client.is_user_authorized():
                    print(f"[*] Using authorized user session: {sess_stem}")
                    return client, "user", None
                await client.disconnect()
            except Exception as e:
                # 2. If locked by running bot/forwarder, create isolated ephemeral clone
                try:
                    temp_stem = f"temp_scan_{sess_stem}_{os.getpid()}"
                    temp_sess = ROOT_DIR / f"{temp_stem}.session"
                    shutil.copy2(sess_file, temp_sess)
                    
                    client = TelegramClient(str(ROOT_DIR / temp_stem), API_ID, API_HASH)
                    await client.connect()
                    if await client.is_user_authorized():
                        print(f"[*] Using authorized ephemeral session clone: {sess_stem}")
                        return client, "user", temp_sess
                    await client.disconnect()
                    if temp_sess.exists():
                        temp_sess.unlink(missing_ok=True)
                except Exception as inner_e:
                    print(f"[!] Session {sess_stem} fallback clone failed: {inner_e}")

    # Fallback to Bot Token Client
    print("[*] No authorized user session found. Initializing Bot Client...")
    bot_client = TelegramClient(str(ROOT_DIR / "session_bot_scanner"), API_ID, API_HASH)
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
    with sqlite3.connect(DB_PATH) as conn:
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
        try:
            async for msg in client.iter_messages(peer, reply_to=topic_id, limit=None):
                title = None
                icon = "🎬"
                item_type = "video"

                if msg.video:
                    title = msg.file.name if (msg.file and msg.file.name) else (msg.message.split("\n")[0] if msg.message else f"Lecture Video #{msg.id}")
                    icon = "🎬"
                    item_type = "video"
                elif msg.document:
                    title = msg.file.name if (msg.file and msg.file.name) else (msg.message.split("\n")[0] if msg.message else f"Lecture Notes #{msg.id}")
                    icon = "📑"
                    item_type = "document"
                elif msg.audio:
                    title = msg.file.name if (msg.file and msg.file.name) else (msg.message.split("\n")[0] if msg.message else f"Audio #{msg.id}")
                    icon = "🎧"
                    item_type = "audio"
                elif msg.message and len(msg.message.strip()) > 2:
                    first_line = msg.message.strip().split("\n")[0]
                    if not first_line.startswith("/") and len(first_line) < 120:
                        title = first_line
                        icon = "📌"
                        item_type = "note"

                if title:
                    clean = title
                    for ext in [".mp4", ".pdf", ".mkv", ".m4a", ".mp3", ".avi", ".epub"]:
                        clean = clean.replace(ext, "").replace(ext.upper(), "")
                    clean = clean.strip()
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

async def scan_group(target_chat_id: int, target_topic_id: Optional[int] = None, scan_messages: bool = True):
    from telethon.tl.functions.messages import GetForumTopicsRequest

    client, client_type, temp_sess_file = await get_authorized_client()
    try:
        peer = None
        # Try direct resolution
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

            for sid in search_ids:
                try:
                    peer = await client.get_input_entity(sid)
                    if peer: break
                except Exception:
                    pass
                try:
                    ent = await client.get_entity(sid)
                    if ent:
                        peer = ent
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
                        break
            except Exception:
                pass

        if not peer:
            try:
                peer = await client.get_entity(target_chat_id)
            except Exception as e:
                print(f"[!] Warning: Could not resolve peer for {target_chat_id}: {e}")
                return

        # Case 1: Targeted Single-Topic Scan (Lightning fast for /topicindex)
        if target_topic_id:
            print(f"[*] Scanning specific topic #{target_topic_id} in chat {target_chat_id}...")
            # Try to fetch topic title via GetForumTopicsRequest if user client
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

        with sqlite3.connect(DB_PATH) as conn:
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

            # STAGE 2: HARVEST MESSAGES
            if scan_messages and topics_list:
                total_harvested = 0
                for t in topics_list:
                    t_id = t.id if hasattr(t, 'id') else t["id"]
                    t_title = getattr(t, 'title', None) or (t.get("title") if isinstance(t, dict) else f"Topic #{t_id}")
                    if t_id == 1:
                        continue  # Skip root general topic
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
    target_chat = int(sys.argv[1]) if len(sys.argv) > 1 else -1003912970546
    target_topic = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else None
    asyncio.run(scan_group(target_chat, target_topic))

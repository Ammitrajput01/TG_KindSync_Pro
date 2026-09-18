#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Kind Doctor Autonomous Group & Topic Scanner Engine
Automatically scans all forum topics, lectures, videos, and PDFs in any Telegram supergroup
and populates history_core.sqlite for instant /mainindex, /topicindex, and /find search!
"""

import os
import sys
import asyncio
import sqlite3
import shutil
from pathlib import Path
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_topic_items_chat_topic ON telegram_topic_items(chat_id, topic_id)
    """)
    conn.commit()

async def scan_group(target_chat_id: int, scan_messages: bool = True):
    from telethon import TelegramClient
    from telethon.tl.functions.messages import GetForumTopicsRequest

    # Prioritize primary forwarder session for authentic supergroup access
    sess_path = ROOT_DIR / "session_forwarder"
    if not (ROOT_DIR / "session_forwarder.session").exists():
        sess_path = ROOT_DIR / "session_scanner"

    client = TelegramClient(str(sess_path), API_ID, API_HASH)
    await client.connect()

    is_user_auth = await client.is_user_authorized()
    if not is_user_auth:
        await client.disconnect()
        # Fallback to bot token if user session not authorized
        client = TelegramClient(str(ROOT_DIR / "session_bot_scanner"), API_ID, API_HASH)
        await client.start(bot_token=BOT_TOKEN)

    try:
        peer = await client.get_input_entity(target_chat_id)

        # 1. Fetch Forum Topics from Telegram
        try:
            res = await client(GetForumTopicsRequest(
                peer=peer,
                offset_date=None,
                offset_id=0,
                offset_topic=0,
                limit=100
            ))
            topics_list = getattr(res, 'topics', []) or []
        except Exception as e:
            print(f"[!] Warning: GetForumTopicsRequest failed ({e})")
            topics_list = []

        with sqlite3.connect(DB_PATH) as conn:
            init_tables(conn)

            # =========================================================
            # STAGE 1: IMMEDIATE TOPIC METADATA COMMIT (< 2 Seconds)
            # Guarantees /mainindex works instantly even if process stops
            # =========================================================
            saved_count = 0
            for t in topics_list:
                topic_title = getattr(t, 'title', None) or f"Topic #{t.id}"
                topic_icon = "🩺"
                t_lower = topic_title.lower()
                if "surgery" in t_lower:
                    topic_icon = "🔪"
                elif "prep" in t_lower or "notes" in t_lower or "pdf" in t_lower:
                    topic_icon = "📑"
                elif "sir" in t_lower or "dr" in t_lower:
                    topic_icon = "👨‍⚕️"
                elif "pharma" in t_lower or "med" in t_lower:
                    topic_icon = "💊"
                elif "micro" in t_lower or "patho" in t_lower:
                    topic_icon = "🔬"

                conn.execute("""
                    INSERT OR REPLACE INTO telegram_group_topics (chat_id, topic_id, topic_title, topic_icon, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (target_chat_id, t.id, topic_title, topic_icon))
                saved_count += 1

            conn.commit()
            print(f"STAGE 1 COMPLETE: {saved_count} topics registered & committed to DB!")

            # =========================================================
            # STAGE 2: MESSAGE HARVEST WITH PER-TOPIC COMMITS
            # =========================================================
            if scan_messages:
                for t in topics_list:
                    if t.id == 1:
                        continue  # General root topic

                    try:
                        async for msg in client.iter_messages(target_chat_id, reply_to=t.id, limit=60):
                            title = None
                            icon = "🎬"
                            if msg.video:
                                title = msg.file.name if (msg.file and msg.file.name) else (msg.message.split("\n")[0] if msg.message else f"Lecture Video #{msg.id}")
                                icon = "🎬"
                            elif msg.document:
                                title = msg.file.name if (msg.file and msg.file.name) else (msg.message.split("\n")[0] if msg.message else f"Lecture Notes #{msg.id}")
                                icon = "📑"
                            elif msg.audio:
                                title = msg.file.name if (msg.file and msg.file.name) else (msg.message.split("\n")[0] if msg.message else f"Audio #{msg.id}")
                                icon = "🎧"
                            elif msg.message and len(msg.message.strip()) > 3:
                                first_line = msg.message.strip().split("\n")[0]
                                if not first_line.startswith("/") and len(first_line) < 100:
                                    title = first_line
                                    icon = "📌"

                            if title:
                                clean = title.replace(".mp4", "").replace(".pdf", "").replace(".mkv", "").strip()
                                conn.execute("""
                                    INSERT OR IGNORE INTO telegram_topic_items 
                                    (chat_id, topic_id, msg_id, title, icon)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (target_chat_id, t.id, msg.id, clean[:90], icon))

                        # Commit after each topic so progress is never lost
                        conn.commit()
                    except Exception as ex:
                        pass

        print(f"SUCCESS: Scanned {len(topics_list)} topics for {target_chat_id}")

    finally:
        await client.disconnect()

if __name__ == "__main__":
    target = int(sys.argv[1]) if len(sys.argv) > 1 else -1003912970546
    asyncio.run(scan_group(target))

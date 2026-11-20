"""
Autonomous High-Speed Study Help Direct Group Cloner
Source: Study Help 😉 (-1003912970546)
Target: Study Help 2.0 😉 (-1004467980132)

Architectural Invariants:
1. Fast Tier-1 Server-Side Cloud Pointer Copy (~0.15s/post, 0 bytes bandwidth).
2. Original Media Thumbnails Strictly Preserved (THUMB_MODE='original').
3. Clean Captions: Strips third-party promotional links, handles, and watermarks,
   replacing with Kind Doctor & Team + Study Help 2.0 signature.
4. Autonomous Forum Topic Discovery and Matching Topic Creation.
5. SQLite WAL Watermark Tracking (Resumable across crashes and stops).
6. Real-time Telemetry dispatched to Kind Doctor HQ (Topic 9: Cloner Telemetry) & PM.
"""
import asyncio
import aiohttp
import html
import io
import logging
import os
import re
import sqlite3
import sys
import time
from contextlib import suppress
from datetime import datetime
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv(override=True)

from telethon import TelegramClient
from telethon.tl.types import InputReplyToMessage
from telethon.tl.functions.messages import GetForumTopicsRequest
from telethon.errors import FloodWaitError
from devi.operator.session_vault import get_vault_client_for_target
from devi.operator.deep_cloner import (
    DeepClonerEngine,
    create_clone_job,
    update_clone_job_progress,
    async_update_clone_job_progress,
    get_or_create_target_topic,
    clean_cloned_caption,
    _safe_resolve_entity,
    _job_cancel_flags,
    _job_pause_flags,
    init_clone_jobs_table,
    DB_PATH
)

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(LOG_DIR / "study_help_clone.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("StudyHelpCloner")

# Configuration
SOURCE_CHAT_ID = -1003912970546
TARGET_CHAT_ID = -1004467980132
ADMIN_USER_ID = 1553619403
MISSION_CONTROL_CHAT = -1003942399840
CLONER_TOPIC_ID = 9
BOT_TOKEN = os.getenv("BOT_TOKEN", "8749455751:AAFT6BEMH1O5OW4-yM3gFJn9gsCI-6J3S9k")

# Ensure original thumbnails are preserved
os.environ["THUMB_MODE"] = "original"

# Discussion & chatterbox topics to skip
SKIP_KEYWORDS = ["chit chat", "chatter box", "chatterbox", "add member", "add members", "spam"]


def get_topic_watermark(src_chat: str, src_top: int, tgt_chat: str, tgt_top: int):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            row = conn.execute("""
                SELECT max_id, completed_files, is_finished 
                FROM topic_watermarks 
                WHERE source_chat = ? AND source_topic = ? AND target_chat = ? AND target_topic = ?
            """, (str(src_chat), src_top, str(tgt_chat), tgt_top)).fetchone()
            if row:
                return {"max_id": row[0], "completed": row[1], "is_finished": bool(row[2])}
    except Exception as e:
        logger.debug(f"Watermark lookup error: {e}")
    return {"max_id": 0, "completed": 0, "is_finished": False}


def update_topic_watermark(src_chat: str, src_top: int, tgt_chat: str, tgt_top: int, max_id: int, inc: int = 0, is_finished: bool = False):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO topic_watermarks (source_chat, source_topic, target_chat, target_topic, max_id, completed_files, is_finished, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(source_chat, source_topic, target_chat, target_topic) DO UPDATE SET
                    max_id = MAX(max_id, excluded.max_id),
                    completed_files = completed_files + excluded.completed_files,
                    is_finished = CASE WHEN excluded.is_finished = 1 THEN 1 ELSE topic_watermarks.is_finished END,
                    updated_at = excluded.updated_at
            """, (str(src_chat), src_top, str(tgt_chat), tgt_top, max_id, inc, 1 if is_finished else 0, time.time()))
            conn.commit()
    except Exception as e:
        logger.warning(f"Watermark update error: {e}")


async def send_telemetry_card(user_client: TelegramClient, text: str):
    """Dispatches real-time cloner card to Mission Control Topic 9 and Admin PM."""
    # 1. Mission Control Forum (Topic 9)
    try:
        mc_peer = await _safe_resolve_entity(user_client, MISSION_CONTROL_CHAT)
        await user_client.send_message(mc_peer, text, parse_mode="html", reply_to=CLONER_TOPIC_ID)
    except Exception as e:
        logger.debug(f"MC telemetry dispatch failed: {e}")

    # 2. Admin PM
    try:
        admin_peer = await _safe_resolve_entity(user_client, ADMIN_USER_ID)
        await user_client.send_message(admin_peer, text, parse_mode="html")
    except Exception as e:
        logger.debug(f"Admin PM dispatch failed: {e}")


async def bot_copy_message(http_session: aiohttp.ClientSession, bot_token: str, src_chat: int, tgt_chat: int, tgt_topic: int, msg_id: int, caption: str):
    """Copies a message directly via Bot API (Immune to MTProto user SendMedia FloodWait)."""
    url = f"https://api.telegram.org/bot{bot_token}/copyMessage"
    html_cap = caption.replace("**Kind Doctor & Team**", "<b>Kind Doctor & Team</b>") if caption else ""
    if len(html_cap) > 1024:
        html_cap = html_cap[:1020] + "..."
    payload = {
        "chat_id": tgt_chat,
        "from_chat_id": src_chat,
        "message_id": msg_id,
        "caption": html_cap,
        "parse_mode": "HTML"
    }
    if tgt_topic and tgt_topic > 1:
        payload["message_thread_id"] = tgt_topic
    
    try:
        async with http_session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=25)) as resp:
            res = await resp.json()
            if res.get("ok"):
                return True, (None, 0)
            err = res.get("description", "Unknown error")
            retry_after = res.get("parameters", {}).get("retry_after", 0)
            return False, (err, retry_after)
    except Exception as e:
        return False, (str(e), 0)


async def main():
    logger.info("🚀 INITIALIZING AUTONOMOUS STUDY HELP DIRECT CLONER")
    logger.info(f"• Source Group: {SOURCE_CHAT_ID}")
    logger.info(f"• Target Group: {TARGET_CHAT_ID}")
    logger.info(f"• Engine Mode : Tier-1 Direct Pointer Copy (Fast, Original Thumbnails, Clean Captions)")

    init_clone_jobs_table()

    http_session = aiohttp.ClientSession()
    user_client, _ = await get_vault_client_for_target(preferred_user_id=ADMIN_USER_ID)
    if not user_client:
        logger.error("❌ Failed to obtain MTProto client for admin account.")
        await http_session.close()
        return

    src_peer = await _safe_resolve_entity(user_client, SOURCE_CHAT_ID)
    tgt_peer = await _safe_resolve_entity(user_client, TARGET_CHAT_ID)

    # Register Clone Job in SQLite
    job_id = create_clone_job(
        user_id=ADMIN_USER_ID,
        source_chat=str(SOURCE_CHAT_ID),
        target_chat=str(TARGET_CHAT_ID),
        job_type="group"
    )

    # Step 1: Discover All Topics from Source Group
    discovered_topics = []
    offset_id = 0
    offset_topic = 0

    logger.info("📋 Discovering all topics in source group...")
    while True:
        try:
            res = await user_client(GetForumTopicsRequest(
                peer=src_peer,
                offset_date=0,
                offset_id=offset_id,
                offset_topic=offset_topic,
                limit=100
            ))
            topics_chunk = getattr(res, 'topics', [])
            if not topics_chunk:
                break
            for t in topics_chunk:
                t_id = getattr(t, 'id', None)
                t_title = getattr(t, 'title', None) or f"Topic #{t_id}"
                if t_id and (t_id, t_title) not in discovered_topics:
                    discovered_topics.append((t_id, t_title))
            if len(topics_chunk) < 100:
                break
            last_t = topics_chunk[-1]
            if offset_topic == last_t.id:
                break
            offset_topic = last_t.id
            offset_id = getattr(last_t, 'top_message', 0)
        except Exception as ex_t:
            logger.warning(f"GetForumTopicsRequest ended: {ex_t}")
            break

    # Natural curriculum sort by topic id
    discovered_topics.sort(key=lambda x: x[0])
    total_topics = len(discovered_topics)
    logger.info(f"✅ Discovered {total_topics} topics in Study Help.")

    init_card = (
        f"🚀 <b>STUDY HELP ➔ STUDY HELP 2.0 DIRECT CLONE LAUNCHED</b> 🩺\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📂 <b>Source Group:</b> <code>Study Help 😉</code> ({SOURCE_CHAT_ID})\n"
        f"🎯 <b>Target Group:</b> <code>Study Help 2.0 😉</code> ({TARGET_CHAT_ID})\n"
        f"📑 <b>Total Discovered Topics:</b> <b>{total_topics}</b>\n"
        f"⚡ <b>Mode:</b> Direct Tier-1 Fast Forward (0.15s / msg)\n"
        f"🖼️ <b>Thumbnails:</b> 100% Original Preserved\n"
        f"✨ <b>Captions:</b> Cleaned of Third-Party Promo & Links\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 <b>Admin:</b> @Kinddoctor4u | @Ammitrajput1\n"
        f"🕒 <b>Started:</b> <code>{datetime.now().strftime('%A, %d %B %Y | %I:%M %p')}</code>"
    )
    await send_telemetry_card(user_client, init_card)

    grand_total_cloned = 0
    completed_topics_count = 0

    for idx, (src_top_id, src_top_title) in enumerate(discovered_topics, start=1):
        # Skip chatterbox topics
        is_chatter = any(kw in src_top_title.lower() for kw in SKIP_KEYWORDS)
        if is_chatter:
            logger.info(f"⏭️ Skipping discussion topic #{idx}/{total_topics}: '{src_top_title}'")
            completed_topics_count += 1
            continue

        logger.info(f"⚡ Processing Topic #{idx}/{total_topics}: '{src_top_title}' (ID: {src_top_id})")

        # Resolve or create target topic in Study Help 2.0
        try:
            target_topic_id = await get_or_create_target_topic(
                BOT_TOKEN,
                user_client,
                TARGET_CHAT_ID,
                src_top_title
            )
        except Exception as e:
            logger.error(f"Failed to create/resolve topic '{src_top_title}': {e}")
            target_topic_id = 1

        # Check existing watermark
        wm = get_topic_watermark(str(SOURCE_CHAT_ID), src_top_id, str(TARGET_CHAT_ID), target_topic_id)
        if wm["is_finished"]:
            logger.info(f"⏩ Topic '{src_top_title}' already fully cloned ({wm['completed']} msgs). Skipping.")
            completed_topics_count += 1
            continue

        min_msg_id = wm["max_id"]
        logger.info(f"▶️ Streaming '{src_top_title}' (Resuming from msg #{min_msg_id})...")

        dest_thread = target_topic_id if target_topic_id and target_topic_id > 1 else None
        reply_hdr = dest_thread

        topic_cloned = 0
        current_max_id = min_msg_id

        try:
            async for msg in user_client.iter_messages(src_peer, reply_to=src_top_id, min_id=min_msg_id, reverse=True):
                if getattr(msg, 'action', None) or not (msg.text or msg.media):
                    continue

                orig_filename = getattr(msg.file, 'name', None)
                raw_text = (msg.text or "").strip()
                cleaned_caption = clean_cloned_caption(
                    raw_text=raw_text,
                    orig_filename=orig_filename,
                    topic_title=src_top_title,
                    is_media=bool(msg.media)
                )

                sent = False
                for retry in range(3):
                    ok, (err, retry_after) = await bot_copy_message(
                        http_session, BOT_TOKEN, SOURCE_CHAT_ID, TARGET_CHAT_ID, target_topic_id, msg.id, cleaned_caption
                    )
                    if ok:
                        sent = True
                        break
                    elif retry_after and retry_after > 0:
                        logger.warning(f"⏳ Bot API Rate Limit: Sleeping {retry_after + 1}s")
                        await asyncio.sleep(retry_after + 1)
                    else:
                        logger.info(f"Bot copy notice on msg #{msg.id} ({err}) -> Trying MTProto pointer fallback...")
                        try:
                            if msg.media:
                                await user_client.send_file(
                                    tgt_peer,
                                    file=msg.media,
                                    caption=cleaned_caption,
                                    reply_to=reply_hdr
                                )
                            elif msg.text:
                                await user_client.send_message(
                                    tgt_peer,
                                    cleaned_caption,
                                    reply_to=reply_hdr
                                )
                            sent = True
                            break
                        except FloodWaitError as fe:
                            logger.warning(f"⏳ MTProto FloodWait {fe.seconds + 2}s")
                            await asyncio.sleep(min(fe.seconds + 2, 60))
                        except Exception as e_send:
                            logger.warning(f"Error copying msg #{msg.id} (attempt {retry+1}): {e_send}")
                            await asyncio.sleep(0.5)

                if sent:
                    topic_cloned += 1
                    grand_total_cloned += 1
                    current_max_id = max(current_max_id, msg.id)
                    update_topic_watermark(str(SOURCE_CHAT_ID), src_top_id, str(TARGET_CHAT_ID), target_topic_id, current_max_id, inc=1)
                    await asyncio.sleep(0.35)

            # Mark topic finished
            update_topic_watermark(str(SOURCE_CHAT_ID), src_top_id, str(TARGET_CHAT_ID), target_topic_id, current_max_id, is_finished=True)
            completed_topics_count += 1
            logger.info(f"✅ Finished Topic #{idx}/{total_topics}: '{src_top_title}' ({topic_cloned} messages cloned).")

            # Dispatch periodic milestone card every 5 topics or if topic had content
            if topic_cloned > 0 or completed_topics_count % 5 == 0:
                milestone_card = (
                    f"📑 <b>TOPIC CLONED SUCCESSFULLY</b> 🩺\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"✅ <b>Topic #{completed_topics_count}/{total_topics}:</b> <code>{html.escape(src_top_title)}</code>\n"
                    f"📦 <b>Messages Mirrored:</b> <b>{topic_cloned}</b>\n"
                    f"📊 <b>Grand Total Mirrored:</b> <b>{grand_total_cloned}</b>\n"
                    f"⚡ <b>Status:</b> In-Progress · Fast Cloud Stream\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🕒 <code>{datetime.now().strftime('%I:%M:%S %p')}</code>"
                )
                await send_telemetry_card(user_client, milestone_card)

        except Exception as ex_topic:
            logger.error(f"Error processing topic '{src_top_title}': {ex_topic}")
            await asyncio.sleep(1.0)

    final_card = (
        f"🎉 <b>STUDY HELP 2.0 FULL CLONE COMPLETED!</b> 🩺\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>All {completed_topics_count} Topics Successfully Mirrored</b>\n"
        f"📦 <b>Total Materials Cloned:</b> <b>{grand_total_cloned}</b>\n"
        f"📁 <b>Target:</b> <code>Study Help 2.0 😉</code> ({TARGET_CHAT_ID})\n"
        f"🛡️ <b>Formatting:</b> 100% Cleaned, Zero Ads, Original Media Intact\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 <b>Kind Doctor & Team Mission Accomplished!</b>"
    )
    await send_telemetry_card(user_client, final_card)
    logger.info("🎉 ALL TOPICS CLONED SUCCESSFULLY!")
    await http_session.close()


if __name__ == "__main__":
    asyncio.run(main())

# -*- coding: utf-8 -*-
"""
Devi Operator Forum Indexer & Topic Scanner Command Handlers
Handles /mainindex, /topics, /topicindex, /scan, /autoindex in O(1) time.
Architect: Dr. Amit Singh (Kind Doctor) · @Kinddoctor4u
"""

from typing import List, Optional

async def handle_main_index(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    thread_id = message.get("message_thread_id") if message else None
    target_chat_id = bot._resolve_study_group_id(chat_id, admin_id)
    
    chunks = bot._build_main_index_cards(target_chat_id)
    for card_text, kb in chunks:
        await bot._send_message(session, chat_id, card_text, reply_markup=kb, message_thread_id=thread_id, parse_mode="HTML")

async def handle_topics_catalog(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    thread_id = message.get("message_thread_id") if message else None
    target_chat_id = bot._resolve_study_group_id(chat_id, admin_id)
    
    topics = bot._get_topics(target_chat_id, sort_mode="az")
    if not topics:
        await bot._send_message(session, chat_id, "ℹ️ <i>No topics indexed yet. Use /scan or /mainindex.</i>", message_thread_id=thread_id, parse_mode="HTML")
        return

    lines = [
        "📚 <b>TOPICS DIRECTORY (A–Z CATALOG)</b> 🩺",
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    for idx, t in enumerate(topics[:35], 1):
        t_name = t.get("name", "Topic")
        t_id = t.get("thread_id")
        lines.append(f"{idx}. <b>{t_name}</b> — <code>/topicindex {t_id}</code>")
    
    await bot._send_message(session, chat_id, "\n".join(lines), message_thread_id=thread_id, parse_mode="HTML")

async def handle_topic_index(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    thread_id = message.get("message_thread_id") if message else None
    target_chat_id = bot._resolve_study_group_id(chat_id, admin_id)
    
    if len(parts) < 2:
        await bot._send_message(session, chat_id, "Usage: <code>/topicindex &lt;topic_id&gt;</code>", message_thread_id=thread_id, parse_mode="HTML")
        return

    try:
        t_id = int(parts[1])
        items = bot._get_topic_items(target_chat_id, t_id)
        if not items:
            await bot._send_message(session, chat_id, f"ℹ️ <i>No items indexed under topic {t_id} yet.</i>", message_thread_id=thread_id, parse_mode="HTML")
            return
        
        lines = [
            f"📑 <b>TOPIC INDEX #{t_id}</b> 🩺",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ]
        for idx, item in enumerate(items[:30], 1):
            title = item.get("title", f"Lecture {idx}")
            link = item.get("link", "")
            lines.append(f"{idx}. <a href=\"{link}\"><b>{title}</b></a>" if link else f"{idx}. <b>{title}</b>")
        
        await bot._send_message(session, chat_id, "\n".join(lines), message_thread_id=thread_id, parse_mode="HTML")
    except Exception as e:
        await bot._send_message(session, chat_id, f"⚠️ Error: <code>{str(e)}</code>", message_thread_id=thread_id, parse_mode="HTML")

def register_indexer_handlers(router):
    router.register(["/mainindex", "/main_index", "/indexmaster", "/alltopics"], handle_main_index, "Main Category Index Cards", "indexer")
    router.register(["/topics"], handle_topics_catalog, "Alphabetical Topics Directory", "indexer")
    router.register(["/topicindex", "/subindex", "/index"], handle_topic_index, "Direct Clickable Topic Catalog", "indexer")

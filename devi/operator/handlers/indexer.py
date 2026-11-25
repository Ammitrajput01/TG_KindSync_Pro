# -*- coding: utf-8 -*-
"""
Devi Operator Forum Indexer & Topic Scanner Command Handlers
Handles /mainindex, /topics, /topicindex, /scan, /autoindex in O(1) time.
Architect: Dr. Amit Singh (Kind Doctor) · @Kinddoctor4u
"""

import html
from typing import List, Optional

async def handle_main_index(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    """Unpacks (cards, reply_markup) properly if invoked directly."""
    thread_id = message.get("message_thread_id") if message else None
    target_chat_id = bot._resolve_study_group_id(chat_id, admin_id)
    
    cards, reply_markup = bot._build_main_index_cards(target_chat_id)
    if not cards:
        return None
    for idx, card_text in enumerate(cards):
        kb = reply_markup if idx == len(cards) - 1 or idx == 0 else None
        await bot._send_message(session, chat_id, card_text, reply_markup=kb, message_thread_id=thread_id, parse_mode="HTML")
    return True

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
    for idx, t in enumerate(topics[:50], 1):
        t_name = html.escape(str(t.get("topic_title") or t.get("name") or "Topic"))
        t_id = t.get("topic_id") or t.get("thread_id")
        lines.append(f"{idx}. <b>{t_name}</b> — <code>/topicindex {t_id}</code>")
    
    await bot._send_message(session, chat_id, "\n".join(lines), message_thread_id=thread_id, parse_mode="HTML")

async def handle_topic_index(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    thread_id = message.get("message_thread_id") if message else None
    target_chat_id = bot._resolve_study_group_id(chat_id, admin_id)
    
    t_id = thread_id
    for p in parts[1:]:
        if p.isdigit():
            t_id = int(p)
            break

    if not t_id:
        return await handle_main_index(bot, session, chat_id, admin_id, "/mainindex", message, ["/mainindex"])

    try:
        items = bot._get_topic_items(target_chat_id, int(t_id))
        if not items:
            return None
        
        clean_chat_id = str(target_chat_id).replace("-100", "").replace("-", "").lstrip("@")
        lines = [
            f"📑 <b>TOPIC INDEX #{t_id}</b> 🩺",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ]
        for idx, item in enumerate(items[:35], 1):
            title = html.escape(str(item.get("title") or f"Lecture {idx}"))
            m_id = item.get("msg_id")
            link = item.get("custom_link") or item.get("link") or (
                f"https://t.me/c/{clean_chat_id}/{t_id}/{m_id}" if (m_id and clean_chat_id.isdigit()) else ""
            )
            lines.append(f"{idx}. <a href=\"{link}\"><b>{title}</b></a>" if link else f"{idx}. <b>{title}</b>")
        
        await bot._send_message(session, chat_id, "\n".join(lines), message_thread_id=thread_id, parse_mode="HTML", disable_web_page_preview=True)
        return True
    except Exception as e:
        await bot._send_message(session, chat_id, f"⚠️ Error: <code>{html.escape(str(e))}</code>", message_thread_id=thread_id, parse_mode="HTML")
        return True

def register_indexer_handlers(router):
    # Only register /topics on fast-path; /mainindex, /topicindex, /index fall through
    # to DeviTelegramBot's full auto-scan + auto-pin + pagination handlers.
    router.register(["/topics"], handle_topics_catalog, "Alphabetical Topics Directory", "indexer")

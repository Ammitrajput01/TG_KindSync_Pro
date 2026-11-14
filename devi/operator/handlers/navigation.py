# -*- coding: utf-8 -*-
"""
Devi Operator Navigation & Identity Command Handlers
Handles /start, /help, /menu, /mode, /support, /id, /myid, /about, /botinfo
Architect: Dr. Amit Singh (Kind Doctor) · @Kinddoctor4u
"""

import html
from typing import List, Optional

async def handle_start_or_menu(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    cmd = parts[0].lower().split("@")[0]
    thread_id = message.get("message_thread_id") if message else None

    if cmd == "/help" and len(parts) > 1:
        subcat = parts[1].lower().strip()
        card_text, kb = bot._build_interactive_help_card(subcat, is_admin=bot.is_admin(admin_id))
        await bot._send_message(session, chat_id, card_text, reply_markup=kb, message_thread_id=thread_id, parse_mode="HTML")
        return

    await bot._render_main_menu(session, chat_id, admin_id, thread_id=thread_id)

async def handle_support(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    thread_id = message.get("message_thread_id") if message else None
    support_card = (
        f"👨‍⚕️ **Kind Doctor Direct Desk & Live Line** 🩺\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Agar aapko study material, notes, batches join karne ya kisi medical topic par guidance chahiye:\n\n"
        f"👉 **Bas yahi par apna message, doubt ya request type karke send kar dijiye!**\n\n"
        f"🔒 **100% Private & Direct:**\n"
        f"• Aapka message seedha **Kind Doctor** ke private desk par securely deliver hota hai.\n"
        f"• Doctor jaise hi message dekhenge, aapko unka reply isi bot ke through mil jayega.\n"
        f"• Kisi phone number ya external application ki zaroorat nahi hai! 🤍"
    )
    await bot._send_message(session, chat_id, support_card, message_thread_id=thread_id)

async def handle_id(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    thread_id = message.get("message_thread_id") if message else None
    reply_to = message.get("reply_to_message") if message else None
    lines = [
        f"🆔 **Telegram Identity Card** 🩺",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ]
    if reply_to and reply_to.get("from"):
        target_u = reply_to["from"]
        lines.append(f"• **Target User ID**: `{target_u.get('id')}` ({target_u.get('first_name', 'User')})")
        if target_u.get("username"):
            lines.append(f"• **Target Username**: @{target_u.get('username')}")
    
    lines.append(f"• **Your Permanent ID**: `{admin_id}`")
    lines.append(f"• **Current Chat ID**: `{chat_id}`")
    if thread_id:
        lines.append(f"• **Current Topic ID**: `{thread_id}`")
    await bot._send_message(session, chat_id, "\n".join(lines), message_thread_id=thread_id)

async def handle_about(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    thread_id = message.get("message_thread_id") if message else None
    about_text = (
        f"🩺 <b>Kind Doctor Bot (@KindDoc_bot)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"• <b>Developer & Chief Architect:</b> Dr. Amit Singh (@Kinddoctor4u)\n"
        f"• <b>Master Administration:</b> @Kinddoctor4u | @Ammitrajput1\n"
        f"• <b>Core Purpose:</b> Medical Study Assistant, High-Speed Wire Cloner, and CDSS Clinical Engine.\n"
        f"• <b>Engine Status:</b> 24/7 Always-Online Cloud Suite with Polyglot Acceleration."
    )
    await bot._send_message(session, chat_id, about_text, message_thread_id=thread_id, parse_mode="HTML")

def register_navigation_handlers(router):
    router.register(["/start", "/help", "/menu", "/mode", "/fullhelp"], handle_start_or_menu, "Main Navigation & Help Menu", "navigation")
    router.register(["/support", "/contact"], handle_support, "Direct Doctor Help Line", "navigation")
    router.register(["/id", "/myid", "/info"], handle_id, "User & Chat Telegram ID Info", "navigation")
    router.register(["/about", "/botinfo"], handle_about, "About Kind Doctor Suite", "navigation")

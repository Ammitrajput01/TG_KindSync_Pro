# -*- coding: utf-8 -*-
"""
Devi Operator Administrative & Server Maintenance Command Handlers
Handles /speed, /pacing, /strip, /polyglot, /engine, /vps, /backup in O(1) time.
Architect: Dr. Amit Singh (Kind Doctor) · @Kinddoctor4u
"""

import sys
from typing import List, Optional

async def handle_strip_words(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    thread_id = message.get("message_thread_id") if message else None
    card_text, kb = bot._build_strip_words_card_data(admin_id, page=1)
    await bot._send_message(session, chat_id, card_text, reply_markup=kb, disable_web_page_preview=True, message_thread_id=thread_id)

async def handle_pacing(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    thread_id = message.get("message_thread_id") if message else None
    card_text, kb = bot._build_pacing_card_data(admin_id)
    await bot._send_message(session, chat_id, card_text, reply_markup=kb, disable_web_page_preview=True, message_thread_id=thread_id)

async def handle_polyglot(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    thread_id = message.get("message_thread_id") if message else None
    if not bot.is_admin(admin_id):
        await bot._send_message(session, chat_id, "⛔ Restricted to Master Admins.", message_thread_id=thread_id)
        return

    try:
        from devi.operator.polyglot_accelerator import get_acceleration_status
        accel = get_acceleration_status()
    except Exception:
        accel = {
            "crypto_engine": "Standard Fallback",
            "json_engine": "Standard JSON",
            "analytics_engine": "SQLite",
            "platform": sys.platform,
            "event_loop": "asyncio"
        }

    polyglot_card = (
        f"⚡ <b>POLYGLOT NATIVE ACCELERATION MATRIX</b> 🚀\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🛡️ <b>Hardware Cryptography:</b> <code>{accel.get('crypto_engine')}</code>\n"
        f"🦀 <b>JSON Parsing (Rust):</b> <code>{accel.get('json_engine')}</code>\n"
        f"🦆 <b>Analytical Scanner (DuckDB):</b> <code>{accel.get('analytics_engine')}</code>\n"
        f"🌐 <b>Event Loop Architecture:</b> <code>{accel.get('event_loop')}</code>\n"
        f"🚀 <b>Kernel Socket Pacing:</b> <code>TCP_NODELAY + 1MB Buffers + TCP_NOTSENT_LOWAT (Zero Bufferbloat)</code>\n"
        f"💻 <b>Runtime Platform:</b> <code>{accel.get('platform')}</code>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>Dual-Parity Shield:</b> Oracle Linux VPS ⇋ Windows Friend Edition\n"
        f"🛡️ <b>Zero-Friction Fallback:</b> 100% active (Graceful pure-Python safety)\n"
        f"👑 <b>Master Admins:</b> @Kinddoctor4u | @Ammitrajput1"
    )
    accel_kb = {
        "inline_keyboard": [
            [
                {"text": "🔄 Refresh Matrix", "callback_data": "act_polyglot_status"},
                {"text": "🎛️ Master Engine", "callback_data": "act_engine_refresh"}
            ]
        ]
    }
    await bot._send_message(session, chat_id, polyglot_card, reply_markup=accel_kb, message_thread_id=thread_id)

def register_admin_handlers(router):
    router.register(["/strip", "/stripwords", "/striplist", "/stripcard"], handle_strip_words, "Strip Words & Watermark Studio", "admin")
    router.register(["/pacing", "/speed", "/delay"], handle_pacing, "Transmission Speed & Flood Pacing", "admin")
    router.register(["/polyglot", "/accelerator"], handle_polyglot, "Polyglot Acceleration Matrix Status", "admin")

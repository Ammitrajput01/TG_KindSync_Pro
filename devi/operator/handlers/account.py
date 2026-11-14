# -*- coding: utf-8 -*-
"""
Devi Operator Multi-Tenant User Session Account Linking Command Handlers
Handles /connect, /myaccount, /disconnect in O(1) time with Fernet encryption.
Architect: Dr. Amit Singh (Kind Doctor) · @Kinddoctor4u
"""

import asyncio
from typing import List, Optional
from devi.operator.session_vault import get_user_linked_session, mask_phone_number, delete_linked_user_session

async def handle_connect(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    thread_id = message.get("message_thread_id") if message else None
    now = asyncio.get_event_loop().time()
    
    attempts = [t for t in bot.connect_rate_limits.get(admin_id, []) if now - t < 3600]
    if len(attempts) >= 5:
        rate_limit_msg = (
            "⏳ <b>Rate Limit Exceeded:</b>\n\n"
            "You have initiated 5 connection attempts in the last hour. "
            "Please wait a few minutes before trying again to prevent Telegram flood restrictions."
        )
        await bot._send_message(session, chat_id, rate_limit_msg, message_thread_id=thread_id)
        return

    existing = get_user_linked_session(admin_id)
    if existing:
        already_msg = (
            "✅ <b>Your Telegram Account is Already Connected!</b> 🩺\n\n"
            f"🆔 <b>Telegram User ID:</b> <code>{admin_id}</code>\n"
            "⚡ <b>Status:</b> <code>ACTIVE & ENCRYPTED (Fernet)</code> 🟢\n"
            "🚀 <b>Power:</b> Full access to your own private groups & 800+ topics enabled.\n\n"
            "• View details: <code>/myaccount</code>\n"
            "• Disconnect session: <code>/disconnect</code>\n"
            "• To switch accounts, disconnect first."
        )
        markup = {
            "inline_keyboard": [
                [{"text": "🗑️ Disconnect Account", "callback_data": "act_disconnect"}],
                [{"text": "ℹ️ Learn More (/connect_help)", "callback_data": "act_connect_help"}]
            ]
        }
        await bot._send_message(session, chat_id, already_msg, reply_markup=markup, message_thread_id=thread_id)
        return

    if chat_id < 0:
        guide_dm = (
            "🔒 <b>Security & Privacy Protection:</b>\n\n"
            "For your privacy, phone numbers and login codes must be entered in the <b>Bot's Private DM</b>:\n\n"
            f"👉 <a href=\"https://t.me/{bot.bot_username}?start=connect\"><b>Click Here to Connect Account Securely in DM</b></a>"
        )
        await bot._send_message(session, chat_id, guide_dm, message_thread_id=thread_id)
        return

    attempts.append(now)
    bot.connect_rate_limits[admin_id] = attempts

    bot.pending_auth[admin_id] = {
        "step": "awaiting_consent",
        "chat_id": chat_id,
        "ts": now,
        "deadline": now + 600
    }

    consent_text = (
        "🔐 <b>Connect Your Own Telegram Account (/connect)</b> 🩺\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "This feature allows you to link your Telegram account so the bot can use <b>YOUR session</b> "
        "to scan forum topics and clone study materials from groups/channels you are already a member of "
        "(including private channels and supergroups with 800+ topics that the bot cannot see).\n\n"
        "🛡️ <b>Strict Privacy & Security Guarantees:</b>\n"
        "• <b>100% User Isolation:</b> Your session is strictly used for <b>your own jobs only</b>.\n"
        "• 🔒 <b>Fernet Encryption:</b> Stored encrypted at rest using Fernet encryption.\n"
        "• 🛑 <b>Zero Logging:</b> Your phone number and OTP code are never logged.\n"
        "• 🗑️ <b>Instant Revocation:</b> You can delete your session anytime with <code>/disconnect</code>.\n\n"
        "👉 <i>Click 'I Agree & Continue' below to enter your phone number.</i>"
    )
    markup = {
        "inline_keyboard": [
            [{"text": "✅ I Agree & Continue", "callback_data": "auth_consent_agree"}],
            [{"text": "❌ Cancel", "callback_data": "auth_cancel"}]
        ]
    }
    await bot._send_message(session, chat_id, consent_text, reply_markup=markup, message_thread_id=thread_id)

async def handle_myaccount(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    thread_id = message.get("message_thread_id") if message else None
    existing = get_user_linked_session(admin_id)
    if not existing:
        not_conn = (
            "ℹ️ <b>No Telegram Account Connected</b> 🩺\n\n"
            "You haven't linked your account yet. Linking your account lets the bot clone from your private groups.\n\n"
            "👉 Use <code>/connect</code> to link your account securely."
        )
        markup = {
            "inline_keyboard": [
                [{"text": "🔐 Connect Account (/connect)", "callback_data": "act_connect_init"}]
            ]
        }
        await bot._send_message(session, chat_id, not_conn, reply_markup=markup, message_thread_id=thread_id)
        return

    masked_phone = mask_phone_number(existing.get("phone", ""))
    first_name = existing.get("first_name", "Telegram User")
    conn_time = existing.get("connected_at", "Recently")
    
    detail_msg = (
        "👤 <b>Your Connected Account Details:</b> 🩺\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"• <b>Name:</b> {first_name}\n"
        f"• <b>Phone Number:</b> <code>{masked_phone}</code>\n"
        f"• <b>Telegram User ID:</b> <code>{admin_id}</code>\n"
        f"• <b>Connected Since:</b> <code>{conn_time}</code>\n"
        "• <b>Storage Mode:</b> <code>Fernet 256-bit AES Encrypted</code> 🔒\n"
        "• <b>Permission Level:</b> <code>Personal Dedicated Userbot</code> 🟢\n\n"
        "💡 <i>Your session is only accessed when you start a cloning job for yourself.</i>"
    )
    markup = {
        "inline_keyboard": [
            [{"text": "🗑️ Disconnect Account", "callback_data": "act_disconnect"}]
        ]
    }
    await bot._send_message(session, chat_id, detail_msg, reply_markup=markup, message_thread_id=thread_id)

async def handle_disconnect(bot, session, chat_id: int, admin_id: int, text: str, message: Optional[dict], parts: List[str]):
    thread_id = message.get("message_thread_id") if message else None
    deleted = delete_linked_user_session(admin_id)
    if deleted:
        msg = (
            "🗑️ <b>Account Disconnected Successfully</b>\n\n"
            "Your encrypted session has been permanently removed from the bot database. "
            "The bot can no longer access your personal groups or channels."
        )
    else:
        msg = "ℹ️ No active connected session was found for your account."
    await bot._send_message(session, chat_id, msg, message_thread_id=thread_id)

def register_account_handlers(router):
    router.register(["/connect", "/linkaccount", "/connectaccount", "/login"], handle_connect, "Connect Telegram User Account", "account")
    router.register(["/myaccount", "/accountinfo"], handle_myaccount, "View Connected Account Info", "account")
    router.register(["/unlinkaccount", "/disconnect", "/logout"], handle_disconnect, "Revoke Connected Session", "account")

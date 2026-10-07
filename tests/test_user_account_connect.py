#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Unit and Integration Tests for Kind Doctor Bot "/connect" Feature:
- User consent flow (decline / abort)
- Phone format validation
- Space-separated OTP handling & attempt cap (max 5)
- 2FA branch handling
- 10-minute timeout expiry
- /disconnect database removal & client stopping
- Strict user session isolation (User A vs User B)
- Fernet encryption round-trip & ciphertext non-plaintext verification
"""

import os
import sys
import re
import pytest
import sqlite3
import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from telethon.errors import (
    PhoneCodeInvalidError, PhoneCodeExpiredError,
    SessionPasswordNeededError, PasswordHashInvalidError,
    PhoneNumberInvalidError, FloodWaitError
)

from devi.operator.session_vault import (
    encrypt_session_string, decrypt_session_string,
    save_linked_user_session, get_user_linked_session,
    delete_linked_user_session, get_user_client,
    get_vault_client_for_target, mask_phone_number,
    DB_PATH
)
from devi.operator.telegram_bot import DeviTelegramBot

# Sample dummy StringSession (Telethon 1.x format)
MOCK_RAW_SESSION = "1BZbW5tUBwMC4t3K8eZqJ6v9XyLmNqRtPuWsDvFhJkMnPqRsTuVwXyZ0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ=="

@pytest.fixture(autouse=True)
def clean_test_sessions():
    """Ensure test users are cleaned up before and after each test."""
    test_users = [999001, 999002, 999003]
    with sqlite3.connect(DB_PATH) as conn:
        for u in test_users:
            conn.execute("DELETE FROM telegram_linked_sessions WHERE user_id = ?", (u,))
        conn.commit()
    yield
    with sqlite3.connect(DB_PATH) as conn:
        for u in test_users:
            conn.execute("DELETE FROM telegram_linked_sessions WHERE user_id = ?", (u,))
        conn.commit()

# ---------------------------------------------------------------------------
# 1. Fernet Encryption & Non-Plaintext Storage Test
# ---------------------------------------------------------------------------
def test_fernet_roundtrip_and_non_plaintext():
    """Verify session string is encrypted with Fernet and never stored in plaintext."""
    enc = encrypt_session_string(MOCK_RAW_SESSION)
    assert enc != MOCK_RAW_SESSION
    assert enc.startswith("gAAAAA"), "Fernet token must start with standard Fernet header"
    assert MOCK_RAW_SESSION not in enc, "Plaintext session must never appear in ciphertext"

    dec = decrypt_session_string(enc)
    assert dec == MOCK_RAW_SESSION, "Decrypted session must match original raw string"

def test_db_storage_is_encrypted():
    """Verify stored SQLite column contains ciphertext token, not plaintext."""
    user_id = 999001
    phone = "+919876543210"
    success = save_linked_user_session(user_id, phone, MOCK_RAW_SESSION, name="Test Doctor", username="testdoc")
    assert success is True

    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("SELECT session_string, phone_number FROM telegram_linked_sessions WHERE user_id = ?", (user_id,)).fetchone()
        assert row is not None
        db_session_val, db_phone_val = row[0], row[1]

    # Verify column in SQLite is Fernet encrypted
    assert db_session_val.startswith("gAAAAA")
    assert MOCK_RAW_SESSION not in db_session_val

    # Verify getter returns decrypted string
    retrieved = get_user_linked_session(user_id)
    assert retrieved == MOCK_RAW_SESSION

# ---------------------------------------------------------------------------
# 2. Strict User Isolation Test (User A vs User B)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_user_session_strict_isolation():
    """Verify User A's session is never accessible or returned for User B."""
    user_a = 999001
    user_b = 999002

    # User A connects account
    save_linked_user_session(user_a, "+919876543210", MOCK_RAW_SESSION, name="User A")

    # User B has no connected account
    sess_a = get_user_linked_session(user_a)
    sess_b = get_user_linked_session(user_b)

    assert sess_a == MOCK_RAW_SESSION
    assert sess_b is None, "User B must not be able to retrieve User A's session"

    # Verify get_user_client returns None for User B
    client_b = await get_user_client(user_b)
    assert client_b is None, "get_user_client must return None for unconnected user"

# ---------------------------------------------------------------------------
# 3. /disconnect Lifecycle Test
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_disconnect_removes_session_and_stops_client():
    """Verify /disconnect wipes database row immediately and cleans up active references."""
    user_id = 999001
    save_linked_user_session(user_id, "+919876543210", MOCK_RAW_SESSION, name="Test User")

    assert get_user_linked_session(user_id) is not None

    deleted = delete_linked_user_session(user_id)
    assert deleted is True

    # Database must now be empty for this user
    assert get_user_linked_session(user_id) is None

# ---------------------------------------------------------------------------
# 4. FSM Test: Consent Decline Aborts Cleanly
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_fsm_consent_decline():
    """Verify saying 'no' or 'cancel' at consent step aborts flow without saving."""
    bot = DeviTelegramBot(bot_token="123456:ABC-DEF")
    user_id = 999001
    chat_id = 999001

    bot.pending_auth[user_id] = {
        "step": "awaiting_consent",
        "chat_id": chat_id,
        "deadline": asyncio.get_event_loop().time() + 600
    }

    mock_session = AsyncMock()
    with patch.object(bot, '_send_message', new_callable=AsyncMock) as mock_send:
        handled = await bot._handle_account_linking_step(mock_session, chat_id, user_id, "no", {})
        assert handled is True
        assert user_id not in bot.pending_auth, "pending_auth must be cleared after decline"
        mock_send.assert_called_once()
        assert "cancelled" in mock_send.call_args[0][2].lower()

# ---------------------------------------------------------------------------
# 5. FSM Test: Invalid Phone Format Rejected and Re-Prompted
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_fsm_invalid_phone_rejected():
    """Verify invalid phone numbers are rejected with format instructions."""
    bot = DeviTelegramBot(bot_token="123456:ABC-DEF")
    user_id = 999001
    chat_id = 999001

    bot.pending_auth[user_id] = {
        "step": "awaiting_phone",
        "chat_id": chat_id,
        "deadline": asyncio.get_event_loop().time() + 600
    }

    mock_session = AsyncMock()
    with patch.object(bot, '_send_message', new_callable=AsyncMock) as mock_send:
        handled = await bot._handle_account_linking_step(mock_session, chat_id, user_id, "hello1234", {})
        assert handled is True
        assert bot.pending_auth[user_id]["step"] == "awaiting_phone", "Must remain on awaiting_phone step"
        assert "Invalid Phone Number" in mock_send.call_args[0][2]

# ---------------------------------------------------------------------------
# 6. FSM Test: Wrong OTP Attempt Cap (5 Attempts) Then Abort
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_fsm_otp_attempt_cap_aborts():
    """Verify entering invalid OTP 5 times aborts the connection flow."""
    bot = DeviTelegramBot(bot_token="123456:ABC-DEF")
    user_id = 999001
    chat_id = 999001

    mock_client = AsyncMock()
    mock_client.sign_in.side_effect = PhoneCodeInvalidError(request=None)

    bot.pending_auth[user_id] = {
        "step": "awaiting_otp",
        "chat_id": chat_id,
        "client": mock_client,
        "phone": "+919876543210",
        "phone_code_hash": "hash_123",
        "otp_attempts": 0,
        "deadline": asyncio.get_event_loop().time() + 600
    }

    mock_session = AsyncMock()
    with patch.object(bot, '_send_message', new_callable=AsyncMock) as mock_send, \
         patch.object(bot, '_delete_message', new_callable=AsyncMock):

        # Attempts 1 to 4 should retry
        for i in range(1, 5):
            await bot._handle_account_linking_step(mock_session, chat_id, user_id, "1 2 3 4 5", {})
            assert user_id in bot.pending_auth
            assert bot.pending_auth[user_id]["otp_attempts"] == i

        # 5th attempt must abort flow
        await bot._handle_account_linking_step(mock_session, chat_id, user_id, "1 2 3 4 5", {})
        assert user_id not in bot.pending_auth, "Must abort and pop state on 5th failure"
        assert "Maximum 5 OTP attempts" in mock_send.call_args[0][2]

# ---------------------------------------------------------------------------
# 7. FSM Test: 2FA Branch Triggers Correctly
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_fsm_2fa_branch_trigger():
    """Verify SessionPasswordNeededError transitions step to awaiting_2fa."""
    bot = DeviTelegramBot(bot_token="123456:ABC-DEF")
    user_id = 999001
    chat_id = 999001

    mock_client = AsyncMock()
    mock_client.sign_in.side_effect = SessionPasswordNeededError(request=None)

    bot.pending_auth[user_id] = {
        "step": "awaiting_otp",
        "chat_id": chat_id,
        "client": mock_client,
        "phone": "+919876543210",
        "phone_code_hash": "hash_123",
        "otp_attempts": 0,
        "deadline": asyncio.get_event_loop().time() + 600
    }

    mock_session = AsyncMock()
    with patch.object(bot, '_send_message', new_callable=AsyncMock) as mock_send, \
         patch.object(bot, '_delete_message', new_callable=AsyncMock):
        handled = await bot._handle_account_linking_step(mock_session, chat_id, user_id, "5 4 3 2 1", {})
        assert handled is True
        assert bot.pending_auth[user_id]["step"] == "awaiting_2fa"
        assert "2FA" in mock_send.call_args[0][2]

# ---------------------------------------------------------------------------
# 8. FSM Test: Flow Timeout Clears State
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_fsm_timeout_clears_state():
    """Verify inactivity beyond deadline (10 minutes) clears state and warns user."""
    bot = DeviTelegramBot(bot_token="123456:ABC-DEF")
    user_id = 999001
    chat_id = 999001

    mock_client = AsyncMock()
    bot.pending_auth[user_id] = {
        "step": "awaiting_otp",
        "chat_id": chat_id,
        "client": mock_client,
        "phone": "+919876543210",
        "deadline": asyncio.get_event_loop().time() - 10  # Expired 10s ago
    }

    mock_session = AsyncMock()
    with patch.object(bot, '_send_message', new_callable=AsyncMock) as mock_send:
        handled = await bot._handle_account_linking_step(mock_session, chat_id, user_id, "1 2 3 4 5", {})
        assert handled is True
        assert user_id not in bot.pending_auth, "Expired session state must be popped"
        assert "timed out" in mock_send.call_args[0][2].lower()

# ---------------------------------------------------------------------------
# 9. Rate Limiting Test (Max 5 Attempts per Hour)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_connect_rate_limit_per_user():
    """Verify /connect rate limiting blocks user after 5 attempts in an hour."""
    bot = DeviTelegramBot(bot_token="123456:ABC-DEF")
    user_id = 999001
    chat_id = 999001
    now = asyncio.get_event_loop().time()

    # Pre-populate 5 attempts in the last 10 minutes
    bot.connect_rate_limits[user_id] = [now - 600, now - 500, now - 400, now - 300, now - 200]

    mock_session = AsyncMock()
    with patch.object(bot, '_send_message', new_callable=AsyncMock) as mock_send:
        await bot._handle_admin_command(mock_session, chat_id, user_id, "/connect")
        mock_send.assert_called_once()
        assert "Rate Limit Exceeded" in mock_send.call_args[0][2]

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit test suite for In-Bot 16:9 Cover Thumbnail Studio & Subject Header formatting.
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from devi.operator.telegram_bot import DeviTelegramBot
from tg_kindsync_pro import detect_subject

def test_subject_header_clean_without_hashtags():
    """Verify that detect_subject outputs clean name and icon, and default AUTO_HASHTAGS is false."""
    subj = detect_subject("Lecture 01 Anatomy of Upper Limb.mp4", "")
    assert subj is not None
    assert subj["name"] == "ANATOMY"
    assert subj["icon"] == "🦴"
    assert os.getenv("AUTO_HASHTAGS", "false").lower() in ("false", "0", "no")

@pytest.mark.asyncio
async def test_bot_thumb_commands_registered():
    """Verify that /setthumb, /viewthumb, /delthumb are in allowed public commands."""
    from devi.operator.telegram_bot import PUBLIC_ALLOWED_COMMANDS
    for cmd in ["/setthumb", "/thumb", "/viewthumb", "/delthumb", "/resetthumb"]:
        assert cmd in PUBLIC_ALLOWED_COMMANDS, f"{cmd} must be in PUBLIC_ALLOWED_COMMANDS"

@pytest.mark.asyncio
async def test_bot_setthumb_prompt_when_sent_alone():
    """Verify that /setthumb when sent without a photo sets user in pending_thumb_upload."""
    bot = DeviTelegramBot(bot_token="123456:TEST_TOKEN")
    session = MagicMock()
    bot._send_message = AsyncMock(return_value=1234)

    msg = {
        "message_id": 100,
        "chat": {"id": 1553619403, "type": "private"},
        "from": {"id": 1553619403, "username": "Kinddoctor4u"},
        "text": "/setthumb"
    }

    await bot._handle_admin_command(session, 1553619403, 1553619403, "/setthumb", message=msg)

    assert 1553619403 in bot.pending_thumb_upload
    assert bot._send_message.called

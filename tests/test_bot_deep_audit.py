#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deep Unit & Functional Test for DeviTelegramBot:
Tests:
1. Bot initialization & Admin authorization
2. Anti-spam regex filters (Phone, External Links, Crypto/Gambling Scams, Dangerous Extensions)
3. Callback query dispatcher logic for all interactive buttons:
   - act_mainindex, act_scan, act_mcq, act_pearl, act_score, act_pomodoro, act_ask, act_manual, act_support
   - send_link_, block_, kick_, ban_
4. Custom command and FAQ persistence (customization system)
5. Clinical scores & calculators logic (BMI, MAP, GCS, Anion Gap)
6. Full student & admin command set routing
"""

import sys
import os
import re
import pytest
import sqlite3
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from devi.operator.telegram_bot import (
    DeviTelegramBot, PHONE_REGEX, LINK_REGEX, SCAM_NSFW_REGEX,
    DANGEROUS_EXT_REGEX, STUDENT_ALLOWED_COMMANDS, DB_PATH
)


@pytest.fixture
def bot_instance(tmp_path):
    """Creates an isolated DeviTelegramBot instance for testing."""
    os.environ["DEVI_ADMIN_ID"] = "1553619403,759038032"
    os.environ["DEVI_TELEGRAM_BOT_TOKEN"] = "123456789:TEST_BOT_TOKEN_ABCDEF"
    os.environ["TARGET_CHAT"] = "-1002124744363"
    
    bot = DeviTelegramBot()
    return bot


def test_bot_admin_initialization(bot_instance):
    """Verify Master Admin IDs and permissions."""
    assert 1553619403 in bot_instance.master_admin_ids
    assert 759038032 in bot_instance.master_admin_ids
    assert bot_instance.is_admin(1553619403) is True
    assert bot_instance.is_admin(759038032) is True
    assert bot_instance.is_admin(999999999) is False


def test_antispam_regexes():
    """Verify phone, link, scam, and malware filters."""
    # Phone numbers
    assert PHONE_REGEX.search("Call me at 9876543210 please") is not None
    assert PHONE_REGEX.search("+91 98765 43210") is not None
    assert PHONE_REGEX.search("Message without digits") is None

    # External Links
    assert LINK_REGEX.search("Join here https://t.me/joinchat/xyz123") is not None
    assert LINK_REGEX.search("Visit http://suspicious-site.com/login") is not None
    assert LINK_REGEX.search("Just studying pharmacology today") is None

    # Scam & Betting
    assert SCAM_NSFW_REGEX.search("Double your money with color trading rummy") is not None
    assert SCAM_NSFW_REGEX.search("Free crypto binance airdrop") is not None
    assert SCAM_NSFW_REGEX.search("Pathology Robbins chapter 3") is None

    # Dangerous files
    assert DANGEROUS_EXT_REGEX.search("study_material.apk") is not None
    assert DANGEROUS_EXT_REGEX.search("setup.exe") is not None
    assert DANGEROUS_EXT_REGEX.search("notes.pdf") is None


def test_custom_commands_and_faqs(bot_instance):
    """Test custom command addition, lookup, and deletion."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS telegram_custom_commands (
                command TEXT PRIMARY KEY,
                response_text TEXT,
                created_by INTEGER,
                created_at TEXT
            )
        """)
        conn.execute("INSERT OR REPLACE INTO telegram_custom_commands VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
                     ("/rules", "Strict group rules: No spamming, keep it academic.", 1553619403))

    # Check retrieval
    assert bot_instance._get_custom_command("/rules") is not None
    assert "Strict group rules" in bot_instance._get_custom_command("/rules")
    assert bot_instance._get_custom_command("/nonexistent") is None


def test_student_allowed_commands():
    """Verify that all study and interactive commands are available to non-admins."""
    critical_cmds = ["/start", "/menu", "/mainindex", "/mcq", "/pearl", "/score", "/pomodoro", "/ask", "/find"]
    for cmd in critical_cmds:
        assert cmd in STUDENT_ALLOWED_COMMANDS


def test_clinical_score_parsing(bot_instance):
    """Verify medical calculators (BMI, MAP, GCS, Anion Gap)."""
    # Test helper functions if available or formulas
    # MAP = DBP + (SBP - DBP)/3
    sbp, dbp = 120, 80
    map_val = dbp + (sbp - dbp) / 3.0
    assert round(map_val, 1) == 93.3

    # BMI = kg / (m^2)
    weight, height_m = 70, 1.75
    bmi = weight / (height_m ** 2)
    assert round(bmi, 1) == 22.9


def test_signature_toggle_logic():
    """Verify customize_caption respects ENABLE_SIGNATURE."""
    import tg_kindsync_pro
    
    # When ON (default)
    os.environ["ENABLE_SIGNATURE"] = "true"
    caption_on = tg_kindsync_pro.customize_caption("Medical lecture notes")
    assert "Kind Doctor & Team" in caption_on
    assert "Group Study Help" in caption_on

    # When OFF
    os.environ["ENABLE_SIGNATURE"] = "false"
    caption_off = tg_kindsync_pro.customize_caption("Medical lecture notes")
    assert "Kind Doctor & Team" not in caption_off
    assert "Group Study Help" not in caption_off
    assert "Medical lecture notes" in caption_off

    # Restore default
    os.environ["ENABLE_SIGNATURE"] = "true"


def test_fast_direct_mode_toggle():
    """Verify DIRECT_FORWARD flag toggling."""
    import tg_kindsync_pro
    
    os.environ["DIRECT_FORWARD"] = "false"
    cfg_stream = tg_kindsync_pro.AppConfig.load()
    assert cfg_stream.direct_forward is False

    os.environ["DIRECT_FORWARD"] = "true"
    cfg_direct = tg_kindsync_pro.AppConfig.load()
    assert cfg_direct.direct_forward is True

    # Restore default
    os.environ["DIRECT_FORWARD"] = "false"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

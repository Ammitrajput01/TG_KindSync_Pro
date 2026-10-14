import pytest
import sqlite3
from pathlib import Path
from devi.operator.telegram_bot import DeviTelegramBot
from devi.operator.session_vault import DB_PATH
import tg_kindsync_pro

def test_group_settings_migration_and_defaults():
    bot = DeviTelegramBot()
    test_chat_id = -1009999888877
    
    settings = bot._get_group_settings(test_chat_id)
    assert "join_track_dest" in settings
    assert settings.get("join_track_dest") == "pm"
    assert "welcome_timeout" in settings
    assert settings.get("welcome_timeout") == 60

    # Test updating settings
    bot._save_group_setting(test_chat_id, "welcome_timeout", 120)
    bot._save_group_setting(test_chat_id, "join_track_dest", "group")
    
    updated = bot._get_group_settings(test_chat_id)
    assert updated.get("welcome_timeout") == 120
    assert updated.get("join_track_dest") == "group"

    # Cleanup
    with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
        conn.execute("DELETE FROM telegram_group_settings WHERE chat_id = ?", (str(test_chat_id),))

def test_screen_false_scrollback_invariant():
    """Verify tg_kindsync_pro uses screen=False in Live context for terminal scrollback support."""
    src_file = Path("tg_kindsync_pro.py")
    content = src_file.read_text(encoding="utf-8")
    assert "screen=False" in content
    # Ensure screen=True is not present for Live
    assert "Live(self.render_dashboard(), console=console, refresh_per_second=1, screen=True" not in content

def test_platform_detach_attributes_and_handlers():
    """Verify TerminalPlatform includes detach and multitasking methods."""
    assert hasattr(tg_kindsync_pro.TerminalPlatform, "resume_live_dashboard")
    assert hasattr(tg_kindsync_pro.TerminalPlatform, "stop")
    assert hasattr(tg_kindsync_pro, "_GLOBAL_ACTIVE_PLATFORM")

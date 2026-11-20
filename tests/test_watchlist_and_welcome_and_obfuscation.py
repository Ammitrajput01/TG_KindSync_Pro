import pytest
import os
import json
from pathlib import Path
from tg_kindsync_pro import apply_clean_rules, get_clean_rules
from devi.operator.telegram_bot import DeviTelegramBot

def test_welcome_message_default_ttl():
    """Verify welcome message default TTL is strictly 86400 seconds (24 hours / 1 day)."""
    bot = DeviTelegramBot()
    settings = bot._get_group_settings(-1009999999999)
    assert settings.get("welcome_timeout") == 86400, "Default welcome_timeout must be 86400 seconds (24 hours)"

def test_anti_dmca_obfuscation_matrix():
    """Verify medical brand names are converted into anti-DMCA leet-speak representation."""
    raw_sample = "Study Medicine Lecture by DAMS and Marrow Edition 6 with PrepLadder notes and Cerebellum QBank"
    cleaned = apply_clean_rules(raw_sample)
    
    assert "D@MS" in cleaned, "DAMS should be replaced by D@MS"
    assert "M@rr0w" in cleaned, "Marrow should be replaced by M@rr0w"
    assert "Prep L@dder" in cleaned, "PrepLadder should be replaced by Prep L@dder"
    assert "Cer@bellum" in cleaned, "Cerebellum should be replaced by Cer@bellum"
    # Ensure no unintended substring corruption
    assert "macadam" == apply_clean_rules("macadam"), "Unrelated words containing 'dam' must not be corrupted"

def test_highlight_watchlist_loading():
    """Verify highlight watchlist correctly loads quarantined users."""
    bot = DeviTelegramBot()
    wl = bot._get_highlight_watchlist()
    assert len(wl) >= 50, f"Expected at least 50 highlight users in watchlist, found {len(wl)}"
    # Preeti rank 1 check
    assert 1750439796 in wl, "Rank 1 member (ID 1750439796) must be present in watchlist"


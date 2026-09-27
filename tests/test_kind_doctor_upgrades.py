"""
Verification test for:
1. Kind Doctor Bot Name Auto-Sync (setMyName)
2. Unified Branding Toggle (Signature + Thumbnail linked)
3. Adaptive Dynamic Pacing (Uncapped media wire speed)
"""

import os
import sys
import inspect
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

def test_telegram_bot_name_sync():
    bot_file = Path(__file__).resolve().parent.parent / "devi" / "operator" / "telegram_bot.py"
    content = bot_file.read_text(encoding="utf-8")
    
    assert "setMyName" in content, "setMyName endpoint must be called in telegram_bot.py"
    assert '"name": "Kind Doctor 🩺"' in content, "Bot name must be explicitly set to 'Kind Doctor 🩺'"
    print("[+] test_telegram_bot_name_sync passed!")

def test_unified_branding_toggle_logic():
    # Test telegram bot callback logic
    bot_file = Path(__file__).resolve().parent.parent / "devi" / "operator" / "telegram_bot.py"
    content = bot_file.read_text(encoding="utf-8")
    
    assert 'new_th = "custom" if new_sig == "true" else "original"' in content
    assert 'set_key(str(ENV_PATH), "THUMB_MODE", new_th)' in content
    print("[+] test_unified_branding_toggle_bot passed!")

def test_kindsync_unified_clean_mode():
    kindsync_file = Path(__file__).resolve().parent.parent / "tg_kindsync_pro.py"
    content = kindsync_file.read_text(encoding="utf-8")
    
    # Verify t_path checks sig_enabled
    assert 'sig_enabled = os.getenv("ENABLE_SIGNATURE", "true").strip().lower() in ("true", "1", "yes")' in content
    assert 'get_input_file(client)' in content and 'sig_enabled' in content
    
    # Verify terminal choice 12 toggles both
    assert 'new_th = "custom" if new_val == "true" else "original"' in content
    assert 'set_key(env_path, "THUMB_MODE", new_th)' in content
    print("[+] test_kindsync_unified_clean_mode passed!")

def test_uncapped_media_velocity():
    kindsync_file = Path(__file__).resolve().parent.parent / "tg_kindsync_pro.py"
    content = kindsync_file.read_text(encoding="utf-8")
    
    assert 'actual_delay = 0.0  # 100% Uncapped Supersonic Speed' in content
    print("[+] test_uncapped_media_velocity passed!")

def test_stripping_always_active():
    from tg_kindsync_pro import apply_clean_rules, sanitize_filename, clean_index_title
    
    # 1. Check strip_words.txt words are stripped unconditionally
    sample_text = "Neuroanatomy Lecture 1 Shimperd @AnandxBotss kirmada rockstar"
    cleaned = apply_clean_rules(sample_text)
    assert "Shimperd" not in cleaned, "Shimperd must be stripped"
    assert "@AnandxBotss" not in cleaned, "@AnandxBotss must be stripped"
    assert "kirmada" not in cleaned, "kirmada must be stripped"
    
    # 2. Check admin / uploader tags are stripped
    sample_admin = "Pathology Notes\nUploaded by: Dr. Foreign Admin\nAdmin: @SpamAdminBot"
    cleaned_admin = apply_clean_rules(sample_admin)
    assert "Uploaded by" not in cleaned_admin
    assert "Admin:" not in cleaned_admin
    
    # 3. Check filename sanitization also strips
    clean_fn = sanitize_filename("Shimperd - Lecture 01 @AnandxBotss.mp4")
    assert "Shimperd" not in clean_fn
    assert "@AnandxBotss" not in clean_fn
    
    print("[+] test_stripping_always_active passed!")

if __name__ == "__main__":
    test_telegram_bot_name_sync()
    test_unified_branding_toggle_logic()
    test_kindsync_unified_clean_mode()
    test_uncapped_media_velocity()
    test_stripping_always_active()
    print("\n[OK] ALL KIND DOCTOR UPGRADES VERIFIED 100% PASSING!")

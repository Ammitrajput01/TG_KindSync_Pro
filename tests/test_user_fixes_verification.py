import os
import sys
from pathlib import Path

# Fix Windows console UTF-8 output
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from tg_kindsync_pro import (
    sanitize_filename, customize_caption, ThumbEnforcer,
    parse_telegram_link,
)


def test_parse_telegram_link():
    res = parse_telegram_link("https://t.me/c/4234551262/259")
    chat_id = res.get("CHAT_ID")
    topic_id = res.get("TOPIC_ID")
    assert chat_id == -1004234551262, f"Expected -1004234551262 got {chat_id}"
    assert topic_id == 259, f"Expected 259 got {topic_id}"


def test_sanitize_filename_with_replace_words_and_prefix(monkeypatch):
    import tg_kindsync_pro
    monkeypatch.setenv("REPLACE_WORDS", "OldAcademy:KindDoctor,Batch2024:2026")
    monkeypatch.setenv("CUSTOM_FILE_PREFIX", "DrAmit - ")
    monkeypatch.setitem(tg_kindsync_pro._CLEAN_RULES_CACHE, "mtime_env", -1)
    s_name = sanitize_filename("OldAcademy Anatomy Lecture 01 Batch2024.mp4", fallback_ext=".mp4")
    assert "OldAcademy" not in s_name
    assert "KindDoctor" in s_name
    assert s_name.startswith("DrAmit - ")


def test_customize_caption_strip_hashtags_when_tagging_off(monkeypatch):
    monkeypatch.setenv("AUTO_HASHTAGS", "false")
    monkeypatch.setenv("STRIP_HASHTAGS", "true")
    monkeypatch.setenv("CUSTOM_HEADER", "🌟 EXCLUSIVE LECTURE")
    monkeypatch.setenv("CUSTOM_FOOTER", "👨‍⚕️ Curated by Kind Doctor")

    cap_in = "Pharmacology Class 01 #OldChannel #Promo join @channel"
    cap_out = customize_caption(cap_in)
    assert "#OldChannel" not in cap_out
    assert "#Promo" not in cap_out
    assert "🌟 EXCLUSIVE LECTURE" in cap_out
    assert "👨‍⚕️ Curated by Kind Doctor" in cap_out


def test_customize_caption_auto_hashtags_when_on(monkeypatch):
    monkeypatch.setenv("AUTO_HASHTAGS", "true")
    monkeypatch.setenv("STRIP_HASHTAGS", "false")
    cap_in2 = "Anatomy Lecture 05 on Upper Limb"
    cap_out2 = customize_caption(cap_in2)
    assert "#Anatomy" in cap_out2 or "#Lecture05" in cap_out2


def test_thumb_enforcer_fallback():
    te = ThumbEnforcer()
    t = te.get()
    assert t is not None
    assert os.path.exists(t)

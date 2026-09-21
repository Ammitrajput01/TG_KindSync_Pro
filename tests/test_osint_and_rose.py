"""
Comprehensive Unit & Integration Test Suite for Part 2:
- SangMata & OSINT Entity Resolver (GlobalOSINTResolver)
- Rose Style Group Notes Engine (_save_note, _get_note, _delete_note, _list_notes)
- Rose Style Group Filters Engine (_save_faq, _get_faq, _delete_faq, _list_faqs)
- SangMata Biometric Change Radar & History Tracker
"""

import os
import sys
import pytest
import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from devi.operator.telegram_bot import DeviTelegramBot
from devi.operator.osint_resolver import GlobalOSINTResolver, osint_resolver


@pytest.fixture
def bot_and_db(tmp_path):
    os.environ["DEVI_ADMIN_ID"] = "1553619403,759038032"
    os.environ["DEVI_TELEGRAM_BOT_TOKEN"] = "123456789:TEST_BOT_TOKEN"
    os.environ["TARGET_CHAT"] = "-1002124744363"
    
    bot = DeviTelegramBot()
    return bot


def test_osint_candidate_sessions():
    """Verify that GlobalOSINTResolver detects all available .session files."""
    resolver = GlobalOSINTResolver()
    sessions = resolver.get_candidate_sessions()
    assert isinstance(sessions, list)
    assert len(sessions) > 0
    # Expected candidate sessions
    assert any("session_" in s for s in sessions)


def test_rose_notes_crud(bot_and_db):
    """Verify Rose Notes CRUD lifecycle: Save, Get, List, Delete."""
    bot = bot_and_db
    chat_id = -100987654321
    admin_id = 1553619403

    # 1. Save note
    success = bot._save_note(chat_id, "syllabus", "MBBS Pathology & Pharmacology outline", admin_id)
    assert success is True

    # 2. Get note
    content = bot._get_note(chat_id, "syllabus")
    assert content == "MBBS Pathology & Pharmacology outline"

    # Case insensitivity & hash stripping
    content_upper = bot._get_note(chat_id, "#SYLLABUS")
    assert content_upper == "MBBS Pathology & Pharmacology outline"

    # 3. List notes
    notes = bot._list_notes(chat_id)
    assert len(notes) >= 1
    assert any(n["note_name"] == "syllabus" for n in notes)

    # 4. Update note
    bot._save_note(chat_id, "syllabus", "Updated 2026 Curriculum", admin_id)
    assert bot._get_note(chat_id, "syllabus") == "Updated 2026 Curriculum"

    # 5. Delete note
    deleted = bot._delete_note(chat_id, "syllabus")
    assert deleted is True
    assert bot._get_note(chat_id, "syllabus") is None


def test_rose_filters_crud(bot_and_db):
    """Verify Rose Filters CRUD lifecycle."""
    bot = bot_and_db
    chat_id = -100987654321
    admin_id = 1553619403

    # 1. Save filter
    bot._save_faq(chat_id, "books", "Download medical ebooks from topic #10", admin_id)

    # 2. Get filter
    reply = bot._get_faq(chat_id, "books")
    assert reply == "Download medical ebooks from topic #10"

    # 3. List filters
    filters = bot._list_faqs(chat_id)
    assert len(filters) >= 1
    assert any(f["keyword"] == "books" for f in filters)

    # 4. Delete filter
    deleted = bot._delete_faq(chat_id, "books")
    assert deleted is True
    assert bot._get_faq(chat_id, "books") is None


def test_sangmata_dossier_formatting(bot_and_db):
    """Verify SangMata dossier formatting with shift velocity and risk badge."""
    bot = bot_and_db
    sample_dossier = {
        "user_id": 123456789,
        "full_name": "Dr. Rajput",
        "username": "rajput_md",
        "phone": "+919876543210",
        "is_premium": True,
        "language": "en",
        "total_messages": 75,
        "changes_count": 4,
        "first_seen": "2026-01-10 10:00:00",
        "name_history": [
            {"name": "Amit", "changed_at": "2026-01-15 12:00"},
            {"name": "Dr. Amit", "changed_at": "2026-02-20 15:30"}
        ],
        "username_history": [
            {"username": "amit_old", "changed_at": "2026-01-15 12:00"},
            {"username": "amit_doc", "changed_at": "2026-02-20 15:30"}
        ]
    }

    card = bot._format_sangmata_dossier(sample_dossier, title_prefix="SANGMATA AUDIT")
    assert "123456789" in card
    assert "Dr. Rajput" in card
    assert "@rajput_md" in card
    assert "Telegram Premium" in card
    assert "Amit" in card
    assert "@amit_old" in card
    assert "High Velocity" in card or "Watchlist" in card
    assert "Kind Doctor Live Sentinel" in card


def test_osint_local_sqlite_fallback():
    """Verify OSINT resolver fallback to SQLite dossier when offline."""
    resolver = GlobalOSINTResolver()
    res = resolver.resolve_from_local_db("1553619403")
    # Should resolve or return None gracefully without crashing
    if res:
        assert "user_id" in res
        assert res["source"] == "local_sqlite_dossier"

    sangmata_hist = resolver.get_sangmata_history(1553619403)
    assert isinstance(sangmata_hist, dict)
    assert "name_history" in sangmata_hist
    assert "username_history" in sangmata_hist

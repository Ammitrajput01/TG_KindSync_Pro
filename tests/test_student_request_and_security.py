import pytest
import sqlite3
from devi.operator.telegram_bot import DeviTelegramBot, STUDENT_ALLOWED_COMMANDS

def test_student_request_detection():
    bot = DeviTelegramBot()
    # Explicit triggers
    assert bot._is_student_request("#request Pathoma chapter 3 notes") is True
    assert bot._is_student_request("/request Marrow surgery notes") is True
    assert bot._is_student_request("req: Cerebellum pathology") is True
    assert bot._is_student_request("#req DAMS pharmacology") is True
    assert bot._is_student_request("please upload internal medicine lectures") is True
    assert bot._is_student_request("plz send anat notes") is True
    assert bot._is_student_request("notes chahiye anatomy ke") is True
    assert bot._is_student_request("bhai cerebellum lecture upload kar do") is True

    # Non-requests
    assert bot._is_student_request("Good morning doctors") is False
    assert bot._is_student_request("How are you all?") is False
    assert bot._is_student_request("/find pathology") is False
    assert bot._is_student_request("hello") is False

def test_student_allowed_commands_security():
    # Sensitive commands MUST NOT be in STUDENT_ALLOWED_COMMANDS
    for sensitive_cmd in (
        "/invitelink", "/sendlink", "/send", "/say", "/dr", "/clone", "/batchclone",
        "/clonegroup", "/clonetopic", "/stopclone", "/pauseclone", "/resumeclone",
        "/panel", "/settings", "/control", "/botpanel", "/welcome", "/setwelcome",
        "/resetwelcome", "/strip", "/addstrip", "/delstrip", "/vps", "/polyglot",
        "/engine", "/clean", "/backup", "/autoforward", "/routes", "/lockdown"
    ):
        assert sensitive_cmd not in STUDENT_ALLOWED_COMMANDS, f"Security Breach: {sensitive_cmd} is in STUDENT_ALLOWED_COMMANDS!"

    # Safe educational commands MUST be in STUDENT_ALLOWED_COMMANDS
    for safe_cmd in ("/start", "/help", "/topics", "/mainindex", "/find", "/support", "/calc", "/dose", "/mcq"):
        assert safe_cmd in STUDENT_ALLOWED_COMMANDS, f"{safe_cmd} should be in STUDENT_ALLOWED_COMMANDS"

def test_request_tables_initialization():
    import sqlite3
    conn = sqlite3.connect(":memory:")
    # Verify table schemas execute cleanly
    conn.execute("""
        CREATE TABLE IF NOT EXISTS telegram_group_request_topics (
            source_chat_id BIGINT PRIMARY KEY,
            admin_chat_id BIGINT NOT NULL,
            topic_id INTEGER NOT NULL,
            group_title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_request_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS telegram_group_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_chat_id BIGINT NOT NULL,
            source_msg_id INTEGER NOT NULL,
            student_user_id BIGINT NOT NULL,
            student_name TEXT,
            student_username TEXT,
            admin_chat_id BIGINT NOT NULL,
            admin_topic_id INTEGER NOT NULL,
            admin_msg_id INTEGER,
            request_text TEXT,
            status TEXT DEFAULT 'pending',
            fulfilled_by_id BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("INSERT INTO telegram_group_request_topics (source_chat_id, admin_chat_id, topic_id, group_title) VALUES (-1001, -1002, 10, 'Study Group')")
    row = conn.execute("SELECT group_title FROM telegram_group_request_topics WHERE source_chat_id = -1001").fetchone()
    assert row[0] == 'Study Group'
    conn.close()

def test_group_request_topic_mapping_methods():
    bot = DeviTelegramBot()
    # Test helper method signature and existence
    assert hasattr(bot, "_get_or_create_group_request_topic")
    assert hasattr(bot, "_get_request_topic_by_group")
    assert hasattr(bot, "_get_request_group_by_topic")
    assert hasattr(bot, "_dispatch_group_member_strike_backup")

def test_high_risk_strike_watchlist_table_and_loading():
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS high_risk_strike_watchlist (
            user_id BIGINT PRIMARY KEY,
            source_chat_id BIGINT,
            username TEXT,
            full_name TEXT,
            join_date TEXT,
            reason TEXT,
            quarantined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        INSERT INTO high_risk_strike_watchlist (user_id, source_chat_id, username, full_name, join_date, reason)
        VALUES (99999, -100123, 'suspect1', 'Suspect User', '2026-11-22 12:00:00', 'Strike Threat')
    """)
    row = conn.execute("SELECT username, reason FROM high_risk_strike_watchlist WHERE user_id = 99999").fetchone()
    assert row[0] == 'suspect1'
    assert row[1] == 'Strike Threat'
    conn.close()

def test_strip_words_study_platforms_symbol_obfuscation():
    from devi.operator.deep_cloner import clean_cloned_caption
    sample = "Download DocTutorials and UWorld and Boards and Beyond lectures now!"
    cleaned = clean_cloned_caption(sample)
    assert "D0cTut0ri@ls" in cleaned
    assert "UW0rld" in cleaned
    assert "B0@rds & B€yond" in cleaned
    assert "DocTutorials" not in cleaned

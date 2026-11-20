"""
Unit test suite for Kind Doctor Mission Control Forum Hub & Dynamic Student Ticket Routing.
Verifies:
1. SQLite tables initialization (telegram_admin_forum_config, telegram_support_tickets, telegram_support_messages)
2. Mission Control config saving and fetching
3. Student ticket creation, lookup by user_id and topic_id
4. Ticket status lifecycle (open -> closed -> reopen)
5. Incremental message counters
6. Open ticket queue querying for /inbox HUD
"""
import pytest
import sqlite3
from unittest.mock import AsyncMock, patch, MagicMock
from devi.operator.telegram_bot import DeviTelegramBot, DB_PATH

@pytest.fixture
def test_bot():
    bot = DeviTelegramBot()
    # Ensure test tables exist in DB
    bot._init_db()
    return bot

def test_mission_control_config_lifecycle(test_bot):
    # Test saving mission control config
    test_chat = -100987654321
    t_joins = 101
    t_radar = 102
    t_cloner = 103
    t_briefings = 104

    test_bot._save_mission_control_config(test_chat, t_joins, t_radar, t_cloner, t_briefings)

    conf = test_bot._get_mission_control_config()
    assert conf is not None
    assert conf["chat_id"] == test_chat
    assert conf["topic_joins_id"] == t_joins
    assert conf["topic_radar_id"] == t_radar
    assert conf["topic_cloner_id"] == t_cloner
    assert conf["topic_briefings_id"] == t_briefings

def test_student_ticket_mapping_and_resolution(test_bot):
    student_id = 9988776655
    topic_id = 555
    topic_title = "👨‍🎓 Dr. Test Student (@test_stud)"

    # Create ticket
    test_bot._upsert_student_ticket(student_id, topic_id, topic_title, status="open")

    # Verify lookup by student ID
    tk = test_bot._get_student_ticket(student_id)
    assert tk is not None
    assert tk["topic_id"] == topic_id
    assert tk["topic_title"] == topic_title
    assert tk["status"] == "open"

    # Verify reverse lookup by topic ID
    resolved_uid = test_bot._get_student_by_topic(topic_id)
    assert resolved_uid == student_id

    # Test counter increments
    test_bot._increment_ticket_count(student_id, inbound=True)
    test_bot._increment_ticket_count(student_id, inbound=True)
    test_bot._increment_ticket_count(student_id, inbound=False)

    tk_updated = test_bot._get_student_ticket(student_id)
    assert tk_updated["total_inbound"] >= 2
    assert tk_updated["total_outbound"] >= 1

    # Test status update (close ticket)
    test_bot._update_ticket_status(student_id, "closed")
    tk_closed = test_bot._get_student_ticket(student_id)
    assert tk_closed["status"] == "closed"

    # Test reopening
    test_bot._update_ticket_status(student_id, "open")
    tk_reopened = test_bot._get_student_ticket(student_id)
    assert tk_reopened["status"] == "open"

def test_open_tickets_queue_for_inbox(test_bot):
    # Insert multiple test tickets
    for i in range(1, 4):
        test_bot._upsert_student_ticket(1000 + i, 200 + i, f"👨‍🎓 Student {i}", status="open")

    open_tks = test_bot._get_open_tickets(limit=10)
    assert len(open_tks) >= 3
    user_ids = [t["user_id"] for t in open_tks]
    assert 1001 in user_ids
    assert 1002 in user_ids
    assert 1003 in user_ids

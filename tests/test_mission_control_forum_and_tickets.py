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

@pytest.mark.asyncio
async def test_admin_reply_relayed_from_topic_to_student(test_bot):
    mc_chat = -1003942399840
    student_id = 1659687042
    topic_id = 12
    admin_id = 1553619403

    # Setup config & ticket mapping
    test_bot._save_mission_control_config(mc_chat, 7, 8, 9, 10)
    test_bot._upsert_student_ticket(student_id, topic_id, "👨‍🎓 Pooja (@pooja_axis)", status="open")

    # Incoming message from Admin in forum topic
    msg = {
        "message_id": 9991,
        "from": {"id": admin_id, "username": "Kinddoctor4u", "first_name": "Kind"},
        "chat": {"id": mc_chat, "type": "supergroup", "title": "Kind Doctor HQ"},
        "message_thread_id": topic_id,
        "text": "Hlo hru ?"
    }

    mock_session = AsyncMock()
    with patch.object(test_bot, "_send_message", new_callable=AsyncMock) as mock_send:
        mock_send.return_value = 12345
        await test_bot._handle_incoming_message(mock_session, msg)

        # Verify delivery to student
        calls = [c for c in mock_send.call_args_list if c[0][1] == student_id]
        assert len(calls) == 1, "Expected exactly 1 message delivered to student"
        assert "Hlo hru ?" in calls[0][0][2]
        assert "Kind Doctor" in calls[0][0][2]

    # Verify ticket outbound counter incremented
    tk = test_bot._get_student_ticket(student_id)
    assert tk["total_outbound"] >= 1

@pytest.mark.asyncio
async def test_admin_close_command_in_topic(test_bot):
    mc_chat = -1003942399840
    student_id = 1659687042
    topic_id = 12
    admin_id = 1553619403

    test_bot._save_mission_control_config(mc_chat, 7, 8, 9, 10)
    test_bot._upsert_student_ticket(student_id, topic_id, "👨‍🎓 Pooja (@pooja_axis)", status="open")

    msg = {
        "message_id": 9992,
        "from": {"id": admin_id, "username": "Kinddoctor4u", "first_name": "Kind"},
        "chat": {"id": mc_chat, "type": "supergroup", "title": "Kind Doctor HQ"},
        "message_thread_id": topic_id,
        "text": "/close"
    }

    mock_session = AsyncMock()
    with patch.object(test_bot, "_close_forum_topic", new_callable=AsyncMock) as mock_close, \
         patch.object(test_bot, "_send_message", new_callable=AsyncMock) as mock_send:
        mock_close.return_value = True
        mock_send.return_value = 12346
        await test_bot._handle_incoming_message(mock_session, msg)

        mock_close.assert_called_once_with(mock_session, mc_chat, topic_id)
        tk = test_bot._get_student_ticket(student_id)
        assert tk["status"] == "closed"

def test_daily_joins_csv_generation(test_bot):
    # Insert test joins today
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR REPLACE INTO member_history (user_id, chat_id, full_name, username, join_date) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                     (888111, -1003912970546, "Dr. Alice", "alice_med"))
        conn.execute("INSERT OR REPLACE INTO member_history (user_id, chat_id, full_name, username, join_date) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                     (888222, -1003912970546, "Dr. Bob", "bob_med"))
        conn.commit()

    csv_bytes, filename, caption, count = test_bot._generate_daily_joins_report()
    assert count >= 2
    assert "daily_members_joined_" in filename
    assert filename.endswith(".csv")
    csv_str = csv_bytes.decode("utf-8")
    assert "888111" in csv_str
    assert "Dr. Alice" in csv_str
    assert "888222" in csv_str
    assert "DAILY MEMBER JOINS REPORT" in caption

def test_extract_topic_id_from_updates_telethon():
    from tg_kindsync_pro import extract_topic_id_from_updates
    from telethon.tl.types import Updates, UpdateChannel, UpdateNewChannelMessage, MessageService, MessageActionTopicCreate, PeerChannel

    # Test with normal updates
    m = MessageService(id=42, peer_id=PeerChannel(channel_id=123), action=MessageActionTopicCreate(title='Test Topic', icon_color=0), date=None)
    u1 = UpdateChannel(channel_id=123)
    u2 = UpdateNewChannelMessage(message=m, pts=1, pts_count=1)
    up = Updates(updates=[u1, u2], users=[], chats=[], date=None, seq=0)

    tid = extract_topic_id_from_updates(up, default_id=1)
    assert tid == 42

    # Test fallback with None or empty
    assert extract_topic_id_from_updates(None, default_id=99) == 99



import pytest
import sqlite3
import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from devi.operator.session_vault import (
    init_linked_sessions_table,
    save_linked_user_session,
    get_user_linked_session,
    get_all_active_linked_sessions,
    delete_linked_user_session
)
from devi.operator.group_scanner import extract_telegram_target

def test_linked_sessions_crud():
    init_linked_sessions_table()
    test_uid = 8877665544
    test_phone = "+919999988888"
    test_session = "1BJWTESTSTRINGSESSIONDUMMYFORTESTINGPURPOSESLONGERTHAN50CHARS..."
    
    # 1. Save
    res = save_linked_user_session(test_uid, test_phone, test_session, name="Dr. Test User", username="drtest")
    assert res is True
    
    # 2. Get
    s = get_user_linked_session(test_uid)
    assert s == test_session
    
    # 3. List
    all_s = get_all_active_linked_sessions()
    assert any(x["user_id"] == test_uid for x in all_s)
    
    # 4. Delete
    d = delete_linked_user_session(test_uid)
    assert d is True
    assert get_user_linked_session(test_uid) is None

def test_extract_telegram_target():
    # Link with +
    r1 = extract_telegram_target("https://t.me/+AbCdEfGh123")
    assert r1["type"] == "invite_hash"
    assert r1["value"] == "AbCdEfGh123"
    
    # Joinchat link
    r2 = extract_telegram_target("https://t.me/joinchat/xyz987")
    assert r2["type"] == "invite_hash"
    assert r2["value"] == "xyz987"
    
    # Channel username
    r3 = extract_telegram_target("https://t.me/ThePirateBayGroup")
    assert r3["type"] == "username"
    assert r3["value"] == "ThePirateBayGroup"
    
    # @Username
    r4 = extract_telegram_target("@KindDoc_bot")
    assert r4["type"] == "username"
    assert r4["value"] == "KindDoc_bot"
    
    # Numeric ID
    r5 = extract_telegram_target("-1003504807114")
    assert r5["type"] == "chat_id"
    assert r5["value"] == -1003504807114

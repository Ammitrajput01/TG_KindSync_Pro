"""
Regression & Integrity Test Suite for Group Cloner, State Sync, SQLite Tracking, and Search
"""

import os
import sys
import json
import sqlite3
import asyncio
from pathlib import Path

# Add project root to path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from tg_kindsync_pro import (
    _match_channel_query,
    _normalize_search_str,
    update_env_file,
    AppConfig,
    StateManager
)

def test_search_query_multi_token():
    print("[*] 1. Testing Multi-Token & Unicode Search...")
    sample_channels = [
        {"id": -1001928374650, "title": "Pirate Bay Medical 2026", "username": "piratemed"},
        {"id": -1001122334455, "title": "Johari MBBS 1st Year Anatomy", "username": "joharimbbs"},
        {"id": -1009988776655, "title": "डॉक्टर हेल्प ग्रुप Study 😉", "username": "doctorhelp"},
        {"id": -1005544332211, "title": "Cerebellum Rapid Revision V8", "username": None},
    ]

    # Substring search
    assert _match_channel_query(sample_channels[0], "pirate"), "Should match 'pirate'"
    # Multi-token search (different order)
    assert _match_channel_query(sample_channels[0], "2026 pirate medical"), "Should match multi-token words"
    # Hindi search
    assert _match_channel_query(sample_channels[2], "डॉक्टर"), "Should match Hindi unicode text"
    # Chat ID search with and without -100
    assert _match_channel_query(sample_channels[1], "-1001122334455"), "Should match full Chat ID"
    assert _match_channel_query(sample_channels[1], "1122334455"), "Should match partial numeric ID"
    # Username search
    assert _match_channel_query(sample_channels[1], "joharimbbs"), "Should match username"
    print("    [+] All Search & Filter queries passed perfectly!")

def test_env_in_memory_synchronization():
    print("[*] 2. Testing Env & In-Memory Synchronization...")
    test_src = "-1009876543210"
    test_tgt = "-1001234567890"
    test_rules = "-1009876543210:101:-1001234567890:201,-1009876543210:102:-1001234567890:202"

    from dotenv import set_key
    update_env_file(chat_id=test_src, topic_id=0, mode="1")
    update_env_file(chat_id=test_tgt, topic_id=0, mode="2")
    set_key(".env", "FORWARDING_RULES", test_rules)
    os.environ["FORWARDING_RULES"] = test_rules

    # Load AppConfig with override=True
    cfg = AppConfig.load(routing_mode=2)
    assert str(cfg.source_chat) == test_src, f"Expected {test_src}, got {cfg.source_chat}"
    assert str(cfg.target_chat) == test_tgt, f"Expected {test_tgt}, got {cfg.target_chat}"
    assert len(cfg.forwarding_rules) == 2, f"Expected 2 rules, got {len(cfg.forwarding_rules)}"
    assert cfg.forwarding_rules[0]["source_topic"] == 101, "First rule source topic should be 101"
    assert cfg.forwarding_rules[1]["target_topic"] == 202, "Second rule target topic should be 202"
    print("    [+] Env, os.environ, and AppConfig.load() synchronized accurately!")

async def test_sqlite_clone_session_persistence():
    print("[*] 3. Testing SQLite Topic Mapping Persistence...")
    state_mgr = StateManager()
    await state_mgr.start()
    
    src = "-1008888888888"
    tgt = "-1009999999999"
    await state_mgr.save_clone_topic_mapping(src, 10, tgt, 20, "Anatomy Intro", 150)
    await state_mgr.save_clone_topic_mapping(src, 11, tgt, 21, "Physiology Block", 230)
    
    topics = await state_mgr.get_clone_session_topics(src, tgt)
    assert len(topics) == 2, f"Expected 2 topics, got {len(topics)}"
    assert topics[0]["topic_title"] == "Anatomy Intro"
    assert topics[1]["topic_title"] == "Physiology Block"
    
    latest = await state_mgr.get_latest_clone_session()
    assert latest is not None
    assert latest["source_chat"] == src
    assert latest["target_chat"] == tgt
    
    await state_mgr.close()
    print("    [+] SQLite Cloner Topic Mapping and State Persistence verified!")

def run_regression_suite():
    print("\n========================================================")
    print("   GROUP CLONER & SEARCH INTEGRITY REGRESSION SUITE")
    print("========================================================\n")
    test_search_query_multi_token()
    test_env_in_memory_synchronization()
    asyncio.run(test_sqlite_clone_session_persistence())
    print("\n========================================================")
    print("   [OK] ALL 3 REGRESSION AUDIT GATES PASSED (100% HEALTHY)")
    print("========================================================\n")

if __name__ == "__main__":
    run_regression_suite()

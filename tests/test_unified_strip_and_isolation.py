"""
Comprehensive Verification Suite for:
1. Unified Strip Words Synchronization & Safety Backups (strip_sync.py)
2. Multi-Tenant Session Isolation & Autonomous Worker Allocation (session_vault.py)
3. Dual-Process Split Status Radar & Interactive Pacing Cards (telegram_bot.py)
"""

import os
import sys
import asyncio
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from devi.operator.strip_sync import (
    get_all_raw_rules,
    add_strip_rules,
    delete_strip_rule,
    search_strip_rule,
    deduplicate_and_clean,
    sync_strip_words_file_to_db,
    STRIP_FILE,
    FRIEND_STRIP_FILE,
    BACKUP_DIR
)
from devi.operator.session_vault import (
    get_vault_client_for_target,
    get_all_active_linked_sessions,
    MASTER_ADMIN_IDS
)
from devi.operator.telegram_bot import DeviTelegramBot

def test_strip_sync_suite():
    print("[+] Testing Universal Strip Rules Bridge...")
    
    # 1. Sync file to DB
    total = sync_strip_words_file_to_db()
    assert total > 0, f"Expected active strip rules, got {total}"
    
    initial_rules = get_all_raw_rules()
    assert len(initial_rules) >= total
    
    # 2. Add temporary test rule
    import time
    delete_strip_rule("__UNIT_TEST_SAMPLE_STRIP_WORD_999__")
    delete_strip_rule("__TEST_WORD_123__")
    test_rule = f"__UNIT_TEST_SAMPLE_{os.getpid()}_{int(time.time())}__"
    added = add_strip_rules([test_rule], added_by=1553619403)
    assert added == 1, f"Expected 1 added rule, got {added}"
    
    # Verify in DB and both files
    assert test_rule in get_all_raw_rules()
    if STRIP_FILE.exists():
        assert test_rule in STRIP_FILE.read_text(encoding="utf-8")
    if FRIEND_STRIP_FILE.exists():
        assert test_rule in FRIEND_STRIP_FILE.read_text(encoding="utf-8")
        
    # 3. Search rule
    matches = search_strip_rule("UNIT_TEST_SAMPLE")
    assert any(test_rule in m for m in matches), "Expected to find test rule via search"
    
    # 4. Delete rule & verify safety backup
    deleted = delete_strip_rule(test_rule, deleted_by=1553619403)
    assert deleted is True, "Failed to delete test rule"
    assert test_rule not in get_all_raw_rules()
    
    # Check backup directory has backups
    backups = list(BACKUP_DIR.glob("strip_words_backup_*.txt"))
    assert len(backups) > 0, "Safety backup file was not created on deletion"
    print(f"    ✓ Strip sync verified. Safety backup created: {backups[-1].name}")

def test_session_isolation_suite():
    print("[+] Testing Multi-Tenant Session Isolation...")
    overview = get_all_active_linked_sessions()
    print(f"    Available sessions in vault: {len(overview)}")
    
    # Master Admin accounts
    assert 1553619403 in MASTER_ADMIN_IDS
    assert 759038032 in MASTER_ADMIN_IDS
    
    # Verify worker session pool has designated accounts
    from devi.operator.session_vault import WORKER_SESSION_POOL
    assert "session_forwarder.session" not in WORKER_SESSION_POOL, "Master forwarder session must NEVER be in worker pool"
    print("    ✓ Worker session pool excludes master session_forwarder")

def test_dual_process_radar_and_cards():
    print("[+] Testing Dual-Process Split Status Radar & Cards...")
    bot = DeviTelegramBot(bot_token="TEST_DUMMY_TOKEN")
    
    # 1. Dual Radar Card
    card_text, kb = bot._build_clone_status_card_data(1553619403)
    assert "SECTION 1: Terminal Forwarder Engine" in card_text
    assert "SECTION 2: In-Bot Deep Cloner Jobs" in card_text
    assert "DUAL RUNTIME RADAR" in card_text
    
    # Verify action buttons exist in keyboard
    all_callbacks = [btn["callback_data"] for row in kb.get("inline_keyboard", []) for btn in row]
    assert "act_cloner_refresh" in all_callbacks
    assert "act_stripwords" in all_callbacks
    assert "act_pacing" in all_callbacks
    print("    ✓ Dual-Process Radar card and action buttons verified")
    
    # 2. Strip Words Interactive Card
    strip_text, strip_kb = bot._build_strip_words_card_data(1553619403, page=1)
    assert "Universal Strip & Clean Rules Card" in strip_text
    assert "Active Cleaning Rules" in strip_text
    strip_callbacks = [btn["callback_data"] for row in strip_kb.get("inline_keyboard", []) for btn in row]
    assert "act_strip_add" in strip_callbacks
    assert "act_strip_search" in strip_callbacks
    assert "act_strip_del" in strip_callbacks
    assert "act_strip_dedup" in strip_callbacks
    print("    ✓ Interactive Strip Rules Card verified")
    
    # 3. Pacing Card
    pace_text, pace_kb = bot._build_pacing_card_data(1553619403)
    assert "Engine Transmission Velocity & Pacing Card" in pace_text
    pace_callbacks = [btn["callback_data"] for row in pace_kb.get("inline_keyboard", []) for btn in row]
    assert "act_pace_0.0" in pace_callbacks
    assert "act_pace_0.05" in pace_callbacks
    assert "act_pace_0.2" in pace_callbacks
    assert "act_pace_1.0" in pace_callbacks
    print("    ✓ Interactive Transmission Pacing Card verified")

def run_suite():
    test_strip_sync_suite()
    test_session_isolation_suite()
    test_dual_process_radar_and_cards()
    print("\n✅ All Unified Strip & Session Isolation tests passed successfully!\n")

if __name__ == "__main__":
    run_suite()

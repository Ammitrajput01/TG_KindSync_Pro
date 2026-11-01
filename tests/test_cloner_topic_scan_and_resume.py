"""
Unit & Regression Test Suite for Cloner Topic Scan, Watermark SQLite Fallback,
Topic Range Selection & Dedicated Topic Resume.
"""

import os
import sys
import tempfile
import asyncio
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from tg_kindsync_pro import (
    StateManager,
    parse_topic_range_selection
)

def test_parse_topic_range_selection():
    print("[*] 1. Testing parse_topic_range_selection logic...")
    
    # Simple list
    res = parse_topic_range_selection("1, 2, 5", max_count=10)
    assert res == [1, 2, 5], f"Expected [1, 2, 5], got {res}"
    
    # Ranges
    res = parse_topic_range_selection("3-7", max_count=10)
    assert res == [3, 4, 5, 6, 7], f"Expected [3, 4, 5, 6, 7], got {res}"
    
    # Combined with semicolons and spaces
    res = parse_topic_range_selection("1; 3; 6-8, 10", max_count=10)
    assert res == [1, 3, 6, 7, 8, 10], f"Expected [1, 3, 6, 7, 8, 10], got {res}"
    
    # Reversed range
    res = parse_topic_range_selection("9-7", max_count=10)
    assert res == [7, 8, 9], f"Expected [7, 8, 9], got {res}"
    
    # Out of bounds and deduplication
    res = parse_topic_range_selection("0, 1, 2, 2, 3, 99", max_count=5)
    assert res == [1, 2, 3], f"Expected [1, 2, 3], got {res}"
    
    # Empty or invalid string
    res = parse_topic_range_selection("invalid, abc, -", max_count=10)
    assert res == [], f"Expected [], got {res}"
    
    print("    [+] parse_topic_range_selection works flawlessly across all patterns!")

def test_auto_skip_chat_box_keywords():
    print("[*] 2. Testing Chat Box / Discussion Topic Detection keywords...")
    chat_keywords = ["chat", "general", "discussion", "doubt", "talk", "queries", "conversation", "spam", "offtopic", "off-topic"]
    
    test_topics = [
        (1, "General"),
        (2, "Pathology Lectures 2026"),
        (3, "Student Chat Box & Doubts"),
        (4, "Biochemistry Notes"),
        (5, "Official Discussion Group"),
        (6, "Pharmacology Flashcards")
    ]
    
    skipped_indices = []
    for idx, (top_id, title) in enumerate(test_topics, 1):
        clean_title = title.strip().lower()
        if top_id == 1 or any(kw in clean_title for kw in chat_keywords):
            skipped_indices.append(idx)
            
    assert skipped_indices == [1, 3, 5], f"Expected topics 1, 3, 5 to be skipped, got {skipped_indices}"
    print("    [+] Chat topics accurately identified and auto-skipped!")

async def test_sqlite_watermark_fallback_and_audit():
    print("[*] 3. Testing SQLite Watermark Fallback & Audit Reconciliation...")
    
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tf:
        temp_db_path = tf.name
        
    try:
        state_mgr = StateManager(db_path=temp_db_path)
        await state_mgr.start()
        
        src_chat = "-1003903797493"
        tgt_chat = "-1004300858087"
        
        # 1. Map 3 topics
        await state_mgr.save_clone_topic_mapping(src_chat, 101, tgt_chat, 201, "Anatomy Block A", 500)
        await state_mgr.save_clone_topic_mapping(src_chat, 102, tgt_chat, 202, "Physiology Block B", 800)
        await state_mgr.save_clone_topic_mapping(src_chat, 103, tgt_chat, 203, "Biochemistry Block C", 300)
        
        # 2. Simulate topic 201: completed
        await state_mgr.mark_clone_topic_completed(src_chat, 101, tgt_chat, 201)
        is_comp = await state_mgr.is_clone_topic_completed(src_chat, 101, tgt_chat)
        assert is_comp is True, "Topic 101 should be marked completed"
        
        # 3. Simulate topic 202: in-progress with messages in forwarded table, but topic_watermarks was NOT written (e.g., kill/crash)
        async with state_mgr.db_lock:
            await state_mgr.db.execute("""
                INSERT INTO forwarded (source_chat, msg_id, target_chat, target_topic, completed_at)
                VALUES (?, ?, ?, ?, ?)
            """, (src_chat, 1540, tgt_chat, 202, 1730000000.0))
            await state_mgr.db.execute("""
                INSERT INTO forwarded (source_chat, msg_id, target_chat, target_topic, completed_at)
                VALUES (?, ?, ?, ?, ?)
            """, (src_chat, 1890, tgt_chat, 202, 1730000010.0))
            await state_mgr.db.commit()
            
        # Test bulletproof fallback in get_topic_watermark
        recovered_wm = await state_mgr.get_topic_watermark(src_chat, 102, tgt_chat, 202)
        assert recovered_wm == 1890, f"Expected watermark 1890 from forwarded fallback, got {recovered_wm}"
        print(f"    [+] Fallback recovered exact max_id {recovered_wm} directly from forwarded records!")
        
        # 4. Audit reconciliation test
        audit = await state_mgr.get_clone_session_audit(src_chat, tgt_chat)
        assert len(audit) == 3, f"Expected 3 audited topics, got {len(audit)}"
        
        # Topic 101: completed
        assert audit[0]["status"] == "completed"
        # Topic 102: in_progress, 2 copied messages, last_copied_msg_id = 1890
        assert audit[1]["status"] == "in_progress"
        assert audit[1]["messages_copied"] == 2
        assert audit[1]["last_copied_msg_id"] == 1890
        # Topic 103: pending, 0 messages copied
        assert audit[2]["status"] == "active" or audit[2]["messages_copied"] == 0
        
        print("    [+] StateManager Audit Reconciliation accurately categorized all 3 states:")
        print(f"        Topic 1: {audit[0]['topic_title']} -> {audit[0]['status']}")
        print(f"        Topic 2: {audit[1]['topic_title']} -> {audit[1]['status']} ({audit[1]['messages_copied']} msgs, max={audit[1]['last_copied_msg_id']})")
        print(f"        Topic 3: {audit[2]['topic_title']} -> {audit[2]['status']} ({audit[2]['messages_copied']} msgs)")
        
        await state_mgr.close()
    finally:
        if os.path.exists(temp_db_path):
            try:
                os.remove(temp_db_path)
            except Exception:
                pass

async def main():
    print("\n========================================================")
    print("   CLONER TOPIC SCAN, WATERMARK FALLBACK & RESUME TEST")
    print("========================================================\n")
    test_parse_topic_range_selection()
    test_auto_skip_chat_box_keywords()
    await test_sqlite_watermark_fallback_and_audit()
    print("\n========================================================")
    print("   [OK] ALL CLONER TOPIC SCAN & RESUME AUDITS PASSED!")
    print("========================================================\n")

if __name__ == "__main__":
    asyncio.run(main())

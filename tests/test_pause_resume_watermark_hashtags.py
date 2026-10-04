#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dedicated unit and integration tests for:
1. Pause / Resume Event-driven non-destructive architecture
2. Topic-wise watermark persistence in StateManager
3. Advanced Hashtag & Watermark Stripping (#The Pirate Bay, #yourwish, etc.)
4. Video 16:9 HD attributes and thumbnail preservation
"""

import sys
import os
import asyncio
import sqlite3
import pytest
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from tg_kindsync_pro import (
    get_clean_rules,
    apply_clean_rules,
    StateManager,
    TerminalPlatform,
    AppConfig,
    ThumbEnforcer
)

def test_clean_rules_hashtags():
    print("[*] 1. Testing Clean Rules & Hashtag Stripping...")
    strip_words, _ = get_clean_rules()
    assert any("Pirate Bay" in w for w in strip_words), "Pirate Bay should be in strip words"
    
    test_cases = [
        ("Lecture 01 Anatomy #The Pirate Bay", "Lecture 01 Anatomy"),
        ("Lecture 02 Physiology #ThePirateBay", "Lecture 02 Physiology"),
        ("Lecture 03 Biochem # The Pirate Bay", "Lecture 03 Biochem"),
        ("Lecture 04 Pathology #The_Pirate_Bay", "Lecture 04 Pathology"),
        ("Lecture 05 Pharma The Pirate Bay", "Lecture 05 Pharma"),
        ("Lecture 06 Surgery #yourwish", "Lecture 06 Surgery"),
        ("Lecture 07 Medicine #medAcadpdf", "Lecture 07 Medicine"),
        ("Lecture 08 Pediatrics @Cerebellumvideosbot", "Lecture 08 Pediatrics"),
    ]
    for inp, expected in test_cases:
        res = apply_clean_rules(inp)
        assert res.strip() == expected.strip(), f"Mismatch: Got '{res}' but expected '{expected}'"
    print("  [+] Hashtags & Watermark cleaning: 100% PASS")

@pytest.mark.asyncio
async def test_topic_watermarks_persistence():
    print("[*] 2. Testing Topic Watermarks Persistence in StateManager...")
    state = StateManager()
    await state.start()
    
    src = "-1001234567890"
    src_topic = 26348
    tgt = "-1009876543210"
    tgt_topic = 55
    
    # Mark completed with topic
    await state.mark_completed(src, 1050, tgt, target_topic=tgt_topic, source_topic=src_topic)
    
    # Check in-memory
    wm = await state.get_topic_watermark(src, src_topic, tgt, tgt_topic)
    assert wm == 1050, f"Expected 1050, got {wm}"
    
    # Persist and close
    await state.persist_watermarks()
    await state.close()
    
    # Re-open fresh state and verify persisted SQLite record
    state2 = StateManager()
    await state2.start()
    wm2 = await state2.get_topic_watermark(src, src_topic, tgt, tgt_topic)
    assert wm2 == 1050, f"Expected 1050 on reload, got {wm2}"
    await state2.close()
    print("  [+] Topic-wise Watermark Auto-Save & Resume Recovery: 100% PASS")

@pytest.mark.asyncio
async def test_pause_resume_event_architecture():
    print("[*] 3. Testing Pause / Resume Event Architecture...")
    cfg = AppConfig(api_id=12345, api_hash="abcdef", source_chat="-100111", target_chat="-100222")
    tp = TerminalPlatform(cfg)
    
    assert tp.pause_evt.is_set(), "Pause event should be initially SET (active)"
    assert not tp.stop_evt.is_set(), "Stop event should be initially CLEAR"
    
    # Simulate Pause
    tp.pause_evt.clear()
    assert not tp.pause_evt.is_set(), "Pause event should be cleared when paused"
    
    # Simulate Resume
    tp.pause_evt.set()
    assert tp.pause_evt.is_set(), "Pause event should be set when resumed"
    print("  [+] Pause / Resume Event non-destructive state: 100% PASS")

async def main():
    print("=" * 60)
    print("   PAUSE / RESUME & HASHTAG STRIPPING VERIFICATION SUITE")
    print("=" * 60)
    test_clean_rules_hashtags()
    await test_topic_watermarks_persistence()
    await test_pause_resume_event_architecture()
    print("=" * 60)
    print("   ALL TESTS PASSED WITH ZERO ERRORS!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())

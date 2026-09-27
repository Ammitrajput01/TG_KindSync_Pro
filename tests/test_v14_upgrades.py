#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification tests for V14.0 Upgrades:
1. Smart caption deduplication (repeated titles, brandings, blank lines).
2. Live Speedometer IPC telemetry read/write.
3. Research insight dates, unread counts, and dismiss endpoints.
"""

import os
import sys
import json
import time
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tg_kindsync_pro import (
    smart_clean_and_deduplicate_caption,
    customize_caption,
    _canonical_line_key
)
from web_dashboard import DashboardServer, ENGINE_TELEMETRY_FILE, DISMISSED_INSIGHTS_FILE
from devi.sentinel.telemetry_bridge import ObserverState


def test_caption_deduplication():
    print("Testing Caption Deduplication...")
    raw_caption = """
    Anesthesia Lecture 01
    Anesthesia Lecture 01
    By Study Help
    By Study Help
    
    
    Join our channel for more updates
    Key points:
    - Point A
    - Point A
    """
    cleaned = smart_clean_and_deduplicate_caption(raw_caption, signature="📚 Kind Doctor\n💬 Study Help")
    print(f"Cleaned output:\n---\n{cleaned}\n---")
    
    # Assertions
    assert "By Study Help" not in cleaned, "Branding in signature should be stripped from body"
    assert cleaned.count("Point A") == 1, "Duplicate bullet points should be reduced to 1"
    assert "\n\n\n" not in cleaned, "Consecutive empty lines should be collapsed"
    
    # Test customize_caption formatting
    formatted = customize_caption("Anesthesia Lecture 01\nAnesthesia Lecture 01")
    print(f"Formatted customize_caption:\n---\n{formatted}\n---")
    assert "🎬 **Title**: Anesthesia Lecture 01" in formatted
    assert formatted.count("Anesthesia Lecture 01") == 1, "Title must not be repeated right after title line"
    print("✅ Caption deduplication PASSED!\n")


def test_engine_telemetry_and_dashboard_status():
    print("Testing Engine Telemetry & Dashboard status...")
    state = ObserverState()
    server = DashboardServer(state)
    
    # Write mock telemetry
    ENGINE_TELEMETRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    mock_data = {
        "timestamp": time.time(),
        "active_file_name": "Surgery_Lecture_04.mp4",
        "active_file_progress": 68.5,
        "active_file_transferred": "685.0 MB",
        "active_file_total": "1.00 GB",
        "active_file_eta": "0m 18s",
        "current_speed_mb": 18.75,
        "peak_speed_mb": 22.40,
        "is_transferring": True
    }
    with open(ENGINE_TELEMETRY_FILE, "w", encoding="utf-8") as f:
        json.dump(mock_data, f)
        
    status = server._build_status_dict()
    print(f"Status output: current_speed={status['current_speed_mb']}, peak_speed={status['peak_speed_mb']}, active_file={status['active_file_name']}")
    
    assert status["current_speed_mb"] == 18.75
    assert status["peak_speed_mb"] == 22.40
    assert status["active_file_name"] == "Surgery_Lecture_04.mp4"
    assert status["is_transferring"] is True
    print("✅ Live telemetry & Speedometer status PASSED!\n")


def test_research_dismissal():
    print("Testing Research Insights Dismissal...")
    state = ObserverState()
    server = DashboardServer(state)
    
    # Clear dismissed for test
    if DISMISSED_INSIGHTS_FILE.exists():
        os.remove(DISMISSED_INSIGHTS_FILE)
        
    initial_status = server._build_status_dict()
    initial_count = initial_status.get("unread_insights_count", 0)
    print(f"Initial unread research count: {initial_count}")
    
    # Dismiss RES-BAN-001
    server._dismiss_insight("RES-BAN-001")
    new_status = server._build_status_dict()
    print(f"After dismissing 1 item: count = {new_status.get('unread_insights_count', 0)}")
    assert new_status.get("unread_insights_count", 0) == max(0, initial_count - 1)
    
    # Dismiss All
    server._dismiss_insight(all_flag=True)
    final_status = server._build_status_dict()
    print(f"After dismiss all: count = {final_status.get('unread_insights_count', 0)}")
    assert final_status.get("unread_insights_count", 0) == 0
    print("✅ Research insights dismissal PASSED!\n")


if __name__ == "__main__":
    test_caption_deduplication()
    test_engine_telemetry_and_dashboard_status()
    test_research_dismissal()
    print("🎉 ALL V14 UPGRADE TESTS COMPLETED SUCCESSFULLY!")

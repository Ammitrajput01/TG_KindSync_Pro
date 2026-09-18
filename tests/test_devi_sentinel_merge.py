"""
Verification Test for DEVI Sentinel Integration & Unification
"""

import os
import sys
import asyncio
import tempfile
from pathlib import Path
import pytest

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from devi.sentinel.telemetry_bridge import (
    ObserverState,
    SentinelTelemetryBridge,
    read_db_metrics,
    create_db_snapshot
)
from devi.sentinel.ai_advisor import SentinelAIAdvisor
from devi.brain.intent_engine import IntentEngine
from devi.brain.model_router import ModelRouter
from devi.config import DEVI_NAME

@pytest.mark.asyncio
async def test_sentinel_telemetry():
    print("[*] 1. Testing Sentinel Telemetry Bridge...")
    state = ObserverState()
    state.add_event("Engine started")
    state.add_recommendation("Balanced mode active")
    assert len(state.recent_events) == 1
    assert len(state.recommendations) >= 1

    # Test read-only DB metrics
    metrics = read_db_metrics()
    assert "total_forwarded" in metrics
    assert "tracked_channels" in metrics
    print(f"    [+] DB Metrics query successful: {metrics['total_forwarded']} records tracked.")

    # Test snapshot backup
    with tempfile.TemporaryDirectory() as tmpdir:
        snap = create_db_snapshot(report_dir=Path(tmpdir))
        assert snap.exists()
        assert snap.stat().st_size > 0
        snap.unlink()
    print("    [+] Online SQLite snapshot backup verified.")

def test_log_stream_parser():
    print("[*] 2. Testing Sentinel Log Forensics Parser...")
    state = ObserverState()
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, encoding="utf-8") as f:
        log_path = Path(f.name)
        f.write("⚡ 18.5 MB/s transfer speed\n")
        f.write("Subject Header Posted: ANATOMY LECTURES\n")
        f.write("Video: lecture_01.mp4 transferred successfully\n")
        f.write("Sleeping early for 15s due to flood wait\n")

    try:
        bridge = SentinelTelemetryBridge(state, log_file=log_path)
        events = bridge.poll_logs(from_start=True)
        assert state.peak_speed_mb == 18.5
        assert state.current_subject == "ANATOMY LECTURES"
        assert state.videos_sent == 1
        assert state.flood_waits_detected == 1
        assert state.flood_wait_seconds_total == 15.0
        assert len(events) == 3
        print(f"    [+] Log stream parser parsed 3 forensic events correctly.")
    finally:
        if log_path.exists():
            log_path.unlink()

def test_ai_advisor():
    print("[*] 3. Testing DEVI AI Advisor...")
    state = ObserverState()
    state.flood_waits_detected = 4
    state.peak_speed_mb = 22.0
    state.total_transfers = 50
    state.videos_sent = 30
    state.docs_sent = 20

    advisor = SentinelAIAdvisor()
    tips = advisor.generate_dynamic_recommendations(state)
    assert len(tips) >= 2
    assert any("Balanced Mode" in t for t in tips)
    print(f"    [+] Dynamic recommendations generated: {len(tips)} tips.")

    digest = advisor.build_daily_digest(state, {"total_forwarded": 1500, "tracked_channels": 4})
    assert DEVI_NAME in digest
    assert "TRANSFER & VELOCITY METRICS" in digest
    print("    [+] Structured 24h AI performance digest verified.")

@pytest.mark.asyncio
async def test_telegram_intent_parsing():
    print("[*] 4. Testing DEVI Saved Messages Conversational Intent Routing...")
    intent_engine = IntentEngine()

    q1 = intent_engine.parse_intent("Devi, speed कैसी चल रही है?")
    assert q1["intent"] == "SHOW_STATUS"

    q2 = intent_engine.parse_intent("System health check karo")
    assert q2["intent"] == "CHECK_HEALTH"

    q3 = intent_engine.parse_intent("Research anti ban protocols")
    assert q3["intent"] == "RESEARCH_TOPIC"
    assert "anti ban" in q3["topic"]

    print("    [+] Natural language intents mapped to DEVI operations successfully.")

def test_sentinel_observer_module_import():
    print("[*] 5. Testing sentinel_observer.py module import...")
    import sentinel_observer
    assert hasattr(sentinel_observer, "render_observer_hud")
    assert hasattr(sentinel_observer, "main")
    assert hasattr(sentinel_observer, "TelegramReporter")
    print("    [+] sentinel_observer.py unified module verified and backwards-compatible.")

async def main():
    print("==================================================")
    print("   DEVI + SENTINEL MERGE VERIFICATION SUITE")
    print("==================================================")
    await test_sentinel_telemetry()
    test_log_stream_parser()
    test_ai_advisor()
    await test_telegram_intent_parsing()
    test_sentinel_observer_module_import()
    print("\n[OK] ALL DEVI + SENTINEL MERGE VERIFICATIONS PASSED!")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(main())

"""
DEVI Master Test Runner
Executes all verification suites across all evolution phases and sentinel integration.
"""

import sys
import asyncio
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Import test runners
from tests.test_devi_phase1 import run_verification as run_phase1
from tests.test_devi_phase2 import run_phase2_verification as run_phase2
from tests.test_devi_phase3 import run_phase3_verification as run_phase3
from tests.test_devi_phase4 import run_phase4_verification as run_phase4
from tests.test_devi_phase5 import run_phase5_verification as run_phase5
from tests.test_devi_sentinel_merge import main as run_sentinel_merge
from tests.test_multi_login import run_multi_login_suite
from tests.test_pause_resume_watermark_hashtags import main as run_pause_resume_suite
from tests.test_unified_strip_and_isolation import run_suite as run_strip_and_isolation_suite
from tests.test_media_downloader import run_media_downloader_suite
from tests.test_master_vrob_and_cdss import main as run_vrob_and_cdss_suite
from tests.test_kind_doctor_upgrades import (
    test_telegram_bot_name_sync,
    test_unified_branding_toggle_logic,
    test_kindsync_unified_clean_mode,
    test_uncapped_media_velocity,
    test_stripping_always_active
)

def run_kind_doctor_suite():
    test_telegram_bot_name_sync()
    test_unified_branding_toggle_logic()
    test_kindsync_unified_clean_mode()
    test_uncapped_media_velocity()
    test_stripping_always_active()

async def run_all():
    print("\n========================================================")
    print("       DEVI MASTER SYSTEM VERIFICATION SUITE")
    print("========================================================\n")

    suites = [
        ("Phase 1: Foundation, Brain & Sandbox", run_phase1),
        ("Phase 2: Research, Skill Discovery & Testing", run_phase2),
        ("Phase 3: Telemetry, Shield & Task Operator", run_phase3),
        ("Phase 4: Self-Healing & Web Dashboard", run_phase4),
        ("Phase 5: Compound ReAct & Evolution Daemon", run_phase5),
        ("Sentinel Merge: Live Watchdog & Telegram Remote", run_sentinel_merge),
        ("Multi-Login: Dual RBAC & Telegram Multi-Session", run_multi_login_suite),
        ("Kind Doctor Upgrades: Bot Name, Unified Branding & Pacing", run_kind_doctor_suite),
        ("Pause/Resume, Watermark Persistence & Hashtag Stripping", run_pause_resume_suite),
        ("Unified Strip Rules, Session Isolation & Dual Radar", run_strip_and_isolation_suite),
        ("Universal In-Topic Media Downloader Engine", run_media_downloader_suite),
        ("Virtual Reorder Buffer (VROB), Biometric Vault & CDSS", run_vrob_and_cdss_suite),
    ]

    passed = 0
    failed = 0

    for name, runner in suites:
        print(f"\n>>> Running: {name} <<<")
        try:
            if asyncio.iscoroutinefunction(runner):
                await runner()
            else:
                runner()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name} encountered error: {e}")
            failed += 1

    print("\n========================================================")
    print(f"   SUMMARY: {passed} PASSED | {failed} FAILED (Total: {len(suites)})")
    if failed == 0:
        print("   STATUS: ALL SYSTEM COMPONENTS ARE 100% HEALTHY!")
    else:
        print("   STATUS: SOME TESTS FAILED. PLEASE CHECK LOGS.")
    print("========================================================\n")
    return failed == 0

if __name__ == "__main__":
    success = asyncio.run(run_all())
    sys.exit(0 if success else 1)

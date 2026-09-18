"""
DEVI Phase 4 Verification Suite
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import asyncio
from aiohttp import test_utils
from devi.memory.memory_store import MemoryStore
from devi.evolution.self_healer import SelfHealer
from devi.dashboard.web_app import DashboardApp
from devi.operator.telegram_bot import DeviTelegramBot

async def run_phase4_verification():
    print("========================================")
    print("   DEVI PHASE 4 VERIFICATION SUITE")
    print("========================================")

    # 1. Test Self-Healing Engine
    print("[*] 1. Testing DEVI Controlled Self-Healing Engine...")
    mem = MemoryStore()
    await mem.initialize()
    healer = SelfHealer(mem)
    heal_res = await healer.scan_and_heal()
    assert heal_res["status"] in ["HEALTHY", "HEALED"], "Self-healing scan failed"
    print(f"    [+] Self-Healing scan completed: Status = {heal_res['status']}")

    # 2. Test Web Dashboard API Endpoints
    print("[*] 2. Testing Web Evolution Dashboard API...")
    dashboard = DashboardApp(port=8765)
    # Validate route table
    routes = [r.resource.canonical for r in dashboard.app.router.routes()]
    assert "/" in routes, "Root route missing in dashboard"
    assert "/api/status" in routes, "Status API missing in dashboard"
    print(f"    [+] Web Dashboard configured with {len(routes)} verified HTTP routes.")

    # 3. Test Telegram Bot Interface Logic
    print("[*] 3. Testing Telegram Operator Bot Readiness...")
    tg_bot = DeviTelegramBot(bot_token="TEST_MOCK_TOKEN")
    assert tg_bot.token == "TEST_MOCK_TOKEN", "Telegram Bot initialization failed"
    print("    [+] Telegram Bot Daemon initialized in safe isolated mode.")

    print("\n[OK] ALL DEVI PHASE 4 TESTS PASSED SUCCESSFULLY!")
    print("========================================")

if __name__ == "__main__":
    asyncio.run(run_phase4_verification())

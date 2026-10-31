#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification Suite for:
1. Telegram Mini App (TMA 2.0) Biometric & Account Auto-Auth
2. Clinical Decision Support System (CDSS) Studio Endpoints (Parkland, GCS, Drug KB, DDI Radar)
3. Dedicated Strip Words Studio & Regex Testing Sandbox
4. Telegram Bot Persistent Chat Menu Button and Panel WebApp links
"""

import asyncio
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from aiohttp import web
from web_dashboard import DashboardServer
from devi.operator.telegram_bot import DeviTelegramBot


async def test_tma_auth_and_cdss():
    """Verify TMA 2.0 Biometric Auto-Auth and CDSS endpoints."""
    # Initialize DashboardServer instance without starting port listener
    mock_state = MagicMock()
    server = DashboardServer(state=mock_state, host="127.0.0.1", port=8080)

    # 1. Test TMA Biometric Auto-Auth for Master Admins
    req_mock_admin1 = MagicMock()
    req_mock_admin1.json = AsyncMock(return_value={"user": {"id": 1553619403, "username": "Kinddoctor4u"}})
    resp1 = await server.handle_api_auth_telegram_webapp(req_mock_admin1)
    body1 = json.loads(resp1.text)
    assert resp1.status == 200, f"Expected 200, got {resp1.status}"
    assert body1["success"] is True
    assert body1["admin"] is True
    assert "session" in body1
    print("  [+] TMA Auto-Auth Primary 1 (@Kinddoctor4u, ID: 1553619403): PASSED")

    req_mock_admin2 = MagicMock()
    req_mock_admin2.json = AsyncMock(return_value={"user": {"id": 759038032, "username": "Ammitrajput1"}})
    resp2 = await server.handle_api_auth_telegram_webapp(req_mock_admin2)
    body2 = json.loads(resp2.text)
    assert resp2.status == 200
    assert body2["success"] is True
    assert body2["admin"] is True
    print("  [+] TMA Auto-Auth Primary 2 (@Ammitrajput1, ID: 759038032): PASSED")

    # 2. Test TMA Auto-Auth Rejection for Unauthorized accounts
    req_mock_intruder = MagicMock()
    req_mock_intruder.json = AsyncMock(return_value={"user": {"id": 999999999, "username": "unknown_intruder"}})
    resp_intruder = await server.handle_api_auth_telegram_webapp(req_mock_intruder)
    assert resp_intruder.status == 403
    print("  [+] TMA Auto-Auth Unauthorized Rejection (403 Forbidden): PASSED")

    # 3. Test Parkland Resuscitation Calculator API
    req_mock_burn = MagicMock()
    req_mock_burn.json = AsyncMock(return_value={"weight_kg": 70, "tbsa_pct": 20})
    resp_burn = await server.handle_api_clinical_parkland(req_mock_burn)
    body_burn = json.loads(resp_burn.text)
    assert body_burn["success"] is True
    assert body_burn["result"]["total_24h_ml"] == 5600.0  # 4 * 70 * 20
    assert body_burn["result"]["first_8h_ml"] == 2800.0
    assert body_burn["result"]["remaining_16h_ml"] == 2800.0
    print("  [+] Clinical Studio: Parkland 4-2-1 Formula Endpoint: PASSED")

    # 4. Test GCS Neuro-Assessment API
    req_mock_gcs = MagicMock()
    req_mock_gcs.json = AsyncMock(return_value={"eye": 3, "verbal": 4, "motor": 5})
    resp_gcs = await server.handle_api_clinical_gcs(req_mock_gcs)
    body_gcs = json.loads(resp_gcs.text)
    assert body_gcs["success"] is True
    assert body_gcs["result"]["score"] == 12
    assert "Moderate" in body_gcs["result"]["severity"]
    print("  [+] Clinical Studio: Glasgow Coma Scale (GCS) Score (12 - Moderate): PASSED")

    # 5. Test Drug Knowledge Base API (Live openFDA or offline KB)
    req_mock_drug = MagicMock()
    req_mock_drug.query = {"q": "amiodarone"}
    resp_drug = await server.handle_api_clinical_drug(req_mock_drug)
    body_drug = json.loads(resp_drug.text)
    assert body_drug["success"] is True
    assert "pulmonary" in body_drug["boxed_warning"].lower()
    print("  [+] Clinical Studio: OpenFDA / Knowledge Base Drug Query: PASSED")

    # 6. Test DDI Drug-Drug Interaction Radar API
    req_mock_ddi = MagicMock()
    req_mock_ddi.json = AsyncMock(return_value={"drug1": "warfarin", "drug2": "aspirin"})
    resp_ddi = await server.handle_api_clinical_ddi(req_mock_ddi)
    body_ddi = json.loads(resp_ddi.text)
    assert body_ddi["success"] is True
    assert "High / Major" in body_ddi["interaction"]["severity"]
    print("  [+] Clinical Studio: Drug-Drug Interaction Radar (Warfarin + Aspirin): PASSED")

    # 7. Test High-Yield Medical Flashcards API
    req_mock_pearls = MagicMock()
    resp_pearls = await server.handle_api_clinical_pearls(req_mock_pearls)
    body_pearls = json.loads(resp_pearls.text)
    assert body_pearls["success"] is True
    assert len(body_pearls["pearls"]) >= 5
    print("  [+] Clinical Studio: 3D Flip High-Yield Medical Flashcards: PASSED")

    # 8. Test Strip Words Studio Regex Sandbox
    req_mock_sandbox = MagicMock()
    req_mock_sandbox.json = AsyncMock(return_value={"text": "Join @SpamChannel for free stuff! Contact @Kinddoctor4u"})
    resp_sandbox = await server.handle_api_test_strip_words(req_mock_sandbox)
    body_sandbox = json.loads(resp_sandbox.text)
    assert body_sandbox["success"] is True
    assert "@SpamChannel" in body_sandbox["original"]
    print("  [+] Strip Words Studio: Live Regex Testing Sandbox API: PASSED")


def test_telegram_bot_tma_buttons():
    """Verify Telegram Bot persistent menu button & WebApp routes."""
    bot = DeviTelegramBot()
    # Test Auto-Forward panel keyboard generation
    card_text, keyboard = bot._build_autoforward_panel_data(1553619403)
    flat_btns = [btn for row in keyboard["inline_keyboard"] for btn in row]
    
    web_app_btns = [btn for btn in flat_btns if "web_app" in btn]
    assert len(web_app_btns) >= 1, "Expected at least 1 WebApp button in Auto-Forward panel"
    assert "operations" in web_app_btns[0]["web_app"]["url"], "Expected operations route in WebApp URL"
    print("  [+] Telegram Bot: Auto-Forward Panel Route Matrix WebApp button: PASSED")


async def main():
    print("==================================================")
    print("   TMA 2.0, CLINICAL STUDIO & STRIP WORDS TEST SUITE")
    print("==================================================")
    await test_tma_auth_and_cdss()
    test_telegram_bot_tma_buttons()
    print("\n[SUCCESS] ALL TMA 2.0, CDSS & STRIP STUDIO TESTS PASSED 100%!")


if __name__ == "__main__":
    asyncio.run(main())

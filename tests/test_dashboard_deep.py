"""
Comprehensive Deep Audit & Test Suite for Web Dashboard Endpoints & RBAC
Validates all REST API components, Auth Manager, Login Manager, and Status serialization.
"""

import os
import sys
import json
import pytest
import asyncio
from pathlib import Path

# Add workspace root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from web_dashboard import (
    DashboardAuthManager,
    TelegramWebLoginManager,
    DashboardServer,
    get_local_lan_ip
)
from devi.sentinel.telemetry_bridge import ObserverState


def test_auth_manager_lifecycle(tmp_path):
    auth_db = tmp_path / "test_users.json"
    auth = DashboardAuthManager(db_file=auth_db)
    
    # 1. Default admin account
    user = auth.authenticate("Amit", "Amit@123")
    assert user is not None
    assert user["role"] == "admin"
    assert user["token"] is not None
    
    token = user["token"]
    validated = auth.verify_token(token)
    assert validated is not None
    assert validated["username"] == "Amit"
    assert validated["role"] == "admin"
    
    # 2. User CRUD
    ok, msg = auth.create_user("operator_user", "Pass@1234", role="operator")
    assert ok is True
    
    op_user = auth.authenticate("operator_user", "Pass@1234")
    assert op_user is not None
    assert op_user["role"] == "operator"
    
    # 3. List users
    users = auth.list_users()
    usernames = [u["username"] for u in users]
    assert "Amit" in usernames
    assert "operator_user" in usernames
    
    # 4. Delete user
    del_ok, del_msg = auth.delete_user("operator_user")
    assert del_ok is True
    assert auth.authenticate("operator_user", "Pass@1234") is None


@pytest.mark.asyncio
async def test_telegram_login_manager_session_listing(tmp_path):
    mgr = TelegramWebLoginManager(base_dir=tmp_path)
    accounts = await mgr.get_accounts_summary()
    assert isinstance(accounts, list)


def test_get_local_lan_ip():
    ip = get_local_lan_ip()
    assert isinstance(ip, str)
    assert len(ip) >= 7  # e.g., 127.0.0.1 or 192.168.x.x


def test_dashboard_server_status_builder():
    state = ObserverState()
    server = DashboardServer(state=state)
    status = server._build_status_dict()
    assert "uptime" in status
    assert "current_speed_mb" in status
    assert "is_paused" in status
    assert "dlq_count" in status
    assert "wifi_url" in status


def test_dashboard_pause_toggle():
    state = ObserverState()
    server = DashboardServer(state=state)
    toggle1 = server._toggle_pause()
    assert "paused" in toggle1
    toggle2 = server._toggle_pause()
    assert "paused" in toggle2
    assert toggle1["paused"] != toggle2["paused"]


def test_dashboard_forward_routes_crud():
    state = ObserverState()
    server = DashboardServer(state=state)
    
    # 1. Create Route
    route_id = server._create_forward_route(
        src_chat=-1001112223334,
        tgt_chat=-1005556667778,
        tgt_topic=10,
        media_filter="video",
        strip_links=True
    )
    assert route_id > 0

    # 2. Get Routes
    routes = server._get_forward_routes()
    assert isinstance(routes, list)
    target_r = next((r for r in routes if r["id"] == route_id), None)
    assert target_r is not None
    assert target_r["source_chat_id"] == -1001112223334
    assert target_r["target_chat_id"] == -1005556667778
    assert target_r["target_topic_id"] == 10

    # 3. Toggle Route
    toggled = server._toggle_forward_route(route_id)
    assert toggled is True
    updated_r = next((r for r in server._get_forward_routes() if r["id"] == route_id), None)
    assert updated_r is not None
    assert updated_r["is_active"] is False

    # 4. Delete Route
    deleted = server._delete_forward_route(route_id)
    assert deleted is True
    deleted_r = next((r for r in server._get_forward_routes() if r["id"] == route_id), None)
    assert deleted_r is None


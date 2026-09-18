#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
🧪 TESTS: MULTI-USER AUTH & TELEGRAM MULTI-SESSION ENGINE
================================================================================
Validates both components:
1. DashboardAuthManager (Password Hashing, Tokens, RBAC, User CRUD)
2. MultiSessionManager (Session Discovery, Account Switching, Pool Round-Robin, Cooldowns)
================================================================================
"""

import os
import sys
import time
import tempfile
import asyncio
from pathlib import Path
import pytest

# Add project root to sys.path
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

from web_dashboard import DashboardAuthManager
from tg_kind_mode_v14 import MultiSessionManager


def test_auth_manager_initialization():
    """Verify that default root admin is created with salt+hash."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test_users.json"
        auth = DashboardAuthManager(db_file=db_file)
        
        # Check that file exists
        assert db_file.exists(), "Auth DB file should be created on init"
        
        # Check that default admin can log in (case-insensitive)
        login_res = auth.authenticate("Amit", "Amit@123")
        assert login_res is not None, "Root admin Amit should authenticate successfully"
        assert login_res["username"] == "Amit"
        assert login_res["role"] == "admin"
        assert "token" in login_res

        # Check lowercase works too
        login_res_lower = auth.authenticate("amit", "Amit@123")
        assert login_res_lower is not None, "Case-insensitive username should authenticate"
        
        # Verify invalid password fails
        bad_res = auth.authenticate("Amit", "wrongpassword")
        assert bad_res is None, "Wrong password must return None"
        print("✔ test_auth_manager_initialization passed!")


def test_auth_tokens_and_rbac():
    """Verify bearer token verification, roles, and user CRUD."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_file = Path(tmpdir) / "test_users.json"
        auth = DashboardAuthManager(db_file=db_file)
        
        # 1. Login and verify token
        res = auth.authenticate("Amit", "Amit@123")
        token = res["token"]
        
        sess = auth.verify_token(token)
        assert sess is not None, "Valid token should be verified"
        assert sess["username"] == "Amit"
        assert sess["role"] == "admin"
        
        # 2. Create operator user
        ok, msg = auth.create_user("operator1", "pass1234", role="operator")
        assert ok is True, f"Failed to create operator: {msg}"
        
        op_login = auth.authenticate("operator1", "pass1234")
        assert op_login is not None, "New operator should log in"
        assert op_login["role"] == "operator"
        
        # 3. Create duplicate user should fail
        ok_dup, _ = auth.create_user("operator1", "anotherpass")
        assert ok_dup is False, "Duplicate user creation must fail"
        
        # 4. List users
        users = auth.list_users()
        usernames = [u["username"] for u in users]
        assert "Amit" in usernames and "operator1" in usernames
        
        # 5. Delete operator
        ok_del, _ = auth.delete_user("operator1")
        assert ok_del is True, "Operator should be deleted"
        
        # Token for deleted user must be invalidated
        assert auth.verify_token(op_login["token"]) is None, "Deleted user's token should be invalid"
        
        # Deleting root admin must fail
        ok_del_admin, _ = auth.delete_user("Amit")
        assert ok_del_admin is False, "Cannot delete root admin Amit"
        
        # 6. Test purge_expired_tokens
        auth.tokens["expired_dummy"] = {"username": "Amit", "expires_at": time.time() - 100}
        auth.purge_expired_tokens()
        assert "expired_dummy" not in auth.tokens, "Expired tokens should be purged"

        # 7. Logout
        assert auth.logout(token) is True
        assert auth.verify_token(token) is None, "Token must be invalidated after logout"
        print("✔ test_auth_tokens_and_rbac passed!")


def test_multi_session_manager():
    """Verify Telegram multi-session management, account switching, and pool routing."""
    mgr = MultiSessionManager(api_id=12345, api_hash="abcdef0123456789abcdef0123456789")
    
    # 1. Basic client retrieval
    client = mgr.get_client()
    assert client is not None, "get_client() should return a client"
    
    # 2. Dynamic session addition
    mgr.add_session("session_account2")
    assert "session_account2" in mgr.session_names
    
    # 3. Account switching
    ok_switch = mgr.set_active_session("session_account2")
    assert ok_switch is True, "Setting active session by name should succeed"
    assert mgr.active_index == mgr.session_names.index("session_account2")
    
    # Switch by invalid name
    assert mgr.set_active_session("non_existent_session") is False
    
    # Switch back by index
    assert mgr.set_active_session(0) is True
    assert mgr.active_index == 0
    
    # 4. FloodWait cooldown & Pool failover
    mgr.pool_mode = True
    mgr.add_session("session_account3")
    
    # Mark primary in FloodWait cooldown for 10 seconds
    mgr.mark_flood_wait("session_forwarder", 10)
    assert mgr.is_session_cooling_down("session_forwarder") is True
    assert mgr.is_session_cooling_down("session_account2") is False
    
    # Pool mode should auto-skip cooling down session
    pool_client = mgr.get_client()
    assert pool_client is not None
    
    print("✔ test_multi_session_manager passed!")


@pytest.mark.asyncio
async def test_telegram_web_login_manager():
    """Verify TelegramWebLoginManager profile discovery, caching, and active session switching."""
    from web_dashboard import TelegramWebLoginManager
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_base = Path(tmpdir)
        # Create mock session files
        (tmp_base / "session_forwarder.session").write_bytes(b"mock_session_1")
        (tmp_base / "account_5678.session").write_bytes(b"mock_session_2")
        
        tg_mgr = TelegramWebLoginManager(base_dir=tmp_base)
        
        # Test stale login cleanup
        tg_mgr.pending_logins["stale_mock"] = {"created_at": time.time() - 400}
        await tg_mgr.cleanup_stale_logins(max_age_seconds=300)
        assert "stale_mock" not in tg_mgr.pending_logins, "Stale login sessions should be cleaned up"
        
        # Test active session switching
        assert tg_mgr.set_active_session("account_5678") is True
        assert tg_mgr.active_session_name == "account_5678"
        assert tg_mgr.set_active_session("non_existent") is False
        
        # Test accounts summary
        accounts = await tg_mgr.get_accounts_summary()
        assert len(accounts) == 2
        assert accounts[0]["filename"] == "session_forwarder.session"
        assert accounts[0]["is_primary"] is True
        assert accounts[1]["filename"] == "account_5678.session"
        assert accounts[1]["is_active"] is True
        
        # Verify user data structure
        for acc in accounts:
            assert "user" in acc
            assert "first_name" in acc["user"]
            
        print("✔ test_telegram_web_login_manager passed!")


async def run_multi_login_suite():
    test_auth_manager_initialization()
    test_auth_tokens_and_rbac()
    test_multi_session_manager()
    await test_telegram_web_login_manager()


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 RUNNING MULTI-LOGIN & MULTI-SESSION COMPREHENSIVE AUDIT")
    print("="*70)
    asyncio.run(run_multi_login_suite())
    print("="*70)
    print("🎉 ALL MULTI-LOGIN UNIT TESTS PASSED (100% SUCCESS)")
    print("="*70 + "\n")

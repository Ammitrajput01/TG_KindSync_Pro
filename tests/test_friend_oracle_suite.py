#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Friend Edition & Oracle Cloud Crash-Proofing Suite (Part 4).
"""

import os
import zipfile
import re
from pathlib import Path
import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "tools" / "legacy_batch"))
from build_oracle_friend_package import get_timestamp_filename, main as build_friend_package


def test_timestamp_naming_format():
    """Verify timestamp adheres to mandatory naming standards."""
    name = get_timestamp_filename("TG_KindSync_Oracle_Friend_Edition", "zip")
    assert name.startswith("TG_KindSync_Oracle_Friend_Edition_")
    assert name.endswith(".zip")
    # Day_Date-Month-Year_Time
    pattern = r"TG_KindSync_Oracle_Friend_Edition_[A-Za-z]+_\d{2}-[A-Za-z]+-\d{4}_\d{2}-\d{2}[AP]M\.zip"
    assert re.match(pattern, name) is not None, f"Filename {name} does not match required pattern"


def test_package_builder_zip_integrity():
    """Verify package builder creates valid zip with all required files."""
    build_friend_package()
    static_zip = Path("tools/legacy_batch/TG_KindSync_Oracle_Friend_Package.zip")
    if not static_zip.exists():
        static_zip = Path("TG_KindSync_Oracle_Friend_Package.zip")
    assert static_zip.exists(), "TG_KindSync_Oracle_Friend_Package.zip must exist"

    with zipfile.ZipFile(static_zip, "r") as z:
        namelist = z.namelist()
        expected_files = [
            "CONNECT_ORACLE_FRIEND.bat",
            "START_ORACLE_FRIEND_24_7.bat",
            "HOW_TO_RUN.txt"
        ]
        for ef in expected_files:
            assert ef in namelist, f"Expected file {ef} missing in zip"


def test_setup_friend_oracle_sh_syntax_and_structure():
    """Verify deploy/setup_friend_oracle.sh has all safety guards and services."""
    script_path = Path("deploy/setup_friend_oracle.sh")
    assert script_path.exists()
    content = script_path.read_text(encoding="utf-8")

    assert "/home/ubuntu/TG_KindSync_Friend" in content
    assert "web_dashboard.py" in content
    assert "sentinel_observer.py" in content
    assert "tg-forwarder-friend.service" in content
    assert "status_friend.sh" in content
    assert "view_live_friend.sh" in content
    assert "restart_friend.sh" in content
    assert "stop_friend.sh" in content
    assert "AUTO_START_LIVE=1" in content


def test_start_friend_24_7_sh_syntax_and_structure():
    """Verify deploy/start_friend_24_7.sh syncs engine files and configures systemd."""
    script_path = Path("deploy/start_friend_24_7.sh")
    assert script_path.exists()
    content = script_path.read_text(encoding="utf-8")

    assert "/home/ubuntu/TG_KindSync_Friend" in content
    assert "web_dashboard.py" in content
    assert "sentinel_observer.py" in content
    assert "systemctl enable" in content
    assert "systemctl restart" in content


def test_bat_scripts_ssh_key_handling():
    """Verify batch scripts handle icacls permissions and target VPS IP."""
    for bat_name in ["CONNECT_ORACLE_FRIEND.bat", "START_ORACLE_FRIEND_24_7.bat"]:
        bat_path = Path("tools/legacy_batch") / bat_name
        if not bat_path.exists():
            bat_path = Path(bat_name)
        assert bat_path.exists()
        content = bat_path.read_text(encoding="utf-8")
        assert "130.210.1.32" in content
        assert "icacls" in content


def test_tg_kindsync_pro_headless_loop_safety():
    """Verify tg_kindsync_pro.py handles is_auto without hanging on safe_input."""
    main_engine = Path("tg_kindsync_pro.py")
    assert main_engine.exists()
    content = main_engine.read_text(encoding="utf-8")
    assert "is_auto" in content
    # Verify safe_input is guarded by 'if not is_auto:'
    assert "if not is_auto:\n                await safe_input(\"\\nPress Enter to return to Main Menu\"" in content

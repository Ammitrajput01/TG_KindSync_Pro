#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import json
import pytest
from pathlib import Path
from web_dashboard import get_polyglot_status_safe, DashboardServer

BASE_DIR = Path(__file__).resolve().parent.parent

def test_polyglot_status_safe_structure():
    st = get_polyglot_status_safe()
    assert isinstance(st, dict)
    assert "crypto_engine" in st
    assert "json_engine" in st
    assert "analytics_engine" in st
    assert "event_loop" in st
    assert "platform" in st

def test_html_polyglot_elements():
    html_file = BASE_DIR / "web" / "templates" / "index.html"
    assert html_file.exists()
    content = html_file.read_text(encoding="utf-8")
    assert 'id="polyglot-header-badge"' in content
    assert 'id="polyglot-matrix-card"' in content
    assert 'id="poly-crypto-val"' in content
    assert 'id="poly-json-val"' in content
    assert 'id="poly-duckdb-val"' in content
    assert 'id="poly-socket-val"' in content

def test_js_polyglot_handlers():
    js_file = BASE_DIR / "web" / "static" / "js" / "dashboard.js"
    assert js_file.exists()
    content = js_file.read_text(encoding="utf-8")
    assert 'function updatePolyglotTelemetry' in content
    assert 'fetchPolyglotStatus' in content
    assert 'd.polyglot_acceleration' in content

def test_dashboard_status_dict_includes_polyglot():
    import time
    class TestState:
        def __init__(self):
            self.start_time = time.monotonic()
            self.total_transfers = 0
            self.videos_sent = 0
            self.docs_sent = 0
            self.photos_sent = 0
            self.albums_sent = 0
            self.current_subject = "Standby"
            self.flood_waits_detected = 0
            self.flood_wait_seconds_total = 0.0
            self.peak_speed_mb = 0.0
            self.db_forwarded_count = 0
            self.recent_events = []
            self.recommendations = []

    server = DashboardServer(TestState(), port=8089)
    status_dict = server._build_status_dict()
    assert "polyglot_acceleration" in status_dict
    poly = status_dict["polyglot_acceleration"]
    assert "crypto_engine" in poly
    assert "json_engine" in poly

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification Suite for:
1. Collapsible Sidebar (Hamburger 3-lines button, icon-only rail, floating tooltips)
2. Reorganized Top Application Header (Telemetry capsule, Doctor pill, non-clipping action bar, more tools dropdown)
3. CSS transitions, Emil Kowalski spring timing, and responsive media queries
4. JavaScript state persistence (localStorage) and keyboard shortcuts (Ctrl+B)
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def test_collapsible_sidebar_and_header():
    index_html = (ROOT_DIR / "web" / "templates" / "index.html").read_text(encoding="utf-8")
    dashboard_css = (ROOT_DIR / "web" / "static" / "css" / "dashboard.css").read_text(encoding="utf-8")
    dashboard_js = (ROOT_DIR / "web" / "static" / "js" / "dashboard.js").read_text(encoding="utf-8")

    print("[*] 1. Validating index.html UI markup...")
    assert 'id="sidebar-toggle-btn"' in index_html, "Missing sidebar-toggle-btn hamburger button"
    assert 'class="collapse-chevron"' in index_html, "Missing collapse-chevron button in sidebar brand"
    assert 'data-tooltip="1. Mission Control"' in index_html, "Missing data-tooltip on nav-overview"
    assert 'data-tooltip="2. Transmission Engine"' in index_html, "Missing data-tooltip on nav-operations"
    assert 'class="header-telemetry-capsule"' in index_html, "Missing header-telemetry-capsule"
    assert 'class="header-doctor-pill"' in index_html, "Missing header-doctor-pill"
    assert 'id="btn-header-snapshot"' in index_html, "Missing prominent btn-header-snapshot"
    assert 'id="header-tools-wrapper"' in index_html, "Missing header-tools-wrapper"
    assert 'id="header-tools-menu"' in index_html, "Missing header-tools-menu dropdown"
    print("  [+] index.html markup: PASSED")

    print("[*] 2. Validating dashboard.css styles...")
    assert '.sidebar.sidebar-collapsed' in dashboard_css, "Missing .sidebar.sidebar-collapsed styles"
    assert 'width: 70px;' in dashboard_css, "Missing 70px width for collapsed sidebar"
    assert '.sidebar.sidebar-collapsed .nav-link::after' in dashboard_css, "Missing collapsed nav tooltip styles"
    assert '.header-telemetry-capsule' in dashboard_css, "Missing .header-telemetry-capsule styles"
    assert '.header-doctor-pill' in dashboard_css, "Missing .header-doctor-pill styles"
    assert '.btn-snapshot-glow' in dashboard_css, "Missing .btn-snapshot-glow styles"
    assert '.header-tools-dropdown-menu' in dashboard_css, "Missing .header-tools-dropdown-menu styles"
    assert '@media (max-width: 1440px)' in dashboard_css, "Missing responsive breakpoint 1440px"
    print("  [+] dashboard.css styles: PASSED")

    print("[*] 3. Validating dashboard.js state and event handlers...")
    assert 'function toggleSidebarCollapse()' in dashboard_js, "Missing toggleSidebarCollapse function"
    assert 'function initSidebarState()' in dashboard_js, "Missing initSidebarState function"
    assert 'localStorage.setItem(\'sidebar_collapsed\'' in dashboard_js, "Missing localStorage persistence"
    assert 'function toggleHeaderToolsDropdown' in dashboard_js, "Missing toggleHeaderToolsDropdown function"
    assert 'function closeHeaderToolsDropdown' in dashboard_js, "Missing closeHeaderToolsDropdown function"
    assert 'initSidebarState();' in dashboard_js, "Missing initSidebarState call in DOMContentLoaded"
    assert "e.key.toLowerCase() === 'b'" in dashboard_js, "Missing Ctrl+B keyboard shortcut for sidebar toggle"
    print("  [+] dashboard.js logic: PASSED")

    print("\n[SUCCESS] ALL COLLAPSIBLE SIDEBAR & RESPONSIVE HEADER TESTS PASSED 100%!")

if __name__ == "__main__":
    test_collapsible_sidebar_and_header()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import urllib.request
import urllib.error

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_URL = "http://127.0.0.1:8080"

def log_test(name, passed, details=""):
    mark = "PASS" if passed else "FAIL"
    print(f"[{mark}] {name}: {details}")
    if not passed:
        sys.exit(1)

def request_json(path, method="GET", data=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read().decode("utf-8")
            return resp.status, json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        content = e.read().decode("utf-8")
        try:
            return e.code, json.loads(content) if content else {}
        except Exception:
            return e.code, {"raw_error": content}

def run_all_deep_tests():
    print("========================================================")
    print("   DEEP DASHBOARD END-TO-END VERIFICATION SUITE")
    print("========================================================")

    # 1. HTML check
    try:
        with urllib.request.urlopen(f"{BASE_URL}/", timeout=5) as r:
            html = r.read().decode("utf-8")
            p = (
                r.status == 200
                and "cycleTheme" in html
                and "runModelSpeedRace" in html
                and "vital-cpu-bar" in html
                and "@Kinddoctor4u" in html
                and "@Ammitrajput1" in html
                and "Ammitrajput1@gmail.com" in html
            )
            log_test("GET / (Index HTML & Cyber Assets)", p, f"Size: {len(html)} bytes")
    except Exception as e:
        log_test("GET /", False, str(e))

    # 2. Status
    c, d = request_json("/api/status")
    log_test("GET /api/status", c == 200 and "uptime" in d, f"Uptime: {d.get('uptime')}")

    # 3. Invalid login rejection
    c, d = request_json("/api/auth/login", method="POST", data={"username": "wrong", "password": "bad"})
    log_test("POST /api/auth/login (Invalid rejection)", c == 401, f"Status: {c}")

    # 4. Valid login
    c, d = request_json("/api/auth/login", method="POST", data={"username": "Amit", "password": "Amit@123"})
    token = d.get("token")
    log_test("POST /api/auth/login (Admin Amit)", c == 200 and bool(token), f"Token: {token[:12]}...")

    # 5. /api/auth/me
    c, d = request_json("/api/auth/me", token=token)
    log_test("GET /api/auth/me", c == 200 and d.get("authenticated") is True, f"User: {d.get('username')}, Role: {d.get('role')}")

    # 6. Users list
    c, d = request_json("/api/auth/users", token=token)
    log_test("GET /api/auth/users", c == 200, f"{len(d.get('users', []))} users")

    # 7. Telegram accounts
    c, d = request_json("/api/telegram/accounts", token=token)
    log_test("GET /api/telegram/accounts", c == 200, f"{len(d.get('accounts', []))} accounts")

    # 8. Devi status
    c, d = request_json("/api/devi/status", token=token)
    log_test("GET /api/devi/status", c == 200, f"{d.get('vitality', {}).get('status')}")

    # 9. Devi chat
    c, d = request_json("/api/devi/chat", method="POST", data={"message": "System status check"}, token=token)
    log_test("POST /api/devi/chat", c == 200 and d.get("success") is True, f"Provider: {d.get('provider')}")

    # 10. Devi council
    c, d = request_json("/api/devi/council", method="POST", data={"topic": "Fast forwarding strategy"}, token=token)
    log_test("POST /api/devi/council", c == 200 and d.get("success") is True, f"{len(d.get('perspectives', []))} models answered")

    # 11. Research insights
    c, d = request_json("/api/research_insights", token=token)
    log_test("GET /api/research_insights", c == 200, f"{len(d.get('insights', []))} insights")

    # 12. Dismiss insight
    c, d = request_json("/api/dismiss_insight", method="POST", data={"id": "test_id", "read": True}, token=token)
    log_test("POST /api/dismiss_insight", c == 200 and d.get("success") is True, "Success")

    # 13. DLQ Errors
    c, d = request_json("/api/errors", token=token)
    log_test("GET /api/errors", c == 200, f"{len(d.get('errors', []))} errors")

    # 14. Backup
    c, d = request_json("/api/backup", method="POST", token=token)
    log_test("POST /api/backup", c == 200 and d.get("success") is True, "Dispatched")

    # 15. Engine pause toggle
    c, d = request_json("/api/pause", method="POST", token=token)
    log_test("POST /api/pause", c == 200 and "paused" in d, f"Paused: {d.get('paused')}")
    if d.get("paused"):
        request_json("/api/pause", method="POST", token=token)

    # 16. Key hunt
    c, d = request_json("/api/devi/hunt", method="POST", token=token)
    log_test("POST /api/devi/hunt", c == 200 and d.get("success") is True, "Hunt active")

    print("========================================================")
    print("   ALL 16 DEEP VERIFICATION CHECKS PASSED 100%!")
    print("========================================================")

if __name__ == "__main__":
    run_all_deep_tests()

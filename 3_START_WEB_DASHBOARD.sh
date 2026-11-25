#!/usr/bin/env bash
# ==============================================================================
# 📊 3. START OBSIDIAN WEB COMMAND CENTER (PORT 8080)
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || true
fi

PY_BIN="$(command -v python3 || command -v python || true)"
echo "[*] Launching DEVI Web Cockpit on http://127.0.0.1:8080 ..."
"$PY_BIN" web_dashboard.py "$@"

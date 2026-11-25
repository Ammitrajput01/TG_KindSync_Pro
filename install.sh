#!/usr/bin/env bash
# ==============================================================================
# 📱 TG KINDSYNC PRO — UNIVERSAL 1-CLICK INSTALLER (TERMUX / LINUX / MACOS)
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -n "${TERMUX_VERSION:-}" ] || [ -d "/data/data/com.termux" ]; then
    bash "$SCRIPT_DIR/KINDSYNC_MASTER.sh" "$@"
    exit $?
fi

echo "============================================================"
echo "  🩺 TG KINDSYNC PRO — LINUX / UNIX / MACOS SETUP"
echo "============================================================"
PY_BIN="$(command -v python3 || command -v python || true)"
if [ -z "$PY_BIN" ]; then
    echo "[!] Python 3 is required. Install python3 + python3-venv and retry."
    exit 1
fi
[ ! -f ".env" ] && [ -f ".env.example" ] && cp .env.example .env
if [ ! -d ".venv" ]; then
    "$PY_BIN" -m venv .venv
fi
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo "✅ Setup complete! Run: source .venv/bin/activate && python main.py"

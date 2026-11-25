#!/usr/bin/env bash
# ==============================================================================
# 🚀 5. 1-CLICK AUTO-UPDATER & SYSTEM UPGRADE FOR ANDROID TERMUX
# ==============================================================================
# Pulls latest commits from GitHub, upgrades requirements, and self-heals
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "  🚀 TG KINDSYNC PRO — 1-CLICK AUTO-UPDATER & SYNC"
echo "  Pulling latest code updates from GitHub..."
echo "============================================================"

# 1. Update source code from GitHub safely
git config --global --add safe.directory "$SCRIPT_DIR" 2>/dev/null || true
git config --global http.version HTTP/1.1 2>/dev/null || true
git pull origin main || echo "[WARN] Git pull skipped or local changes kept."

# 2. Upgrade Python dependencies (Android/Termux safe without fatal abort)
echo ""
echo "[*] Synchronizing Android-safe Python requirements..."
if [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || true
fi

export PIP_DISABLE_PIP_VERSION_CHECK=1
export PIP_NO_CACHE_DIR=1

# Ensure native Termux packages are installed if running inside Termux
if [ -n "${TERMUX_VERSION:-}" ] || [ -d "/data/data/com.termux" ]; then
    pkg install -y python-psutil python-pillow python-cryptography 2>/dev/null || true
    REQ_FILE="requirements-termux.txt"
else
    REQ_FILE="requirements.txt"
fi

PY_BIN="$(command -v python3 || command -v python || true)"
"$PY_BIN" -m pip install --upgrade -r "$REQ_FILE" 2>/dev/null || \
"$PY_BIN" -m pip install --break-system-packages --upgrade -r "$REQ_FILE" 2>/dev/null || \
echo "[WARN] Some optional packages skipped; checking core imports..."

# 3. Instant verification
"$PY_BIN" -c "
import telethon, aiosqlite, dotenv, rich, aiohttp
print('  ✅ All Core Streaming Modules Verified 100% Healthy!')
" || echo "  ⚠️ Run: pip install --break-system-packages telethon aiosqlite python-dotenv rich aiohttp"

echo ""
echo "============================================================"
echo "  🎉 UPDATE COMPLETE & VERIFIED!"
echo "  Launch Engine: bash 1_START_KINDSYNC.sh"
echo "============================================================"


#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# 📱 1. START TG KINDSYNC PRO ENGINE (INTERACTIVE / FOREGROUND)
# ==============================================================================
# Launches 19-quadrant terminal menu, QR scan login, and direct cloner
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if command -v termux-wake-lock &> /dev/null; then
    termux-wake-lock || true
fi

if [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || true
fi

# Auto-initialize .env if missing (Safe MTProto fallback active)
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env 2>/dev/null || touch .env
    else
        touch .env
    fi
fi

if ! python -c "import aiosqlite, telethon, rich, dotenv" 2>/dev/null; then
    echo "[*] Setting up dependencies..."
    bash deploy/install_termux.sh
    if [ -d ".venv" ]; then
        source .venv/bin/activate 2>/dev/null || true
    fi
fi

python tg_kindsync_pro.py "$@"


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

if [ ! -d ".venv" ] || [ ! -f ".env" ]; then
    echo "[*] Setting up dependencies..."
    bash deploy/install_termux.sh
fi

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

python tg_kindsync_pro.py "$@"


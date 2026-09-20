#!/usr/bin/env bash
# ==============================================================================
# 🚀 TG KINDSYNC PRO — ORACLE CLOUD 1-COMMAND AUTO-UPDATER
# ==============================================================================
set -e

cd "$(dirname "$0")/.."
echo "============================================================"
echo "  🚀 TG KINDSYNC PRO — LIVE VPS AUTO-UPDATER"
echo "  Pulling latest code updates from Private GitHub..."
echo "============================================================"

# Auto-initialize git if missing
if [ ! -d ".git" ]; then
    echo "[*] Initializing Git repository link..."
    git init
    git branch -M main
    git remote add origin https://github.com/Ammitrajput01/TG_KindSync_Pro.git 2>/dev/null || git remote set-url origin https://github.com/Ammitrajput01/TG_KindSync_Pro.git
    git fetch origin main
    git checkout -f -B main origin/main
else
    # 1. Pull latest commits from GitHub
    git pull origin main
fi

# 2. Update dependencies if any changed
if [ -d ".venv" ]; then
    source .venv/bin/activate
    pip install -r requirements.txt --quiet
fi

# 3. Gracefully restart all 3 background services
echo "[*] Restarting background systemd services..."
sudo systemctl daemon-reload
sudo systemctl restart tg-forwarder 2>/dev/null || true
sudo systemctl restart tg-kinddoc-bot 2>/dev/null || true
sudo systemctl restart tg-dashboard 2>/dev/null || true

echo ""
echo "============================================================"
echo "  🎉 UPDATE COMPLETE & LIVE!"
echo "  - Telegram Forwarder Engine: RESTARTED"
echo "  - Kind Doctor Bot Daemon:    RESTARTED"
echo "  - DEVI Web Dashboard:        RESTARTED"
echo "============================================================"

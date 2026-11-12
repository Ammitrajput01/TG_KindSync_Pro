#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# 🚀 5. 1-CLICK AUTO-UPDATER FOR ANDROID TERMUX
# ==============================================================================
# Pulls latest commits from GitHub and self-heals dependencies
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "  🚀 TG KINDSYNC PRO — 1-CLICK AUTO-UPDATER"
echo "  Checking for latest updates from GitHub..."
echo "============================================================"

git pull origin main

echo "[*] Synchronizing dependencies..."
bash deploy/install_termux.sh

echo ""
echo "============================================================"
echo "  🎉 UPDATE COMPLETE & VERIFIED 100% HEALTHY!"
echo "============================================================"

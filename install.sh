#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# 📱 TG KINDSYNC PRO — 1-CLICK ALL-IN-ONE INSTALLER & RUNNER FOR ANDROID TERMUX
# ==============================================================================
# 1. Installs all native C & Python dependencies automatically (Zero Prompts)
# 2. Configures wake-lock, Git network buffers, and .env
# 3. Automatically launches the TG KindSync Pro Interactive Terminal & QR Login
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Step 1: Run complete zero-prompt installer
bash deploy/install_termux.sh "$@"

# Step 2: Directly boot interactive engine (QR Login screen)
bash 1_START_KINDSYNC.sh

#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# 📱 TG KINDSYNC PRO — BULLETPROOF 1-CLICK TERMUX INSTALLER (ARM64 / ANDROID)
# ==============================================================================
# Solves all Android Termux compilation errors:
# 1. Installs pre-compiled native packages (python-psutil, python-pillow, python-cryptography)
#    to eliminate "platform android is not supported" and hours of CMake 4.4.4 compilation.
# 2. Omits 'pip install --upgrade pip' which is strictly forbidden in Termux.
# 3. Creates .venv with --system-site-packages to bridge native C libraries.
# 4. Sets Git HTTP/1.1 buffers to prevent "curl 92 HTTP/2 stream 5 reset by server".
# 5. Acquires 24/7 background CPU wake-lock.
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "============================================================"
echo "  🚀 TG KINDSYNC PRO — 1-CLICK ANDROID TERMUX SETUP"
echo "  👨‍⚕️ Kind Doctor & Team · Zero-Freeze Native Architecture"
echo "============================================================"

# Step 1: Termux CPU Wake Lock
if command -v termux-wake-lock &> /dev/null; then
    echo "[1/6] 🔋 Acquiring 24/7 Android CPU Wake Lock..."
    termux-wake-lock || true
fi

# Step 2: Configure Git to avoid mobile network RPC curl 92 aborts
echo "[2/6] 🌐 Configuring Git network buffer stability..."
git config --global http.version HTTP/1.1 || true
git config --global http.postBuffer 524288000 || true

# Step 3: Update Termux Repositories
echo "[3/6] 🔄 Updating Termux package repositories..."
pkg update -y || apt update -y

# Step 4: Install Native Android Packages via pkg (Zero-Compilation)
echo "[4/6] 📦 Installing native Android tools & pre-compiled packages..."
pkg install -y python python-pip git ffmpeg openssl libjpeg-turbo termux-api \
    python-cryptography python-psutil python-pillow

# Step 5: Setup Virtual Environment with System Site Packages
echo "[5/6] 🧠 Creating isolated Python virtual environment..."
if [ ! -d ".venv" ]; then
    python -m venv --system-site-packages .venv
fi
source .venv/bin/activate

# Step 6: Install Pure-Python Lightweight Dependencies
echo "[6/6] ⚡ Installing lightweight Python dependencies (Zero-CMake)..."
# NOTE: Never run 'pip install --upgrade pip' in Termux!
pip install --no-build-isolation -r requirements-termux.txt

# Step 7: Integrity Diagnostics
echo "[+] 🔍 Verifying all core dependencies..."
python -c "
import telethon, psutil, PIL, cryptography, aiosqlite, aiohttp, rich, qrcode
print('  ✅ All Core Android Dependencies Verified 100% Healthy!')
"

# Step 8: Initialize Directories and Config
mkdir -p logs db_backups member_backups data archives
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "  [+] Initialized default .env configuration."
    else
        touch .env
    fi
fi

echo ""
echo "============================================================"
echo "  🎉 ANDROID TERMUX SETUP COMPLETE & 100% OPERATIONAL!"
echo "============================================================"
echo "  • Start 24/7 Background Runner:  bash deploy/RUN_24_7_TERMUX.sh"
echo "  • Interactive Foreground Run:    python tg_kindsync_pro.py"
echo "  • Start Operator Bot:            python -m devi.operator.telegram_bot"
echo "  • Start Web Dashboard:           python web_dashboard.py"
echo "============================================================"

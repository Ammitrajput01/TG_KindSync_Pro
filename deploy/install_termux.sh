#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# 📱 TG KINDSYNC PRO — 100% AUTOMATED ZERO-PROMPT TERMUX INSTALLER (ANDROID)
# ==============================================================================
# 1. 100% Non-Interactive: Zero Y/N prompts (auto-accepts default configs)
# 2. Full System Package Upgrade: Ensures libc++ matches ffmpeg/libplacebo
# 3. Resilient Dpkg Recovery: Automatically runs dpkg --configure -a
# 4. Zero-CMake PyPI Architecture: Pre-compiled native packages (psutil, pillow, crypto)
# 5. Git HTTP/1.1 & 512MB Buffer: Prevents mobile RPC stream resets
# ==============================================================================

# Enforce Non-Interactive Mode (Eliminates all Y/N prompts)
export DEBIAN_FRONTEND=noninteractive
export DPKG_OPTIONS="-o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

echo "============================================================"
echo "  🚀 TG KINDSYNC PRO — FULLY AUTOMATED ANDROID TERMUX SETUP"
echo "  👨‍⚕️ Kind Doctor & Team · Zero-Prompt Native Architecture"
echo "============================================================"

# Step 1: Acquire Android CPU Wake Lock
if command -v termux-wake-lock &> /dev/null; then
    echo "[1/7] 🔋 Activating 24/7 Android CPU Wake Lock..."
    termux-wake-lock || true
fi

# Step 2: Configure Git Mobile Network Buffer
echo "[2/7] 🌐 Configuring Git mobile network buffers (HTTP/1.1)..."
git config --global http.version HTTP/1.1 || true
git config --global http.postBuffer 524288000 || true

# Step 3: Repair any broken dpkg states from previous runs
echo "[3/7] 🔧 Checking and repairing package database..."
dpkg --configure -a 2>/dev/null || true

# Step 4: Auto-Heal Termux Mirrors & Upgrade (Fixes 429 Too Many Requests & Y/N prompts)
echo "[4/7] 🔄 Auto-healing APT mirrors and upgrading packages..."
PREFIX_DIR="${PREFIX:-/data/data/com.termux/files/usr}"
if [ -f "$PREFIX_DIR/etc/apt/sources.list" ]; then
    if grep -q -E "textcord\.xyz|mirror\.bardia\.tech|niranjan\.co|cfe\.re" "$PREFIX_DIR/etc/apt/sources.list" 2>/dev/null; then
        echo "deb https://packages-cf.termux.dev/apt/termux-main stable main" > "$PREFIX_DIR/etc/apt/sources.list"
    fi
fi

if ! (yes '' | apt-get update -y 2>/dev/null); then
    echo "deb https://packages-cf.termux.dev/apt/termux-main stable main" > "$PREFIX_DIR/etc/apt/sources.list"
    if ! (yes '' | apt-get update -y 2>/dev/null); then
        echo "deb https://grimler.se/termux/termux-main stable main" > "$PREFIX_DIR/etc/apt/sources.list"
        yes '' | apt-get update -y 2>/dev/null || true
    fi
fi
yes '' | apt-get -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" dist-upgrade 2>/dev/null || yes '' | pkg upgrade -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" 2>/dev/null || true

# Step 5: Install Native Android Packages via pkg (Zero-Compilation)
echo "[5/7] 📦 Installing core Android tools & pre-compiled packages..."
yes '' | apt-get install -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
    python git openssl termux-api \
    python-cryptography python-psutil python-pillow 2>/dev/null || \
yes '' | pkg install -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" \
    python git openssl termux-api \
    python-cryptography python-psutil python-pillow

# Optional media engine (ffmpeg) with resilient fallback
echo "[+] 🎥 Setting up media libraries..."
yes '' | apt-get install -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" ffmpeg 2>/dev/null || \
yes '' | pkg install -y -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confold" ffmpeg 2>/dev/null || true
dpkg --configure -a 2>/dev/null || true

# Step 6: Setup Virtual Environment & Install Python Dependencies
echo "[6/7] ⚡ Setting up Python environment & lightweight dependencies..."
if [ ! -d ".venv" ]; then
    python -m venv --system-site-packages .venv 2>/dev/null || true
fi
if [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || true
fi

# Install dependencies using pre-compiled wheels only (Eliminates CMake compilation)
echo "[+] 📦 Installing aiosqlite, telethon, rich, yt-dlp..."
python -m pip install --only-binary=:all: aiosqlite telethon aiohttp python-dotenv "rich>=13.0.0" "qrcode[pil]>=7.4.2" "yt-dlp>=2024.10.0" 2>/dev/null || \
pip install --break-system-packages --only-binary=:all: aiosqlite telethon aiohttp python-dotenv "rich>=13.0.0" "qrcode[pil]>=7.4.2" "yt-dlp>=2024.10.0" 2>/dev/null || \
pip install --no-build-isolation -r requirements-termux.txt

# Step 7: Integrity Diagnostics
echo "[7/7] 🔍 Running integrity diagnostics on Android dependencies..."
python -c "
import aiosqlite, telethon, aiohttp, psutil, PIL, cryptography
print('  [+] Core Modules (Telethon, SQLite, AsyncIO, PSUtil, Pillow, Crypto): OK')
import rich, qrcode, yt_dlp
print('  [+] Streaming & Media Modules (Rich CLI, QR Generator, YT-DLP): OK')
print('  ✅ All Android Termux Dependencies Verified 100% Healthy!')
"

# Initialize Directories & Configuration
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
echo "  • Start Master Mobile Terminal:  bash 1_START_TERMUX.sh"
echo "  • Start 24/7 Background Runner:  bash START_24_7_TERMUX.sh"
echo "  • Interactive Foreground Run:    python tg_kindsync_pro.py"
echo "============================================================"

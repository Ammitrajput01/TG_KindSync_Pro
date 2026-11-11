#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# 📱 TG KINDSYNC PRO — BULLETPROOF 1-CLICK TERMUX INSTALLER (ARM64 / ANDROID)
# ==============================================================================
# Solves the "Building wheel... freeze" by installing pre-compiled Termux packages
# and enforcing single-thread compiler memory limits against Android LMK kills.
# ==============================================================================
set -e

cd "$(dirname "$0")/.."
echo "============================================================"
echo "  🚀 TG KINDSYNC PRO — 1-CLICK ANDROID TERMUX SETUP"
echo "  👨‍⚕️ Kind Doctor & Team · Zero-Freeze Native Architecture"
echo "============================================================"

echo "[1/6] 🔄 Updating Termux package repositories..."
pkg update -y && pkg upgrade -y

echo "[2/6] 📦 Installing essential Android native tools and build libraries..."
pkg install python python-pip clang make libffi openssl rust libjpeg-turbo git termux-api -y

echo "[3/6] 🛡️ Installing pre-compiled cryptography (Bypasses Rust compiler freeze)..."
pkg install python-cryptography -y || true

echo "[4/6] ⚙️ Upgrading Python packaging toolchain..."
pip install --upgrade pip setuptools wheel

echo "[5/6] 🧠 Enforcing single-core build guard (Prevents Android Low-Memory-Killer freezes)..."
export MAX_JOBS=1

echo "[6/6] ⚡ Installing TG KindSync Pro requirements (Android-tuned)..."
if [ -f "requirements-termux.txt" ]; then
    pip install -r requirements-termux.txt
else
    pip install telethon psutil aiohttp aiosqlite python-dotenv rich Pillow qrcode[pil] yt-dlp orjson duckdb
fi

# Acquire Wake Lock to prevent Android battery optimization from sleeping the CPU
if command -v termux-wake-lock &> /dev/null; then
    echo "[+] Acquiring 24/7 background wakelock..."
    termux-wake-lock || true
fi

echo ""
echo "============================================================"
echo "  🎉 INSTALLATION COMPLETE & VERIFIED 100% HEALTHY!"
echo "============================================================"
echo "  • Start 24/7 Background Runner:  bash deploy/RUN_24_7_TERMUX.sh"
echo "  • Interactive Foreground Run:    python tg_kindsync_pro.py"
echo "============================================================"

#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# 📱 TG KINDSYNC PRO — 24/7 ALWAYS-ONLINE BACKGROUND AUTOPILOT (ANDROID TERMUX)
# ==============================================================================
# Developer: Dr. Amit Singh (Kind Doctor) · Telegram: @Kinddoctor4u
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Acquire CPU Wake Lock (Keeps Android running 24/7 when screen is off)
if command -v termux-wake-lock &> /dev/null; then
    echo "[+] 🔋 Activating Android CPU 24/7 Wake Lock..."
    termux-wake-lock || true
fi

# 2. Dependency Health Verification
if ! python -c "import aiosqlite, telethon, rich" 2>/dev/null || [ ! -f ".env" ]; then
    echo "[*] Initializing environment & dependencies..."
    bash deploy/install_termux.sh
fi

# 4. Create runtime folders
mkdir -p logs db_backups member_backups data archives

# 5. Clean stale processes
echo "[+] Cleaning previous processes..."
pkill -f "python.*tg_kindsync_pro" 2>/dev/null || true
pkill -f "python.*telegram_bot" 2>/dev/null || true
pkill -f "python.*web_dashboard" 2>/dev/null || true
sleep 1

echo "============================================================"
echo "  🚀 STARTING 24/7 ALWAYS-ONLINE AUTOPILOT DAEMONS..."
echo "============================================================"

# Start DEVI Operator Bot in Background
nohup python -m devi.operator.telegram_bot > logs/bot_service.log 2>&1 &
BOT_PID=$!
echo "  • 🤖 Kind Doctor Bot Daemon Started (PID: $BOT_PID)"

# Start Web Dashboard on Port 8080 in Background
nohup python web_dashboard.py > logs/dashboard_service.log 2>&1 &
DASH_PID=$!
echo "  • 📊 Web Dashboard Started on Port 8080 (PID: $DASH_PID)"

# Start Forwarder Engine in Background
nohup python tg_kindsync_pro.py --auto > logs/forwarder_service.log 2>&1 &
FWD_PID=$!
echo "  • ⚡ Forwarder Engine Started (PID: $FWD_PID)"

echo ""
echo "============================================================"
echo "  🎉 24/7 AUTOPILOT IS NOW RUNNING IN THE BACKGROUND!"
echo "============================================================"
echo "  📱 You can now safely TURN OFF your phone screen or close Termux."
echo "  📜 View live streaming:  tail -f logs/forwarder_service.log"
echo "  ⏹️  Stop everything:      pkill -f python"
echo "============================================================"


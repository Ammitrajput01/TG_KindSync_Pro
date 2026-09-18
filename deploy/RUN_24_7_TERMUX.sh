#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# 📱 TG KINDSYNC PRO - 24/7 ANDROID TERMUX BACKGROUND RUNNER
# ==============================================================================

cd "$(dirname "$0")/.."
echo "============================================================"
echo "  📱 TG KINDSYNC PRO - 24/7 ANDROID TERMUX RUNNER"
echo "  - High-Speed Medical Forwarder & Operator Daemon"
echo "============================================================"

# 1. Acquire Android Wake Lock (Prevents Android from killing CPU when screen is off)
if command -v termux-wake-lock &> /dev/null; then
    echo "[+] Activating Android Termux Wake Lock (24/7 Background Running)..."
    termux-wake-lock
fi

# 2. Check Python Environment
mkdir -p logs db_backups member_backups
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# 3. Kill existing running processes if any
pkill -f "python tg_kindsync_pro.py" 2>/dev/null || true
pkill -f "python -m devi.operator.telegram_bot" 2>/dev/null || true
pkill -f "python web_dashboard.py" 2>/dev/null || true

echo "[+] Starting Forwarder, Bot Daemon, and Dashboard in Background..."

# 4. Start DEVI Bot Daemon in Background
nohup python -m devi.operator.telegram_bot > logs/bot_service.log 2>&1 &
BOT_PID=$!
echo " • 🤖 Kind Doctor Bot Daemon Started (PID: $BOT_PID)"

# 5. Start Web Dashboard in Background
nohup python web_dashboard.py > logs/dashboard_service.log 2>&1 &
DASH_PID=$!
echo " • 📊 Web Dashboard Started on Port 8080 (PID: $DASH_PID)"

# 6. Start Main Forwarder Engine in Background
nohup python tg_kindsync_pro.py > logs/forwarder_service.log 2>&1 &
FWD_PID=$!
echo " • ⚡ Forwarder Engine Started (PID: $FWD_PID)"

echo ""
echo "============================================================"
echo "  🎉 24/7 AUTOPILOT RUNNING IN BACKGROUND!"
echo "============================================================"
echo "  • You can now turn off your phone screen or close Termux."
echo "  • Live Logs:  tail -f logs/forwarder_service.log"
echo "  • Stop All:   pkill -f python"
echo "============================================================"

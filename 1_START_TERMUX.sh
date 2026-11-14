#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
# 📱 TG KINDSYNC PRO — 1-CLICK MASTER TERMINAL FOR ANDROID TERMUX
# ==============================================================================
# Developer & Systems Architect: Dr. Amit Singh (Kind Doctor)
# Branding: Kind Doctor & Team · Telegram: @Kinddoctor4u
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 1. Acquire Android Wake Lock (Keeps CPU awake when screen is turned off)
if command -v termux-wake-lock &> /dev/null; then
    termux-wake-lock || true
fi

# 2. Activate virtual environment if present
if [ -d ".venv" ]; then
    source .venv/bin/activate 2>/dev/null || true
fi

# 3. Auto-initialize .env if missing (Safe MTProto fallback active)
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env 2>/dev/null || touch .env
    else
        touch .env
    fi
fi

# 4. Dependency Health & Self-Healing Check
if ! python -c "import aiosqlite, telethon, rich, dotenv" 2>/dev/null; then
    echo "============================================================"
    echo "  🚀 Verifying & installing dependencies..."
    echo "============================================================"
    bash deploy/install_termux.sh
    if [ -d ".venv" ]; then
        source .venv/bin/activate 2>/dev/null || true
    fi
fi

# 4. Interactive Master Menu Loop
while true; do
    clear
    echo "=============================================================================="
    echo "  📱 TG KINDSYNC PRO — ANDROID TERMUX MASTER CONTROL (24/7)"
    echo "  👨‍⚕️ Kind Doctor & Team · Zero-Freeze Native Architecture"
    echo "=============================================================================="
    echo ""
    echo "  [1] Launch Interactive Engine (QR Login, Forwarder, Cloner, Indexer)"
    echo "  [2] Start 24/7 Background Autopilot (Screen-off continuous streaming)"
    echo "  [3] Start Kind Doctor Bot Daemon (@KindDoc_bot)"
    echo "  [4] Start DEVI Web Dashboard (Port 8080)"
    echo "  [5] Run Full System Verification & Health Check"
    echo "  [6] View Live 24/7 Background Logs"
    echo "  [7] Stop All Background Services (pkill)"
    echo "  [8] Re-run 1-Click Dependency Self-Heal"
    echo ""
    echo "  [0] Exit"
    echo "=============================================================================="
    echo ""
    read -p "Enter your choice [1-8 or 0]: " CHOICE

    case "$CHOICE" in
        1)
            clear
            echo "[*] Launching TG KindSync Pro Interactive Engine..."
            python tg_kindsync_pro.py
            echo ""
            read -p "Press Enter to return to menu..."
            ;;
        2)
            clear
            bash START_24_7_TERMUX.sh
            echo ""
            read -p "Press Enter to return to menu..."
            ;;
        3)
            clear
            echo "[*] Starting Kind Doctor Bot Daemon..."
            python -m devi.operator.telegram_bot
            echo ""
            read -p "Press Enter to return to menu..."
            ;;
        4)
            clear
            echo "[*] Starting Web Dashboard on http://localhost:8080 ..."
            python web_dashboard.py
            echo ""
            read -p "Press Enter to return to menu..."
            ;;
        5)
            clear
            echo "[*] Running System Verification Suite..."
            python tests/run_all_tests.py
            echo ""
            read -p "Press Enter to return to menu..."
            ;;
        6)
            clear
            echo "[*] Streaming live logs (Press Ctrl+C to return to menu)..."
            if [ -f "logs/forwarder_service.log" ]; then
                tail -f logs/forwarder_service.log
            else
                echo "No background log file found yet. Run option [2] first."
                echo ""
                read -p "Press Enter to return to menu..."
            fi
            ;;
        7)
            clear
            echo "[*] Stopping all background Python processes..."
            pkill -f "python.*tg_kindsync_pro" 2>/dev/null || true
            pkill -f "python.*telegram_bot" 2>/dev/null || true
            pkill -f "python.*web_dashboard" 2>/dev/null || true
            sleep 1
            echo "✅ All background services stopped successfully."
            echo ""
            read -p "Press Enter to return to menu..."
            ;;
        8)
            clear
            echo "[*] Re-running 1-Click Setup & Package Self-Heal..."
            bash deploy/install_termux.sh
            echo ""
            read -p "Press Enter to return to menu..."
            ;;
        0)
            echo ""
            echo "Exiting TG KindSync Pro. Keep learning & stay kind! 🩺"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please select from 1-8 or 0."
            sleep 2
            ;;
    esac
done


#!/usr/bin/env bash
# ==============================================================================
# 🚀 TG KINDSYNC PRO - ORACLE CLOUD FRIEND ISOLATED WORKSPACE SETUP
# ==============================================================================

set -e

FRIEND_DIR="/home/ubuntu/TG_KindSync_Friend"
SOURCE_DIR="/home/ubuntu/TG_KindSync_Pro"
USER_NAME="ubuntu"

echo "=============================================================================="
echo "    🚀 SETTING UP 100% ISOLATED FRIEND WORKSPACE ON ORACLE CLOUD (24/7)"
echo "=============================================================================="
echo ""

# 1. Create Isolated Directory
echo "[+] Step 1/4: Creating isolated directory ${FRIEND_DIR}..."
mkdir -p "${FRIEND_DIR}"
mkdir -p "${FRIEND_DIR}/logs"
mkdir -p "${FRIEND_DIR}/data"

# 2. Copy Code Files (NO personal sessions, NO personal databases)
echo "[+] Step 2/4: Copying core engine files..."
if [ -d "${SOURCE_DIR}" ]; then
    cp "${SOURCE_DIR}/tg_kindsync_pro.py" "${FRIEND_DIR}/" 2>/dev/null || true
    cp "${SOURCE_DIR}/main.py" "${FRIEND_DIR}/" 2>/dev/null || true
    cp "${SOURCE_DIR}/quick_setup.py" "${FRIEND_DIR}/" 2>/dev/null || true
    cp "${SOURCE_DIR}/web_dashboard.py" "${FRIEND_DIR}/" 2>/dev/null || true
    cp "${SOURCE_DIR}/sentinel_observer.py" "${FRIEND_DIR}/" 2>/dev/null || true
    cp "${SOURCE_DIR}/requirements.txt" "${FRIEND_DIR}/" 2>/dev/null || true
    if [ -d "${SOURCE_DIR}/devi" ]; then
        cp -r "${SOURCE_DIR}/devi" "${FRIEND_DIR}/" 2>/dev/null || true
    fi
    if [ -d "${SOURCE_DIR}/tools" ]; then
        cp -r "${SOURCE_DIR}/tools" "${FRIEND_DIR}/" 2>/dev/null || true
    fi
fi

cd "${FRIEND_DIR}"

# 3. Setup Python Virtual Environment
echo "[+] Step 3/4: Setting up virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

# Clear stale lock if any
rm -f engine.lock 2>/dev/null || true

# 4. Install & Enable 24/7 Systemd Background Service
echo "[+] Step 4/4: Configuring 24/7 Systemd Background Autopilot..."
sudo bash -c "cat << 'EOF' > /etc/systemd/system/tg-forwarder-friend.service
[Unit]
Description=TG KindSync Pro Friend 24/7 Live Forwarder Engine
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/TG_KindSync_Friend
Environment=TERM=xterm-256color
Environment=PYTHONPATH=/home/ubuntu/TG_KindSync_Friend
Environment=PYTHONUNBUFFERED=1
Environment=AUTO_START_LIVE=1
ExecStartPre=/bin/rm -f /home/ubuntu/TG_KindSync_Friend/engine.lock
ExecStart=/home/ubuntu/TG_KindSync_Friend/.venv/bin/python /home/ubuntu/TG_KindSync_Friend/main.py --live
Restart=always
RestartSec=5
StandardOutput=append:/home/ubuntu/TG_KindSync_Friend/logs/forwarder_service.log
StandardError=append:/home/ubuntu/TG_KindSync_Friend/logs/forwarder_service.log

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
sudo systemctl enable tg-forwarder-friend

# Helper scripts in home folder
cat << 'EOF' > /home/ubuntu/status_friend.sh
#!/usr/bin/env bash
sudo systemctl status tg-forwarder-friend --no-pager
echo ""
echo "--- Last 20 lines of Forwarder Live Log ---"
tail -n 20 /home/ubuntu/TG_KindSync_Friend/logs/forwarder_service.log 2>/dev/null || true
EOF
chmod +x /home/ubuntu/status_friend.sh

cat << 'EOF' > /home/ubuntu/view_live_friend.sh
#!/usr/bin/env bash
echo "Press Ctrl+C anytime to stop viewing logs (Bot will KEEP RUNNING in background)."
echo ""
tail -f /home/ubuntu/TG_KindSync_Friend/logs/forwarder_service.log
EOF
chmod +x /home/ubuntu/view_live_friend.sh

cat << 'EOF' > /home/ubuntu/restart_friend.sh
#!/usr/bin/env bash
echo "[*] Restarting Friend 24/7 Forwarder Service..."
sudo systemctl restart tg-forwarder-friend
sleep 2
sudo systemctl status tg-forwarder-friend --no-pager
EOF
chmod +x /home/ubuntu/restart_friend.sh

cat << 'EOF' > /home/ubuntu/stop_friend.sh
#!/usr/bin/env bash
echo "[*] Stopping Friend 24/7 Forwarder Service..."
sudo systemctl stop tg-forwarder-friend
echo "[OK] Stopped."
EOF
chmod +x /home/ubuntu/stop_friend.sh

# Check if session exists or user needs to login
if [ ! -f "session_forwarder.session" ]; then
    echo ""
    echo "=============================================================================="
    echo "  👋 TELEGRAM LOGIN REQUIRED (ONE-TIME SETUP)"
    echo "=============================================================================="
    echo "Please enter your Telegram phone number and OTP when prompted."
    echo ""
    "${FRIEND_DIR}/.venv/bin/python" tg_kindsync_pro.py
fi

# Clear any lock after interactive session
rm -f engine.lock 2>/dev/null || true

# Start 24/7 Service
echo ""
echo "[*] Activating 24/7 Autopilot Service on Oracle Cloud..."
sudo systemctl restart tg-forwarder-friend
sleep 2

echo ""
echo "=============================================================================="
echo "  🎉 24/7 AUTOPILOT IS NOW PERMANENTLY RUNNING ON ORACLE CLOUD!"
echo "=============================================================================="
echo ""
sudo systemctl status tg-forwarder-friend --no-pager
echo ""
echo "=============================================================================="
echo "✔ Friend's Forwarder is now running 24/7 in Background on Oracle VPS!"
echo "✔ Aap apna PC / Laptop band kar sakte hain, ye cloud par non-stop chalta rahega."
echo "=============================================================================="



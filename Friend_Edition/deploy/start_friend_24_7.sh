#!/usr/bin/env bash
# ==============================================================================
# 🚀 TG KINDSYNC PRO - 24/7 AUTOPILOT SYSTEMD SERVICE FOR FRIEND
# ==============================================================================

set -e

FRIEND_DIR="/home/ubuntu/TG_KindSync_Friend"
SERVICE_NAME="tg-forwarder-friend"

echo "=============================================================================="
echo "    🚀 ENABLING 24/7 LIVE AUTOPILOT ON ORACLE CLOUD FOR FRIEND"
echo "=============================================================================="

# 1. Update core engine files in friend folder if needed
if [ -d "/home/ubuntu/TG_KindSync_Pro" ]; then
    cp "/home/ubuntu/TG_KindSync_Pro/tg_kindsync_pro.py" "${FRIEND_DIR}/" 2>/dev/null || true
    cp "/home/ubuntu/TG_KindSync_Pro/main.py" "${FRIEND_DIR}/" 2>/dev/null || true
    cp "/home/ubuntu/TG_KindSync_Pro/quick_setup.py" "${FRIEND_DIR}/" 2>/dev/null || true
    cp "/home/ubuntu/TG_KindSync_Pro/web_dashboard.py" "${FRIEND_DIR}/" 2>/dev/null || true
    cp "/home/ubuntu/TG_KindSync_Pro/sentinel_observer.py" "${FRIEND_DIR}/" 2>/dev/null || true
    cp "/home/ubuntu/TG_KindSync_Pro/requirements.txt" "${FRIEND_DIR}/" 2>/dev/null || true
    if [ -d "/home/ubuntu/TG_KindSync_Pro/devi" ]; then
        cp -r "/home/ubuntu/TG_KindSync_Pro/devi" "${FRIEND_DIR}/" 2>/dev/null || true
    fi
    if [ -d "/home/ubuntu/TG_KindSync_Pro/tools" ]; then
        cp -r "/home/ubuntu/TG_KindSync_Pro/tools" "${FRIEND_DIR}/" 2>/dev/null || true
    fi
fi

# 2. Create Systemd Service for Friend
sudo bash -c "cat <<EOF > /etc/systemd/system/${SERVICE_NAME}.service
[Unit]
Description=TG KindSync Pro Friend 24/7 Live Forwarder Engine
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=${FRIEND_DIR}
Environment=TERM=xterm-256color
Environment=PYTHONPATH=${FRIEND_DIR}
Environment=PYTHONUNBUFFERED=1
Environment=AUTO_START_LIVE=1
ExecStartPre=/bin/rm -f ${FRIEND_DIR}/engine.lock
ExecStart=${FRIEND_DIR}/.venv/bin/python ${FRIEND_DIR}/main.py --live
Restart=always
RestartSec=5
StandardOutput=append:${FRIEND_DIR}/logs/forwarder_service.log
StandardError=append:${FRIEND_DIR}/logs/forwarder_service.log

[Install]
WantedBy=multi-user.target
EOF"

# 3. Reload systemd, enable on boot, and start service
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl restart ${SERVICE_NAME}

echo ""
echo "=============================================================================="
echo "  🎉 24/7 AUTOPILOT ACTIVATED SUCCESSFULLY!"
echo "=============================================================================="
echo ""
echo "Service Status:"
sudo systemctl status ${SERVICE_NAME} --no-pager
echo ""
echo "✔ Friend's Forwarder is now running 24/7 in Background on Oracle VPS!"
echo "✔ Aap apna PC / Laptop band kar sakte hain, ye cloud par non-stop chalta rahega."
echo "=============================================================================="

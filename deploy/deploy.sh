#!/usr/bin/env bash
# ==============================================================================
# 🚀 TGFORWARDER - 1-CLICK LINUX VPS DEPLOYMENT & SYSTEMD SETUP
# ==============================================================================

set -e

echo "============================================================"
echo "  🚀 TGFORWARDER CLOUD PRODUCTION INSTALLER"
echo "  - Kind Doctor & Team Enterprise Suite"
echo "============================================================"
echo ""

# Ensure we execute in project root directory
cd "$(dirname "$0")/.."
CURRENT_DIR=$(pwd)
CURRENT_USER=$(whoami)

# 1. Update system packages
echo "[+] Step 1/5: Installing System Dependencies & Build Tools..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv build-essential libffi-dev libssl-dev git curl iptables-persistent netfilter-persistent 2>/dev/null || sudo apt-get install -y python3 python3-pip python3-venv build-essential libffi-dev libssl-dev git curl

# 2. Setup Python Virtual Environment
echo "[+] Step 2/5: Setting up Python Virtual Environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Create Persistent Directories
mkdir -p logs db_backups

# 4. Open Port 8080 for Web Dashboard (Oracle Cloud Firewall)
echo "[+] Step 3/5: Opening Port 8080 in Oracle Cloud / Ubuntu Firewall..."
if command -v iptables &> /dev/null; then
    sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8080 -j ACCEPT 2>/dev/null || sudo iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
    if command -v netfilter-persistent &> /dev/null; then
        sudo netfilter-persistent save 2>/dev/null || true
    fi
fi

# 5. Create Systemd Background Services (Auto-Restart on Reboot)
echo "[+] Step 4/5: Creating Systemd Services for 24/7 Autopilot..."

sudo bash -c "cat <<EOF > /etc/systemd/system/tg-forwarder.service
[Unit]
Description=Telegram Forwarder Engine (Kind Doctor)
After=network.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${CURRENT_DIR}
ExecStart=${CURRENT_DIR}/.venv/bin/python ${CURRENT_DIR}/main.py
Restart=always
RestartSec=5
StandardOutput=append:${CURRENT_DIR}/logs/forwarder_service.log
StandardError=append:${CURRENT_DIR}/logs/forwarder_service.log

[Install]
WantedBy=multi-user.target
EOF"

sudo bash -c "cat <<EOF > /etc/systemd/system/tg-teacher.service
[Unit]
Description=Telegram Sentinel AI Teacher & Remote Command Center
After=network.target

[Service]
Type=simple
User=${CURRENT_USER}
WorkingDirectory=${CURRENT_DIR}
ExecStart=${CURRENT_DIR}/.venv/bin/python ${CURRENT_DIR}/sentinel_observer.py
Restart=always
RestartSec=5
StandardOutput=append:${CURRENT_DIR}/logs/teacher_service.log
StandardError=append:${CURRENT_DIR}/logs/teacher_service.log

[Install]
WantedBy=multi-user.target
EOF"

sudo systemctl daemon-reload
echo "[+] Step 4/4: Systemd Services Installed Successfully!"
echo ""
echo "============================================================"
echo "  🎉 DEPLOYMENT COMPLETE!"
echo "============================================================"
echo ""
echo "  To start both services in the background:"
echo "    sudo systemctl start tg-forwarder"
echo "    sudo systemctl start tg-teacher"
echo ""
echo "  To enable auto-start on VPS boot:"
echo "    sudo systemctl enable tg-forwarder"
echo "    sudo systemctl enable tg-teacher"
echo ""
echo "  To check live status:"
echo "    sudo systemctl status tg-forwarder"
echo "    tail -f logs/forwarder_service.log"
echo "============================================================"

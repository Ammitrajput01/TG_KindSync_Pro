# 🌐 TGForwarder — Oracle Cloud Always Free Tier (₹0 Forever) 24/7 Setup Guide

This guide explains how to host your **TGForwarder & Sentinel AI Teacher** online on **Oracle Cloud's Always Free Tier** so it runs **24/7 non-stop with Gigabit cloud speeds (1000 Mbps)** at **₹0 cost forever**, without needing your PC to stay turned on!

---

## 💎 Why Oracle Cloud Always Free Tier is Best:
- **Cost**: **₹0.00 Forever (100% Free for Life)**
- **Specs**: Up to **4 ARM OCPUs, 24 GB RAM, 200 GB NVMe Storage**
- **Network**: **1 Gbps unmetered bandwidth** + **Free Static Public IPv4 Address**
- **Link**: https://www.oracle.com/cloud/free/

---

## 🚀 Step 1: Create Your Free VPS on Oracle Cloud (Takes 3 Minutes)
1. Go to [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/) and sign up.
2. In the Oracle Cloud Console, go to **Compute** ➔ **Instances** ➔ Click **Create Instance**.
3. **Image**: Choose **Ubuntu 22.04 LTS** (or 24.04).
4. **Shape**: Click **Change Shape** ➔ Select **Ampere (ARM)** ➔ **VM.Standard.A1.Flex**:
   - Assign **2 to 4 OCPUs** and **12 to 24 GB RAM** (Labeled: *"Always Free Eligible"*).
5. **Networking**: Keep default VCN (Assign a public IPv4 address = Yes).
6. **SSH Keys**: Click **Save Private Key** (download it to your PC, e.g. `oracle_key.key`).
7. Click **Create**! Your server will turn **Green (Running)** in 60 seconds.
## 🚀 Step 2: Connect to Your Oracle VPS (via SSH)
Open Windows PowerShell on your PC and connect using the private key you downloaded:
```bash
ssh -i "path\to\oracle_key.key" ubuntu@YOUR_ORACLE_PUBLIC_IP
```

---

## 🚀 Step 3: Upload Your Project to Oracle Cloud
From your PC's PowerShell, upload this folder directly to your Oracle VPS:
```bash
scp -i "path\to\oracle_key.key" -r "c:\TGForwarder-New" ubuntu@YOUR_ORACLE_PUBLIC_IP:/home/ubuntu/TGForwarder
```

---

## 🚀 Step 4: Run the 1-Click Installer
On your Oracle VPS terminal, navigate to the folder and run:
```bash
cd /home/ubuntu/TGForwarder
chmod +x deploy/deploy.sh
./deploy/deploy.sh
```
*(The script will automatically install Python 3.12, create the virtual environment, open Port 8080 in Oracle's firewall, and install 24/7 background systemd services!)*

---

## 🎛️ Managing Your Online Bot:

### 1. Start Services:
```bash
sudo systemctl start tg-forwarder
sudo systemctl start tg-teacher
```

### 2. Enable Auto-Start on Server Reboot:
```bash
sudo systemctl enable tg-forwarder
sudo systemctl enable tg-teacher
```

### 3. Check Live Running Status:
```bash
sudo systemctl status tg-forwarder
sudo systemctl status tg-teacher
```

### 4. View Live Logs:
```bash
tail -f logs/forwarder_service.log
```

---

## 🐳 Alternative: Running with Docker (1-Command):

If your VPS has Docker installed, simply run:
```bash
docker compose up -d
```
To view live Docker logs:
```bash
docker compose logs -f
```

---

## 🌐 Accessing Web Dashboard from Phone Anywhere in the World:

When hosted on Oracle Cloud, you can open your live Web Dashboard on your phone's browser (even on 4G/5G mobile internet) from anywhere!

### 1. Open Port 8080 in Oracle Cloud Console (One-Time Setup):
1. Log in to your [Oracle Cloud Console](https://cloud.oracle.com).
2. Go to **Networking** ➔ **Virtual Cloud Networks (VCN)** ➔ Click your VCN.
3. Click on **Security Lists** (left sidebar) ➔ Click **Default Security List**.
4. Click **Add Ingress Rules**:
   - **Source CIDR**: `0.0.0.0/0`
   - **IP Protocol**: `TCP`
   - **Destination Port Range**: `8080`
   - **Description**: `TGForwarder Web Dashboard`
5. Click **Add Ingress Rules**.

### 2. Open on Phone:
Open your phone's browser and go to:
👉 `http://<YOUR-ORACLE-VPS-PUBLIC-IP>:8080`

You will see your live speedometer, delivered count, terminal logs, and can trigger 1-click cloud backups or pause/resume anytime, anywhere! 🚀

---

## 📱 Mobile Telegram Commands (Saved Messages):
In addition to the Web Dashboard, you can also send commands directly in Telegram **Saved Messages** on your phone:
- `/status`  • Live transmission velocity, RAM, and media breakdown
- `/report`  • Instant 24-hour throughput performance digest
- `/backup`  • 1-Click online SQLite database backup sent straight to Saved Messages
- `/errors`  • Inspect the last 5 failed transmissions with error details
- `/dlq`     • Dead Letter Queue count and self-healing status
- `/tips`    • Real-time AI Teacher optimization suggestions
- `/help`    • Complete command center manual

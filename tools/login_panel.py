#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
👑 TELEGRAM DUAL LOGIN PANEL & AUTHENTICATION WIZARD (QR + PHONE OTP)
📱 Tab 1: Instant QR Code Scan (Telethon qr_login)
📞 Tab 2: Phone Number + Official Telegram OTP + 2FA Cloud Password
💎 Modern Glassmorphism Medical / Cyberpunk Dark UI
================================================================================
"""

import os
import sys
import io
import time
import base64
import asyncio
import logging
import webbrowser
from pathlib import Path
from typing import Optional

from aiohttp import web
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import (
    SessionPasswordNeededError,
    PhoneNumberInvalidError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    FloodWaitError
)
import qrcode

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LoginPanel")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Forwarder Pro — Dual Login Wizard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0a0f1d;
            --bg-card: rgba(18, 24, 43, 0.85);
            --border-glass: rgba(255, 255, 255, 0.12);
            --accent-cyan: #00f2fe;
            --accent-blue: #4facfe;
            --accent-green: #00f2a9;
            --accent-red: #ff4757;
            --text-main: #f1f5f9;
            --text-dim: #94a3b8;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Outfit', sans-serif;
        }

        body {
            background: radial-gradient(circle at 50% 10%, #172554 0%, var(--bg-primary) 70%);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .login-card {
            background: var(--bg-card);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border-glass);
            border-radius: 24px;
            width: 100%;
            max-width: 480px;
            padding: 36px 32px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6), 0 0 35px rgba(0, 242, 254, 0.15);
            animation: fadeIn 0.4s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .header {
            text-align: center;
            margin-bottom: 28px;
        }

        .header .badge {
            display: inline-block;
            background: linear-gradient(135deg, rgba(79, 172, 254, 0.2), rgba(0, 242, 254, 0.2));
            color: var(--accent-cyan);
            border: 1px solid rgba(0, 242, 254, 0.3);
            border-radius: 50px;
            padding: 6px 16px;
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            margin-bottom: 12px;
            text-transform: uppercase;
        }

        .header h1 {
            font-size: 1.65rem;
            font-weight: 700;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, #ffffff 30%, var(--accent-cyan) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }

        .header p {
            font-size: 0.9rem;
            color: var(--text-dim);
        }

        .tabs {
            display: flex;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 14px;
            padding: 4px;
            margin-bottom: 28px;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .tab-btn {
            flex: 1;
            padding: 10px 14px;
            border: none;
            background: transparent;
            color: var(--text-dim);
            font-weight: 600;
            font-size: 0.88rem;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .tab-btn.active {
            background: linear-gradient(135deg, #3b82f6, #06b6d4);
            color: #ffffff;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.35);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease-out;
        }

        /* QR Code Tab */
        .qr-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }

        .qr-box {
            background: #ffffff;
            padding: 16px;
            border-radius: 18px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
            display: inline-block;
            position: relative;
        }

        .qr-box img {
            display: block;
            width: 220px;
            height: 220px;
            border-radius: 8px;
        }

        .qr-instruction {
            font-size: 0.88rem;
            color: var(--text-dim);
            line-height: 1.5;
            margin-bottom: 16px;
        }

        .qr-instruction strong {
            color: var(--accent-cyan);
        }

        /* Phone Tab */
        .form-group {
            margin-bottom: 18px;
        }

        .form-group label {
            display: block;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--text-dim);
        }

        .input-control {
            width: 100%;
            padding: 12px 16px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            color: #ffffff;
            font-size: 0.95rem;
            font-family: 'JetBrains Mono', monospace;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .input-control:focus {
            border-color: var(--accent-cyan);
            box-shadow: 0 0 15px rgba(0, 242, 254, 0.25);
        }

        .btn-submit {
            width: 100%;
            padding: 13px;
            background: linear-gradient(135deg, #00f2fe, #4facfe);
            color: #04101e;
            border: none;
            border-radius: 12px;
            font-weight: 700;
            font-size: 0.95rem;
            letter-spacing: 0.02em;
            cursor: pointer;
            transition: transform 0.15s, box-shadow 0.15s;
            margin-top: 8px;
        }

        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 242, 254, 0.4);
        }

        .btn-submit:active {
            transform: translateY(0);
        }

        .btn-submit:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }

        .alert-box {
            margin-top: 18px;
            padding: 12px 16px;
            border-radius: 10px;
            font-size: 0.85rem;
            display: none;
        }

        .alert-box.error {
            background: rgba(255, 71, 87, 0.15);
            border: 1px solid var(--accent-red);
            color: #ff7675;
            display: block;
        }

        .alert-box.success {
            background: rgba(0, 242, 169, 0.15);
            border: 1px solid var(--accent-green);
            color: var(--accent-green);
            display: block;
        }

        .alert-box.info {
            background: rgba(79, 172, 254, 0.15);
            border: 1px solid var(--accent-blue);
            color: var(--accent-cyan);
            display: block;
        }

        .status-pill {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            font-size: 0.82rem;
            color: var(--text-dim);
            margin-top: 20px;
        }

        .pulse-dot {
            width: 8px;
            height: 8px;
            background: var(--accent-green);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--accent-green);
            animation: pulse 1.8s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); opacity: 0.7; }
            50% { transform: scale(1.3); opacity: 1; }
            100% { transform: scale(0.95); opacity: 0.7; }
        }
    </style>
</head>
<body>

    <div class="login-card">
        <div class="header">
            <span class="badge">👨‍⚕️ Kind Doctor Suite</span>
            <h1>Telegram Connect</h1>
            <p>Choose your preferred login method to authorize session</p>
        </div>

        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('qr')">
                <span>📱</span> Instant QR Code
            </button>
            <button class="tab-btn" onclick="switchTab('phone')">
                <span>📞</span> Phone Number + OTP
            </button>
        </div>

        <!-- TAB 1: QR CODE -->
        <div id="tab-qr" class="tab-content active">
            <div class="qr-container">
                <div class="qr-box">
                    <img id="qr-img" src="" alt="Scan QR Code">
                </div>
                <div class="qr-instruction">
                    Open Telegram on your phone:<br>
                    <strong>Settings</strong> ➔ <strong>Devices</strong> ➔ <strong>Link Desktop Device</strong>
                </div>
                <div class="status-pill">
                    <div class="pulse-dot"></div>
                    <span id="qr-status-text">Waiting for Telegram scan...</span>
                </div>
            </div>
        </div>

        <!-- TAB 2: PHONE NUMBER + OTP -->
        <div id="tab-phone" class="tab-content">
            <div id="step-phone">
                <div class="form-group">
                    <label for="phone-input">Phone Number (with country code)</label>
                    <input type="text" id="phone-input" class="input-control" placeholder="+919876543210" value="+91">
                </div>
                <button id="btn-request-code" class="btn-submit" onclick="requestCode()">Send Official Code</button>
            </div>

            <div id="step-otp" style="display: none;">
                <div class="form-group">
                    <label for="otp-input">Enter 5-Digit Verification Code</label>
                    <input type="text" id="otp-input" class="input-control" placeholder="12345" maxlength="8">
                </div>
                <div class="form-group" id="group-2fa" style="display: none;">
                    <label for="pwd-input">2FA Cloud Password (Optional)</label>
                    <input type="password" id="pwd-input" class="input-control" placeholder="Your 2-Step Password">
                </div>
                <button id="btn-submit-code" class="btn-submit" onclick="submitCode()">Verify & Connect</button>
            </div>

            <div id="phone-alert" class="alert-box"></div>
        </div>

        <div id="global-success" class="alert-box success" style="margin-top: 24px; text-align: center; display: none;">
            🎉 <strong>Login Successful!</strong><br>
            Session authorized. You can close this tab and return to the terminal.
        </div>
    </div>

    <script>
        let currentTab = 'qr';
        let isAuthorized = false;

        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            if (tab === 'qr') {
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
                document.getElementById('tab-qr').classList.add('active');
            } else {
                document.querySelectorAll('.tab-btn')[1].classList.add('active');
                document.getElementById('tab-phone').classList.add('active');
            }
        }

        async function pollQR() {
            if (isAuthorized) return;
            try {
                const res = await fetch('/api/qr');
                const data = await res.json();
                if (data.qr_base64) {
                    document.getElementById('qr-img').src = data.qr_base64;
                }
                if (data.authorized) {
                    onLoginSuccess(data.user_name || 'Telegram User');
                    return;
                }
                setTimeout(pollQR, 2500);
            } catch (err) {
                setTimeout(pollQR, 3000);
            }
        }

        async function requestCode() {
            const phone = document.getElementById('phone-input').value.trim();
            const btn = document.getElementById('btn-request-code');
            const alert = document.getElementById('phone-alert');

            if (!phone || phone.length < 8) {
                showAlert('Please enter a valid phone number with country code.', 'error');
                return;
            }

            btn.disabled = true;
            btn.innerText = 'Requesting Code...';
            showAlert('Contacting Telegram MTProto servers...', 'info');

            try {
                const res = await fetch('/api/phone/request_code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ phone })
                });
                const data = await res.json();
                if (data.ok) {
                    document.getElementById('step-phone').style.display = 'none';
                    document.getElementById('step-otp').style.display = 'block';
                    showAlert('Code sent! Check your official Telegram app inbox.', 'success');
                } else {
                    showAlert(data.error || 'Failed to send code.', 'error');
                    btn.disabled = false;
                    btn.innerText = 'Send Official Code';
                }
            } catch (err) {
                showAlert('Network error connecting to login panel.', 'error');
                btn.disabled = false;
                btn.innerText = 'Send Official Code';
            }
        }

        async function submitCode() {
            const code = document.getElementById('otp-input').value.trim();
            const password = document.getElementById('pwd-input').value;
            const btn = document.getElementById('btn-submit-code');

            if (!code) {
                showAlert('Please enter the 5-digit Telegram code.', 'error');
                return;
            }

            btn.disabled = true;
            btn.innerText = 'Verifying...';

            try {
                const res = await fetch('/api/phone/submit_code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ code, password })
                });
                const data = await res.json();
                if (data.ok) {
                    onLoginSuccess(data.user_name || 'Telegram User');
                } else if (data.need_password) {
                    document.getElementById('group-2fa').style.display = 'block';
                    showAlert('Two-Step Verification (2FA) is enabled. Please enter your cloud password.', 'info');
                    btn.disabled = false;
                    btn.innerText = 'Verify 2FA Password';
                } else {
                    showAlert(data.error || 'Verification failed. Check the code.', 'error');
                    btn.disabled = false;
                    btn.innerText = 'Verify & Connect';
                }
            } catch (err) {
                showAlert('Network error validating code.', 'error');
                btn.disabled = false;
                btn.innerText = 'Verify & Connect';
            }
        }

        function showAlert(msg, type) {
            const alert = document.getElementById('phone-alert');
            alert.className = 'alert-box ' + type;
            alert.innerText = msg;
            alert.style.display = 'block';
        }

        function onLoginSuccess(userName) {
            isAuthorized = true;
            document.getElementById('tab-qr').style.display = 'none';
            document.getElementById('tab-phone').style.display = 'none';
            document.querySelector('.tabs').style.display = 'none';
            const s = document.getElementById('global-success');
            s.innerHTML = `🎉 <strong>Login Successful!</strong><br>Welcome <strong>${userName}</strong>.<br><span style="font-size:0.8rem; color:#94a3b8;">Session saved safely. Returning to terminal...</span>`;
            s.style.display = 'block';
            setTimeout(() => {
                window.close();
            }, 3500);
        }

        // Start QR polling
        pollQR();
    </script>
</body>
</html>
"""

class DualLoginServer:
    def __init__(self, client: TelegramClient, host: str = "127.0.0.1", port: int = 5005):
        self.client = client
        self.host = host
        self.port = port
        self.app = web.Application()
        self.runner: Optional[web.AppRunner] = None
        self.qr_login_obj = None
        self.current_qr_base64 = ""
        self.current_phone = ""
        self.phone_code_hash = ""
        self.is_authorized = False
        self.user_name = ""
        self.setup_routes()

    def setup_routes(self):
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/api/qr", self.handle_get_qr)
        self.app.router.add_post("/api/phone/request_code", self.handle_request_code)
        self.app.router.add_post("/api/phone/submit_code", self.handle_submit_code)
        self.app.router.add_get("/api/status", self.handle_status)

    async def handle_index(self, request):
        return web.Response(text=HTML_TEMPLATE, content_type="text/html")

    async def _generate_qr_image(self, url: str) -> str:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=2,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{b64}"

    async def handle_get_qr(self, request):
        if self.is_authorized:
            return web.json_response({"authorized": True, "user_name": self.user_name})

        if not self.client.is_connected():
            await self.client.connect()

        if await self.client.is_user_authorized():
            self.is_authorized = True
            me = await self.client.get_me()
            self.user_name = getattr(me, 'first_name', '') or getattr(me, 'username', 'User')
            return web.json_response({"authorized": True, "user_name": self.user_name})

        if not self.qr_login_obj:
            try:
                self.qr_login_obj = await self.client.qr_login()
                self.current_qr_base64 = await self._generate_qr_image(self.qr_login_obj.url)
                # Background listener for scan
                asyncio.create_task(self._wait_for_qr_scan())
            except Exception as e:
                logger.error(f"Error initiating QR login: {e}")
        elif self.qr_login_obj and hasattr(self.qr_login_obj, "expires") and self.qr_login_obj.expires:
            if time.time() > self.qr_login_obj.expires.timestamp():
                try:
                    await self.qr_login_obj.recreate()
                    self.current_qr_base64 = await self._generate_qr_image(self.qr_login_obj.url)
                except Exception as e:
                    logger.error(f"Error recreating QR code: {e}")

        return web.json_response({
            "authorized": self.is_authorized,
            "qr_base64": self.current_qr_base64,
            "user_name": self.user_name
        })

    async def _wait_for_qr_scan(self):
        if not self.qr_login_obj:
            return
        try:
            user = await self.qr_login_obj.wait(timeout=180)
            if user:
                self.is_authorized = True
                self.user_name = getattr(user, 'first_name', '') or getattr(user, 'username', 'User')
                logger.info(f"🎉 QR Login successful for {self.user_name}!")
        except SessionPasswordNeededError:
            logger.info("QR Scanned, 2FA Cloud Password required.")
        except Exception as e:
            logger.debug(f"QR wait timeout or recreate: {e}")

    async def handle_request_code(self, request):
        try:
            data = await request.json()
            phone = data.get("phone", "").strip().replace(" ", "").replace("-", "")
            if not phone.startswith("+"):
                phone = "+" + phone

            self.current_phone = phone
            sent_code = await self.client.send_code_request(phone)
            self.phone_code_hash = sent_code.phone_code_hash
            return web.json_response({"ok": True, "phone": phone})
        except PhoneNumberInvalidError:
            return web.json_response({"ok": False, "error": "Invalid Phone Number. Include country code (e.g. +91)."})
        except FloodWaitError as fe:
            return web.json_response({"ok": False, "error": f"Rate limited by Telegram. Wait {fe.seconds} seconds."})
        except Exception as e:
            return web.json_response({"ok": False, "error": str(e)})

    async def handle_submit_code(self, request):
        try:
            data = await request.json()
            code = data.get("code", "").strip()
            password = data.get("password", "")

            try:
                if password:
                    me = await self.client.sign_in(password=password)
                else:
                    me = await self.client.sign_in(
                        phone=self.current_phone,
                        code=code,
                        phone_code_hash=self.phone_code_hash
                    )
            except SessionPasswordNeededError:
                return web.json_response({"ok": False, "need_password": True})

            if me:
                self.is_authorized = True
                self.user_name = getattr(me, 'first_name', '') or getattr(me, 'username', 'User')
                return web.json_response({"ok": True, "user_name": self.user_name})
            return web.json_response({"ok": False, "error": "Unknown error during sign in."})
        except PhoneCodeInvalidError:
            return web.json_response({"ok": False, "error": "Invalid 5-digit code entered. Check Telegram chat."})
        except PhoneCodeExpiredError:
            return web.json_response({"ok": False, "error": "Code expired. Please request a new code."})
        except Exception as e:
            return web.json_response({"ok": False, "error": str(e)})

    async def handle_status(self, request):
        return web.json_response({"authorized": self.is_authorized, "user_name": self.user_name})

    async def start(self):
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, self.host, self.port)
        await site.start()
        logger.info(f"✨ Dual Login Web Panel started at: http://{self.host}:{self.port}")

    async def stop(self):
        if self.runner:
            await self.runner.cleanup()

async def launch_dual_login_wizard(client: TelegramClient, port: int = 5005) -> bool:
    """Launches the dual login web server and opens browser tab for 1-click onboarding."""
    if not client.is_connected():
        await client.connect()

    if await client.is_user_authorized():
        return True

    server = DualLoginServer(client, port=port)
    await server.start()
    
    url = f"http://127.0.0.1:{port}"
    print(f"\n=======================================================")
    print(f"🔗 OPENING VISUAL DUAL LOGIN PANEL:")
    print(f"   {url}")
    print(f"=======================================================\n")
    try:
        webbrowser.open(url)
    except Exception:
        pass

    # Wait until authorized or interrupted
    start_t = time.time()
    while time.time() - start_t < 300: # 5 min timeout
        if server.is_authorized or await client.is_user_authorized():
            await asyncio.sleep(2.0)
            await server.stop()
            return True
        await asyncio.sleep(1.0)

    await server.stop()
    return await client.is_user_authorized()

if __name__ == "__main__":
    load_dotenv()
    api_id = int(os.getenv("API_ID", 0) or 0) or 2040
    api_hash = os.getenv("API_HASH", "").strip() or "b18441a1ff607e10a989891a5462e627"
    client = TelegramClient("session_forwarder", api_id, api_hash)
    asyncio.run(launch_dual_login_wizard(client))


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DEVI Enterprise Multi-Channel Batch Completion Notifier
Dispatches instant completion alerts across:
1. Telegram Master Admin DM (@Kinddoctor4u, @Ammitrajput1) with high-priority audio chime
2. WhatsApp Message via CallMeBot / Twilio Webhook
3. Mobile SMS via Fast2SMS / Twilio Gateway
4. Free Mobile Lock-Screen Push via ntfy.sh (Zero-auth, instant phone ring)
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from contextlib import suppress
from datetime import datetime

import aiohttp
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(ROOT_DIR / ".env")

logger = logging.getLogger("DEVI.Notifier")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Master Admin IDs (Strictly Primary 1: 1553619403, Primary 2: 759038032)
PRIMARY_ADMINS = [1553619403, 759038032]


class MultiChannelNotifier:
    """Dispatches asynchronous alerts across Telegram, WhatsApp, SMS, and ntfy.sh."""

    def __init__(self):
        self.bot_token = os.getenv("DEVI_TELEGRAM_BOT_TOKEN", "").strip().strip("'").strip('"')
        self.phone_number = os.getenv("NOTIFIER_PHONE_NUMBER", "").strip().replace(" ", "").replace("-", "")
        self.whatsapp_apikey = os.getenv("CALLMEBOT_API_KEY", "").strip()
        self.fast2sms_key = os.getenv("FAST2SMS_API_KEY", "").strip()
        self.ntfy_topic = os.getenv("NTFY_TOPIC", "ammit_kindsync_alerts").strip()

    async def send_all(
        self,
        title: str,
        message: str,
        stats: Optional[Dict[str, Any]] = None,
        job_type: str = "Batch Clone"
    ) -> Dict[str, bool]:
        """
        Broadcasts completion notification across all enabled channels concurrently.
        Returns a dict of channel delivery statuses.
        """
        results = {}
        now_str = datetime.now().strftime("%A, %d-%B-%Y | %I:%M %p")
        
        # Prepare rich formatted payload
        stat_lines = ""
        if stats:
            stat_lines = "\n".join([f"• {k}: {v}" for k, v in stats.items()])
        
        full_text = (
            f"🎉 {title.upper()}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⚡ Task: {job_type}\n"
            f"📅 Completed: {now_str}\n"
            f"{'━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n' + stat_lines if stat_lines else ''}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{message}\n"
        )

        tasks = [
            self.send_telegram_alert(full_text),
            self.send_ntfy_push(title, full_text),
        ]
        
        if self.phone_number and self.whatsapp_apikey:
            tasks.append(self.send_whatsapp_alert(full_text))
            
        if self.phone_number and self.fast2sms_key:
            tasks.append(self.send_sms_alert(f"{title}: {message}"))

        res = await asyncio.gather(*tasks, return_exceptions=True)
        
        results["telegram"] = res[0] is True
        results["ntfy"] = res[1] is True
        if len(tasks) > 2 and self.whatsapp_apikey:
            results["whatsapp"] = res[2] is True
        if len(tasks) > 3 and self.fast2sms_key:
            results["sms"] = res[-1] is True

        logger.info(f"[Notifier] Broadcast complete. Results: {results}")
        return results

    async def send_telegram_alert(self, text: str) -> bool:
        """Sends high-priority Telegram alert to Primary Admins with unmuted loud chime."""
        if not self.bot_token:
            logger.warning("[Notifier] No Telegram Bot Token configured.")
            return False

        success = False
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            for admin_id in PRIMARY_ADMINS:
                try:
                    url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                    payload = {
                        "chat_id": admin_id,
                        "text": text,
                        "parse_mode": "HTML",
                        "disable_notification": False  # Force loud chime notification
                    }
                    async with session.post(url, json=payload) as resp:
                        if resp.status == 200:
                            success = True
                            logger.info(f"[Notifier] Telegram alert delivered to Admin {admin_id}")
                        else:
                            # Fallback plain text if HTML parsing failed
                            payload.pop("parse_mode", None)
                            async with session.post(url, json=payload) as resp2:
                                if resp2.status == 200:
                                    success = True
                except Exception as e:
                    logger.warning(f"[Notifier] Telegram delivery to {admin_id} error: {e}")
        return success

    async def send_ntfy_push(self, title: str, text: str) -> bool:
        """Sends instant push notification via free open-source ntfy.sh (phone lock-screen ring)."""
        if not self.ntfy_topic:
            return False

        try:
            url = f"https://ntfy.sh/{self.ntfy_topic}"
            headers = {
                "Title": title,
                "Priority": "urgent",
                "Tags": "tada,bell,white_check_mark"
            }
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=8)) as session:
                async with session.post(url, data=text.encode("utf-8"), headers=headers) as resp:
                    if resp.status == 200:
                        logger.info(f"[Notifier] ntfy.sh push alert delivered to topic '{self.ntfy_topic}'")
                        return True
        except Exception as e:
            logger.warning(f"[Notifier] ntfy.sh alert error: {e}")
        return False

    async def send_whatsapp_alert(self, text: str) -> bool:
        """Sends direct personal WhatsApp alert via CallMeBot free API."""
        if not self.phone_number or not self.whatsapp_apikey:
            return False

        try:
            clean_phone = self.phone_number
            if not clean_phone.startswith("+"):
                clean_phone = "+" + clean_phone

            import urllib.parse
            encoded_msg = urllib.parse.quote_plus(text)
            url = f"https://api.callmebot.com/whatsapp.php?phone={clean_phone}&text={encoded_msg}&apikey={self.whatsapp_apikey}"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        logger.info(f"[Notifier] WhatsApp message delivered to {clean_phone}")
                        return True
        except Exception as e:
            logger.warning(f"[Notifier] WhatsApp alert error: {e}")
        return False

    async def send_sms_alert(self, short_text: str) -> bool:
        """Sends direct GSM text SMS to Indian mobile number via Fast2SMS gateway."""
        if not self.phone_number or not self.fast2sms_key:
            return False

        try:
            clean_phone = self.phone_number.replace("+91", "").replace("+", "")
            url = "https://www.fast2sms.com/dev/bulkV2"
            headers = {
                "authorization": self.fast2sms_key,
                "Content-Type": "application/json"
            }
            payload = {
                "route": "v3",
                "sender_id": "TXTIND",
                "message": short_text[:150],  # Standard 160-char GSM SMS slice
                "language": "english",
                "flash": 0,
                "numbers": clean_phone
            }
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.post(url, json=payload, headers=headers) as resp:
                    if resp.status == 200:
                        logger.info(f"[Notifier] Mobile text SMS delivered to {clean_phone}")
                        return True
        except Exception as e:
            logger.warning(f"[Notifier] Fast2SMS alert error: {e}")
        return False


# Global singleton instance for easy import
notifier = MultiChannelNotifier()

if __name__ == "__main__":
    async def _test():
        print("Testing MultiChannelNotifier local dispatch...")
        res = await notifier.send_all(
            title="KindSync Batch Complete Test",
            message="All 150 medical video lectures have been mirrored with zero errors.",
            stats={"Total Files": 150, "Total Volume": "4.2 GB", "Elapsed": "1h 24m"},
            job_type="Test Verification Job"
        )
        print("Test results:", res)

    asyncio.run(_test())

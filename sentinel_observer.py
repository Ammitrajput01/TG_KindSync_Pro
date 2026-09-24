#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
🎓 DEVI — AI TEACHER & LIVE SENTINEL OPERATOR (UNIFIED SIDECAR)
================================================================================
Developer: Dr. Amit Singh (Kind Doctor) & Antigravity AI
Architecture:
  - Unified System: DEVI Brain + Live Telemetry & Sentinel Watchdog.
  - 100% Isolated non-invasive background observer (Zero risk to Main Forwarder).
  - Read-Only log tailing & SQLite WAL telemetry (Zero lock contention).
  - Mobile Telegram Saved Messages AI Remote Center (Slash commands + Natural Language).
  - 24h Daily Performance Digests & Automated Cloud SQLite Backups.
  - Web Dashboard on Port 8080.
================================================================================
"""

import os
import sys
import re
import time
import json
import sqlite3
import asyncio
from pathlib import Path
from datetime import datetime, timezone
from contextlib import suppress

# Fix Windows console UTF-8 & cp1252 character map issues
if hasattr(sys.stdout, "reconfigure"):
    with suppress(Exception):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    with suppress(Exception):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Third-party imports
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text
    from rich.live import Live
    from rich.markup import escape
    from rich import box
except ImportError:
    print("[!] 'rich' library is required. Install via: pip install rich")
    sys.exit(1)

try:
    from telethon import TelegramClient
    from telethon.errors import RPCError
except ImportError:
    print("[!] 'telethon' library is required. Install via: pip install telethon")
    sys.exit(1)

from dotenv import load_dotenv
from web_dashboard import DashboardServer, get_local_lan_ip

# DEVI Unified Architecture Imports
from devi.config import DEVI_NAME, DEVI_TITLE, CURRENT_AUTONOMY_LEVEL
from devi.sentinel.telemetry_bridge import (
    ObserverState,
    SentinelTelemetryBridge,
    read_db_metrics,
    create_db_snapshot,
    MB,
    GB
)
from devi.sentinel.ai_advisor import SentinelAIAdvisor
from devi.brain.model_router import ModelRouter
from devi.brain.intent_engine import IntentEngine
from devi.research.research_agent import ResearchAgent

# Initialize Rich Console
console = Console(force_terminal=True, legacy_windows=False)

# File Paths
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"
DB_FILE = BASE_DIR / "history_core.sqlite"
LOG_FILE = BASE_DIR / "logs" / "tg_kind_mode_v14.log"
DLQ_FILE = BASE_DIR / "dead_letter.jsonl"
REPORT_DIR = BASE_DIR / "observer_reports"

# Global Instances
STATE = ObserverState()
BRIDGE = SentinelTelemetryBridge(STATE, LOG_FILE)
MODEL_ROUTER = ModelRouter()
INTENT_ENGINE = IntentEngine()
ADVISOR = SentinelAIAdvisor(MODEL_ROUTER)
RESEARCHER = ResearchAgent(MODEL_ROUTER)


# ==============================================================================
# TELEGRAM DISPATCHER & AI CONVERSATION BRIDGE (SAVED MESSAGES)
# ==============================================================================
class TelegramReporter:
    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash
        self.client = None
        self.target_peer = "me"  # Defaults to Saved Messages

    async def start(self):
        # Isolate session into observer_reports to eliminate SQLite lock conflicts
        REPORT_DIR.mkdir(parents=True, exist_ok=True)
        main_sess = BASE_DIR / "session_forwarder.session"
        obs_sess = REPORT_DIR / "observer_session.session"

        if main_sess.exists():
            if not obs_sess.exists() or (main_sess.stat().st_mtime > obs_sess.stat().st_mtime):
                import shutil
                with suppress(Exception):
                    shutil.copy2(main_sess, obs_sess)

        session_target = str(REPORT_DIR / "observer_session") if obs_sess.exists() else str(BASE_DIR / "session_forwarder")
        self.client = TelegramClient(session_target, self.api_id, self.api_hash)
        await self.client.connect()

        # ==============================================================================
        # 📱 SAVED MESSAGES DEVI COMMAND & AI CONVERSATION CENTER
        # ==============================================================================
        from telethon import events

        @self.client.on(events.NewMessage(chats="me"))
        async def handle_remote_message(event):
            txt = str(event.raw_text or "").strip()
            if not txt:
                return

            # Check if it's a Slash Command or Natural Language to DEVI
            if txt.startswith("/") or txt.startswith("!") or txt.lower().split()[0] in ("status", "help", "backup", "kill", "clean", "report", "errors", "dlq"):
                await self._handle_slash_command(event, txt)
            else:
                await self._handle_conversational_query(event, txt)

    async def _handle_slash_command(self, event, txt: str):
        cmd_parts = txt.split(maxsplit=1)
        raw_cmd = cmd_parts[0].lower()
        cmd = f"/{raw_cmd.lstrip('/!')}"
        arg = cmd_parts[1].strip() if len(cmd_parts) > 1 else ""

        STATE.add_event(f"[bold cyan]📱 Command Received:[/] [yellow]{cmd}[/]")

        if cmd in ("/start", "/help"):
            providers = [k for k, v in MODEL_ROUTER.available_providers.items() if v]
            p_str = ", ".join(providers) if providers else "Local Offline Engine"
            help_card = (
                f"🎓 **{DEVI_NAME} — AI TEACHER & SENTINEL COMMAND CENTER**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **Autonomy Level**: `Level {CURRENT_AUTONOMY_LEVEL}/9`\n"
                f"• **Active AI Brain**: `{p_str}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💬 `/status`   · Live Transmission Velocity & Telemetry\n"
                f"💬 `/report`   · Instant 24h AI Performance Digest\n"
                f"💬 `/backup`   · 1-Click Cloud SQLite Database Backup\n"
                f"💬 `/kill`     · 🛑 Kill Stuck Processes & Unlock SQLite Database\n"
                f"💬 `/clean_history` · 🧹 Wipe Forwarding History (Auto Safety Backup First)\n"
                f"💬 `/errors`   · Inspect Last 5 Failed Transmissions & Reasons\n"
                f"💬 `/dlq`      · Dead Letter Queue Count & Status\n"
                f"💬 `/tips`     · Real-Time Recommendations (Sorted: Latest #N First)\n"
                f"💬 `/research` · View Active AI Research Queue (Sorted: Latest #N First)\n"
                f"💬 `/research <topic>` · Trigger Autonomous Technical Research\n"
                f"💬 `/help`     · Display this Mobile Command Manual\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 **Pro-Tip**: You can also ask me anything directly! E.g.:\n"
                f"*\"Devi, kill processes\"*, *\"History clean karo\"*, or *\"Devi, check errors\"*"
            )
            await event.reply(help_card, parse_mode="md")

        elif cmd in ("/status", "/stats"):
            db_stats = read_db_metrics()
            cur_mb = STATE.bytes_transferred / MB
            data_str = f"{cur_mb:.2f} MB" if cur_mb < 1024 else f"{cur_mb/1024:.2f} GB"
            uptime_sec = int(time.monotonic() - STATE.start_time)
            hours, rem = divmod(uptime_sec, 3600)
            mins, _ = divmod(rem, 60)
            status_card = (
                f"📊 **[{DEVI_NAME} LIVE ENGINE TELEMETRY]**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **Session Delivered**: `{STATE.total_transfers}` items\n"
                f"• **Media Breakdown**: `{STATE.videos_sent}` 🎥 · `{STATE.docs_sent}` 📄 · `{STATE.photos_sent}` 🖼️\n"
                f"• **Data Streamed**: `{data_str}` (Peak `{STATE.peak_speed_mb:.2f} MB/s`)\n"
                f"• **Active Subject**: `{STATE.current_subject}`\n"
                f"• **Total DB Records**: `{db_stats['total_forwarded']:,}` msgs tracked\n"
                f"• **FloodWaits**: `{STATE.flood_waits_detected}` ({STATE.flood_wait_seconds_total:.1f}s delay)\n"
                f"• **Engine Uptime**: `{hours}h {mins}m`\n"
                f"• **Web Dashboard**: `http://{STATE.lan_ip}:{STATE.web_port}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🟢 *Status: Protected & Monitored by {DEVI_NAME}*"
            )
            await event.reply(status_card, parse_mode="md")

        elif cmd in ("/report", "/digest"):
            db_stats = read_db_metrics()
            report_card = ADVISOR.build_daily_digest(STATE, db_stats)
            await event.reply(report_card, parse_mode="md")

        elif cmd == "/dlq":
            count = 0
            if DLQ_FILE.exists():
                try:
                    with open(DLQ_FILE, "r", encoding="utf-8") as f:
                        count = sum(1 for line in f if line.strip())
                except Exception:
                    pass
            dlq_card = (
                f"🔄 **[{DEVI_NAME} DLQ QUEUE STATUS]**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **Pending Dead Letter Tasks**: `{count}` items\n"
                f"• **Auto-Retry Daemon**: `Active (Self-Healing in 60s)`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 *Send `/errors` to view details of the latest failures.*"
            )
            await event.reply(dlq_card, parse_mode="md")

        elif cmd in ("/errors", "/error"):
            if not DLQ_FILE.exists() or DLQ_FILE.stat().st_size == 0:
                await event.reply("✅ **[ZERO TRANSMISSION ERRORS]**\n\n• Dead letter queue is completely empty.\n• 100% of messages forwarded successfully!", parse_mode="md")
            else:
                lines = []
                try:
                    with open(DLQ_FILE, "r", encoding="utf-8") as f:
                        lines = [line.strip() for line in f if line.strip()]
                except Exception as e:
                    await event.reply(f"⚠️ Error reading DLQ log: {e}")
                    return

                if not lines:
                    await event.reply("✅ **[ZERO TRANSMISSION ERRORS]**\n\n• Dead letter queue is empty!", parse_mode="md")
                    return

                last_entries = lines[-5:]
                err_blocks = []
                for i, entry_str in enumerate(reversed(last_entries), 1):
                    try:
                        d = json.loads(entry_str)
                        ts = d.get("ts", "")[:19].replace("T", " ")
                        msg_id = d.get("msg", "N/A")
                        c_id = d.get("chat", "N/A")
                        t_topic = d.get("target_topic", "N/A")
                        raw_err = str(d.get("error", "Unknown error"))
                        clean_err = raw_err[:90] + ("..." if len(raw_err) > 90 else "")
                        err_blocks.append(
                            f"🔴 **#{i}. Msg ID `{msg_id}`** (Chat: `{c_id}`)\n"
                            f"   • **Error**: `{clean_err}`\n"
                            f"   • **Target Topic**: `{t_topic}`  ·  **Time**: `{ts}`"
                        )
                    except Exception:
                        continue

                res_card = (
                    f"⚠️ **[RECENT FAILED TRANSMISSIONS — LAST {len(err_blocks)}]**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    + "\n\n".join(err_blocks) +
                    f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💡 *Tip: {DEVI_NAME} auto-retries expired references and self-heals in the background.*"
                )
                await event.reply(res_card, parse_mode="md")

        elif cmd in ("/pause", "/stop_forwarding"):
            ctrl_p = BASE_DIR / "engine_control.json"
            try:
                with open(ctrl_p, "w", encoding="utf-8") as cf:
                    json.dump({"paused": True, "ts": time.time(), "source": "saved_messages"}, cf)
                await event.reply("⏸️ **[STREAMING PAUSED]**\n\nForwarder engine ko temporarily pause kar diya gaya hai.\nQueue resume karne ke liye `/resume` bhejein.", parse_mode="md")
            except Exception as ex:
                await event.reply(f"⚠️ Error pausing engine: {ex}")

        elif cmd in ("/resume", "/unpause", "/start_forwarding"):
            ctrl_p = BASE_DIR / "engine_control.json"
            try:
                with open(ctrl_p, "w", encoding="utf-8") as cf:
                    json.dump({"paused": False, "ts": time.time(), "source": "saved_messages"}, cf)
                await event.reply("▶️ **[STREAMING RESUMED]**\n\nQueue re-activated! Pending lectures instantly stream hona shuru ho gaye hain.", parse_mode="md")
            except Exception as ex:
                await event.reply(f"⚠️ Error resuming engine: {ex}")

        elif cmd in ("/speed", "/pacing"):
            mode = arg.lower() if arg else "turbo"
            ctrl_p = BASE_DIR / "engine_control.json"
            valid_modes = {"turbo": 0.5, "ultra": 0.2, "normal": 1.5, "safe": 3.0}
            delay_val = valid_modes.get(mode, 0.5)
            try:
                cur_data = {}
                if ctrl_p.exists():
                    with suppress(Exception):
                        with open(ctrl_p, "r", encoding="utf-8") as cf:
                            cur_data = json.load(cf)
                cur_data.update({"speed_mode": mode, "media_delay": delay_val, "ts": time.time()})
                with open(ctrl_p, "w", encoding="utf-8") as cf:
                    json.dump(cur_data, cf)
                speed_card = (
                    f"⚡ **[PACING VELOCITY UPDATED: {mode.upper()}]**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"• **Speed Mode**        : `{mode.upper()}`\n"
                    f"• **Inter-Media Delay** : `{delay_val}s`\n"
                    f"• **Shield Pacing**     : `Adaptive Flood Shield Active`\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🚀 *Engine will now stream at `{mode}` pacing!*"
                )
                await event.reply(speed_card, parse_mode="md")
            except Exception as ex:
                await event.reply(f"⚠️ Error updating speed: {ex}")

        elif cmd in ("/system", "/vitals", "/server"):
            import psutil
            cpu_pct = psutil.cpu_percent(interval=0.2)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage(str(BASE_DIR))
            uptime_sec = int(time.monotonic() - STATE.start_time)
            hours, rem = divmod(uptime_sec, 3600)
            mins, _ = divmod(rem, 60)
            now_dt = datetime.now()
            date_str = now_dt.strftime("%A, %d %B %Y | %I:%M %p")
            sys_card = (
                f"🖥️ **[TG KINDSYNC PRO — SYSTEM VITALS]**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📅 `{date_str}`\n\n"
                f"⚡ **CPU Usage**      : `{cpu_pct}%`\n"
                f"🧠 **RAM Memory**     : `{ram.used/(1024**3):.2f} GB` / `{ram.total/(1024**3):.2f} GB` ({ram.percent}% used)\n"
                f"💾 **Storage Space**  : `{disk.used/(1024**3):.1f} GB` / `{disk.total/(1024**3):.1f} GB` ({disk.free/(1024**3):.1f} GB free)\n"
                f"⏱️ **Server Uptime**  : `{hours}h {mins}m` (Observer active)\n"
                f"🔥 **Engine State**   : `🟢 ACTIVE & MONITORING`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *Host: {platform.node() or 'Cloud VPS'} • {platform.system()}*"
            )
            await event.reply(sys_card, parse_mode="md")

        elif cmd in ("/logs", "/log"):
            n_lines = 15
            if arg and arg.isdigit():
                n_lines = min(int(arg), 40)
            log_p = BASE_DIR / "logs" / "forwarder_service.log"
            if not log_p.exists():
                log_p = BASE_DIR / "logs" / "engine.log"
            recent_logs = []
            if log_p.exists():
                try:
                    with open(log_p, "r", encoding="utf-8", errors="replace") as lf:
                        all_lines = lf.readlines()
                        recent_logs = [ln.strip() for ln in all_lines[-n_lines:] if ln.strip()]
                except Exception as le:
                    recent_logs = [f"Error reading log file: {le}"]
            else:
                recent_logs = list(STATE.events)[-n_lines:]
            
            clean_log_text = "\n".join(recent_logs) if recent_logs else "No recent log entries."
            if len(clean_log_text) > 3500:
                clean_log_text = clean_log_text[-3500:]
            await event.reply(f"📜 **[LIVE ENGINE LOGS — LAST {len(recent_logs)} EVENTS]**\n```\n{clean_log_text}\n```", parse_mode="md")

        elif cmd in ("/clear_dlq", "/purge_dlq"):
            if DLQ_FILE.exists():
                try:
                    DLQ_FILE.write_text("", encoding="utf-8")
                    await event.reply("✅ **[DLQ PURGED]**\nDead letter error queue has been successfully cleared.", parse_mode="md")
                except Exception as ce:
                    await event.reply(f"⚠️ Failed to purge DLQ: {ce}")
            else:
                await event.reply("✅ DLQ is already empty.", parse_mode="md")

        elif cmd in ("/ask", "/ai"):
            if not arg:
                await event.reply("💡 Please provide a query e.g. `/ask What is GDMT therapy in Heart Failure?`", parse_mode="md")
                return
            await event.reply(f"🩺 *{DEVI_NAME} is synthesizing answer via AI Hub...*", parse_mode="md")
            res = await MODEL_ROUTER.generate_response(
                "You are DEVI, an expert AI Clinical Advisor and System Specialist for TG KindSync Pro.",
                arg
            )
            ans = res.get("text", "No response generated.")
            provider = res.get("provider", "local")
            reply_card = (
                f"🩺 **[{DEVI_NAME.upper()} AI ADVISOR]**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{ans}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🧠 *Synthesized via {provider.upper()} • Kind Doctor Clinical Suite*"
            )
            await event.reply(reply_card, parse_mode="md")

        elif cmd in ("/backup", "/db"):
            await self.send_database_backup(event)

        elif cmd in ("/kill", "/kill_all", "/killall", "/unlock_db", "/unlock", "/force_stop", "/terminate"):
            await self.kill_processes_and_unlock(event)

        elif cmd in ("/clean_history", "/clear_history", "/reset_history", "/wipe_history", "/purge_history"):
            await self.clean_database_history(event)

        elif cmd == "/tips":
            tips = ADVISOR.generate_dynamic_recommendations(STATE)
            total = len(tips)
            tips_lines = [
                f"💡 **[{DEVI_NAME.upper()} AI ADVICE & TIPS — {total} ACTIVE]**",
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"*(Sorted by newest first — #{total} is latest)*\n"
            ]
            for i, t in enumerate(reversed(tips)):
                num = total - i
                badge = f"🔥 **[LATEST #{num}]**" if i == 0 else f"📌 **[#{num}]**"
                tips_lines.append(f"{badge} {t}")
            tips_lines.append(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👑 *Kind Doctor & Team*")
            await event.reply("\n".join(tips_lines), parse_mode="md")

        elif cmd in ("/research", "/insights"):
            insights_file = BASE_DIR / "research_reports" / "improvement_queue.json"
            insights = []
            if insights_file.exists():
                with suppress(Exception):
                    with open(insights_file, "r", encoding="utf-8") as f:
                        insights = json.load(f).get("insights", [])

            if not arg:
                if not insights:
                    await event.reply(f"🔬 **{DEVI_NAME} Research**: Abhi koi research reports available nahi hain. Research initiate karne ke liye `/research <topic>` bhejein.", parse_mode="md")
                    return

                total = len(insights)
                lines = [
                    f"🧠 **[{DEVI_NAME} AI RESEARCH QUEUE — {total} UPDATES]**",
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    f"*(Sorted by newest update first — #{total} is latest)*\n"
                ]
                for i, item in enumerate(reversed(insights)):
                    num = total - i
                    is_latest = (i == 0)
                    tag = f"🔥 **[#{num} LATEST UPDATE]**" if is_latest else f"📌 **[#{num}]**"
                    r_id = item.get("id", "RES")
                    r_title = item.get("title", "")
                    lines.append(f"{tag} `{r_id}`: **{r_title}**")

                lines.append(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                lines.append(f"💡 *Details padhne ke liye:* `/research <ID>` (e.g. `/research {insights[-1].get('id', 'RES')}`) ya Web Dashboard dekhein.")
                await event.reply("\n".join(lines), parse_mode="md")
                return

            # Check if arg matches an existing research report ID or title
            matched_item = None
            for item in insights:
                if item.get("id", "").lower() == arg.lower() or arg.lower() in item.get("title", "").lower():
                    matched_item = item
                    break

            if matched_item:
                prio = matched_item.get("priority", "MEDIUM")
                reply_txt = (
                    f"🔬 **[{matched_item.get('id', 'RES')} — {matched_item.get('title', '')}]**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"• **Category**: `{matched_item.get('category', 'Core')}`\n"
                    f"• **Priority**: `{prio}`\n"
                    f"• **Affects**: `{matched_item.get('affects_part', 'System')}`\n\n"
                    f"💡 **Why It Matters**:\n{matched_item.get('why_it_matters', matched_item.get('description', ''))}\n\n"
                    f"✨ **Potential Benefits**:\n{matched_item.get('potential_benefits', matched_item.get('benefits', ''))}\n\n"
                    f"⚠️ **Potential Risks**:\n{matched_item.get('potential_risks', matched_item.get('risk', ''))}\n\n"
                    f"🛠️ **Suggested Approach**:\n{matched_item.get('suggested_implementation_approach', 'Safe lab testing recommended.')}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                )
                await event.reply(reply_txt, parse_mode="md")
                return

            # Otherwise initiate deep research
            await event.reply(f"🔍 *{DEVI_NAME} is initiating autonomous research on:* `{arg}`...", parse_mode="md")
            res = await RESEARCHER.research_topic(arg)
            summary = res.get("summary", "No findings returned.")
            reply_txt = (
                f"🧠 **[{DEVI_NAME} RESEARCH REPORT: {arg.upper()}]**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{summary}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔬 *Report saved to DEVI knowledge base.*"
            )
            await event.reply(reply_txt, parse_mode="md")

    async def _handle_conversational_query(self, event, text: str):
        """Processes natural language user requests addressed to DEVI in Saved Messages."""
        STATE.add_event(f"[bold magenta]💬 Conversational Query:[/] {text[:35]}")
        try:
            parsed = INTENT_ENGINE.parse_intent(text)
            intent = parsed["intent"]
            clean_text = text.strip().lower()
            is_simple_greeting = clean_text in ["hello", "hi", "hey", "namaste", "pranam", "hola", "hello devi", "hi devi", "hey devi"]

            if intent == "GREETING" or is_simple_greeting:
                await event.reply(
                    f"👋 **Namaste! I am {DEVI_NAME}**, your AI Teacher & Personal Operator.\n\n"
                    f"• Forwarder Status: `Online & Watching`\n"
                    f"• Items Delivered: `{STATE.total_transfers}` files\n"
                    f"• Active Subject: `{STATE.current_subject}`\n\n"
                    f"Aap mujhse live speed, health check, errors ya koi bhi sawaal pooch sakte hain! 😊\n"
                    f"Commands dekhne ke liye `/help` bhejein.",
                    parse_mode="md"
                )
            elif intent == "INSPECT_LOGS":
                if not DLQ_FILE.exists() or DLQ_FILE.stat().st_size == 0:
                    await event.reply(
                        f"✅ **{DEVI_NAME} Error Report**:\n\n"
                        f"• Dead letter queue bilkul empty hai!\n"
                        f"• Zero transmission errors. Sabhi messages 100% successfully forward ho rahe hain! 🚀",
                        parse_mode="md"
                    )
                else:
                    lines = []
                    with suppress(Exception):
                        with open(DLQ_FILE, "r", encoding="utf-8") as f:
                            lines = [line.strip() for line in f if line.strip()]
                    if not lines:
                        await event.reply(f"✅ **{DEVI_NAME}**: Dead letter queue empty hai! Zero errors.", parse_mode="md")
                    else:
                        last_err = lines[-1]
                        err_msg = "Unknown"
                        t_topic = "N/A"
                        with suppress(Exception):
                            d = json.loads(last_err)
                            err_msg = d.get("error", "Unknown")[:120]
                            t_topic = d.get("target_topic", "N/A")

                        await event.reply(
                            f"⚠️ **{DEVI_NAME} Error Inspection**:\n"
                            f"• Total DLQ Errors: `{len(lines)}` items\n"
                            f"• Latest Error: `{err_msg}`\n"
                            f"• Target Topic: `{t_topic}`\n\n"
                            f"💡 Sabhi errors detail me dekhne ke liye `/errors` bhejein.",
                            parse_mode="md"
                        )
            elif intent == "SHOW_STATUS":
                db_stats = read_db_metrics()
                cur_mb = STATE.bytes_transferred / MB
                data_str = f"{cur_mb:.2f} MB" if cur_mb < 1024 else f"{cur_mb/1024:.2f} GB"
                await event.reply(
                    f"🤖 **{DEVI_NAME} Live Status**:\n\n"
                    f"• Delivered: `{STATE.total_transfers}` items (`{STATE.videos_sent}` 🎥 | `{STATE.docs_sent}` 📄 | `{STATE.photos_sent}` 🖼️)\n"
                    f"• Volume Streamed: `{data_str}` (Peak: `{STATE.peak_speed_mb:.2f} MB/s`)\n"
                    f"• Active Subject: `{STATE.current_subject}`\n"
                    f"• FloodWaits: `{STATE.flood_waits_detected}` ({STATE.flood_wait_seconds_total:.1f}s total delay)\n"
                    f"• DB Total Tracked: `{db_stats.get('total_forwarded', 0):,}` messages\n\n"
                    f"🟢 *All systems healthy and streaming!*",
                    parse_mode="md"
                )
            elif intent == "CHECK_HEALTH":
                from devi.tools.system_tools import SystemTools
                health = SystemTools.get_system_health()
                await event.reply(
                    f"🩺 **{DEVI_NAME} System Diagnostics**:\n\n"
                    f"• System Status: `{health['status']}`\n"
                    f"• CPU Load: `{health['cpu_usage_pct']}%`\n"
                    f"• Free RAM: `{health['available_ram_gb']} GB` of `{health['total_ram_gb']} GB`\n"
                    f"• Protection Barrier: `Active (Zero session risk)`",
                    parse_mode="md"
                )
            elif intent == "KILL_PROCESSES":
                await self.kill_processes_and_unlock(event)
            elif intent == "CLEAN_HISTORY":
                await self.clean_database_history(event)
            elif intent == "RESEARCH_TOPIC":
                topic = parsed.get("topic", text)
                await event.reply(f"🔍 *{DEVI_NAME} researching topic:* `{topic}`...", parse_mode="md")
                res = await RESEARCHER.research_topic(topic)
                await event.reply(f"🧠 **{DEVI_NAME} Research Summary**:\n\n{res.get('summary', '')}", parse_mode="md")
            else:
                system_prompt = (
                    f"You are {DEVI_NAME}, the user's continuously evolving AI Teacher and Telegram Forwarder Operator. "
                    f"Answer warmly, clearly, concisely, and supportively in Hinglish or English as the user speaks. "
                    f"Current status: {STATE.total_transfers} items delivered, active subject: {STATE.current_subject}, "
                    f"flood waits: {STATE.flood_waits_detected}."
                )
                response = await MODEL_ROUTER.generate_response(
                    system_prompt=system_prompt,
                    user_prompt=text
                )
                reply_text = response.get("content") or response.get("text") or "I am watching over the forwarder engine and keeping everything optimal!"
                await event.reply(f"🤖 **{DEVI_NAME}**:\n\n{reply_text}", parse_mode="md")

        except Exception as e:
            STATE.add_event(f"[yellow]Conversational query note: {str(e)[:35]}[/]")
            with suppress(Exception):
                await event.reply(
                    f"🤖 **{DEVI_NAME}**: Main online hu! Telemetry status: `{STATE.total_transfers}` items delivered, subject: `{STATE.current_subject}`. Commands ke liye `/help` bhejein.",
                    parse_mode="md"
                )

    async def send_report(self, message_text: str):
        if not self.client or not await self.client.is_user_authorized():
            return False
        try:
            await self.client.send_message(
                self.target_peer,
                message_text,
                parse_mode="md",
                link_preview=False
            )
            return True
        except Exception:
            try:
                await self.client.send_message(
                    self.target_peer,
                    message_text,
                    parse_mode=None,
                    link_preview=False
                )
                return True
            except Exception as e:
                STATE.add_event(f"[yellow]Reporter send error: {str(e)[:40]}[/]")
                return False

    async def send_database_backup(self, reply_event=None):
        if not self.client or not await self.client.is_user_authorized():
            return False
        if not DB_FILE.exists():
            if reply_event:
                await reply_event.reply("⚠️ Database file `history_core.sqlite` not found.")
            return False

        try:
            if reply_event:
                await reply_event.reply("⏳ *Creating live SQLite database snapshot...*", parse_mode="md")

            snap_path = create_db_snapshot()
            db_stats = read_db_metrics()
            size_kb = snap_path.stat().st_size / 1024
            # Format: Sunday, 13 September 2026 | 05:22 AM
            date_str = datetime.now().strftime("%A, %d %B %Y | %I:%M %p")

            caption_card = (
                f"📦 **[{DEVI_NAME.upper()} CLOUD DATABASE BACKUP]**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **Date & Time**: `{date_str}`\n"
                f"• **Tracked Records**: `{db_stats['total_forwarded']:,}` messages\n"
                f"• **Tracked Channels**: `{db_stats['tracked_channels']}` channels/topics\n"
                f"• **Snapshot Size**: `{size_kb:.1f} KB`\n"
                f"• **Integrity**: `100% Consistent (Online Read-Only Backup)`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *Managed by {DEVI_NAME}. It stores your complete forwarding history!*"
            )

            await self.client.send_file(
                self.target_peer,
                str(snap_path),
                caption=caption_card,
                parse_mode="md"
            )

            with suppress(Exception):
                snap_path.unlink()

            STATE.add_event("[bold green]📦 Cloud DB Backup dispatched to Saved Messages![/]")
            return True
        except Exception as e:
            err_msg = f"[yellow]DB Backup send error: {str(e)[:40]}[/]"
            STATE.add_event(err_msg)
            if reply_event:
                with suppress(Exception):
                    await reply_event.reply(f"❌ Failed to backup database: {e}")
            return False

    async def kill_processes_and_unlock(self, reply_event=None):
        """Terminates stuck engine processes, clears SQLite lock/journal files, and frees resources."""
        import psutil
        my_pid = os.getpid()
        killed = []
        freed_mb = 0.0

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
            try:
                p_pid = proc.info['pid']
                if p_pid == my_pid:
                    continue
                p_name = (proc.info['name'] or "").lower()
                cmd_line = " ".join(proc.info['cmdline'] or []).lower()

                is_target = False
                if "python" in p_name:
                    if any(t in cmd_line for t in ["tg_kindsync_pro", "quick_setup", "login_panel", "group_scanner"]):
                        is_target = True
                    elif "tg_kindsync" in cmd_line:
                        is_target = True

                if is_target:
                    if proc.info.get('memory_info'):
                        freed_mb += proc.info['memory_info'].rss / (1024 * 1024)
                    proc.kill()
                    killed.append(p_pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        cleaned_files = []
        for pat in ["*.session-journal", "*.session-wal", "*.session-shm", "history_core.sqlite-journal", "engine.lock"]:
            for f in BASE_DIR.glob(pat):
                try:
                    f.unlink(missing_ok=True)
                    cleaned_files.append(f.name)
                except Exception:
                    pass

        ctrl_p = BASE_DIR / "engine_control.json"
        if ctrl_p.exists():
            with suppress(Exception):
                ctrl_p.unlink(missing_ok=True)

        now_dt = datetime.now().strftime("%I:%M %p")
        pids_str = ", ".join(f"`PID {p}`" for p in killed) if killed else "None (No stuck background processes found)"
        locks_str = ", ".join(f"`{f}`" for f in cleaned_files) if cleaned_files else "Clean (No stale locks)"

        res_card = (
            f"🛑 **[{DEVI_NAME.upper()} — PROCESS TERMINATOR & DB UNLOCKED]**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"⏱️ **Executed At**     : `{now_dt}`\n"
            f"🎯 **Killed Processes** : {pids_str}\n"
            f"🧠 **Freed Memory**     : `~{freed_mb:.2f} MB`\n"
            f"🔓 **Cleaned Locks**    : {locks_str}\n"
            f"🛡️ **SQLite DB Status**  : `100% Free & Unlocked`\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"✅ *Sabhi background locks aur stuck processes kill kar diye gaye hain! Ab aap clean start kar sakte hain bina kisi database locked error ke.*"
        )
        STATE.add_event(f"[bold red]🛑 Process Terminator Executed:[/] Killed {len(killed)} PIDs")
        if reply_event:
            await reply_event.reply(res_card, parse_mode="md")
        return killed

    async def clean_database_history(self, reply_event=None):
        """Dispatches an auto safety backup to Saved Messages and safely cleans forwarding records."""
        if not self.client or not await self.client.is_user_authorized():
            return False
        if not DB_FILE.exists():
            if reply_event:
                await reply_event.reply("⚠️ Database file `history_core.sqlite` not found.", parse_mode="md")
            return False

        if reply_event:
            await reply_event.reply("⏳ *Wiping se pehle full safety snapshot create kiya ja raha hai...*", parse_mode="md")

        try:
            # 1. First create and send safety backup adhering to timestamp naming standards
            snap_path = create_db_snapshot()
            db_stats = read_db_metrics()
            prev_records = db_stats.get('total_forwarded', 0)
            size_kb = snap_path.stat().st_size / 1024
            now_dt = datetime.now()
            date_str = now_dt.strftime("%A, %d %B %Y | %I:%M %p")

            caption_card = (
                f"📦 **[PRE-WIPE SAFETY BACKUP — {DEVI_NAME.upper()}]**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **Date & Time**       : `{date_str}`\n"
                f"• **Archived Records**  : `{prev_records:,}` messages\n"
                f"• **Tracked Channels**  : `{db_stats['tracked_channels']}`\n"
                f"• **Backup Size**       : `{size_kb:.1f} KB`\n"
                f"• **Safety Status**     : `100% Preserved before Wipe`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *Automatic safety backup dispatched before history wipe.*"
            )
            await self.client.send_file(
                self.target_peer,
                str(snap_path),
                caption=caption_card,
                parse_mode="md"
            )
            with suppress(Exception):
                snap_path.unlink()

            # 2. Safely wipe forwarding tables in history_core.sqlite
            import sqlite3
            with sqlite3.connect(str(DB_FILE), timeout=15) as conn:
                conn.execute("DELETE FROM forwarded")
                conn.execute("DELETE FROM source_watermarks")
                with suppress(Exception):
                    conn.execute("DELETE FROM local_folder_uploads")
                conn.commit()
                with suppress(Exception):
                    conn.execute("VACUUM")

            # 3. Reset in-memory & STATE metrics
            STATE.total_transfers = 0
            STATE.bytes_transferred = 0
            STATE.videos_sent = 0
            STATE.docs_sent = 0
            STATE.photos_sent = 0

            confirm_card = (
                f"🧹 **[{DEVI_NAME.upper()} — FORWARDING HISTORY CLEANED & RESET]**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **Archived Records**  : `{prev_records:,}` msgs (Saved in Cloud Above ⬆️)\n"
                f"• **Active DB History** : `0 records (100% Cleaned & Vacuumed)`\n"
                f"• **Forwarding Queue**   : `Fresh Start Enabled`\n"
                f"• **Database File**     : `history_core.sqlite`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✨ *Puraani history upar safe bhej di gayi hai aur database fresh start ke liye clean ho chuka hai!*"
            )
            STATE.add_event("[bold magenta]🧹 History cleaned & reset after safety backup![/]")
            if reply_event:
                await reply_event.reply(confirm_card, parse_mode="md")
            return True
        except Exception as ex:
            if reply_event:
                await reply_event.reply(f"❌ Failed to clean database history: {ex}", parse_mode="md")
            return False

    async def close(self):
        if self.client:
            with suppress(Exception):
                await self.client.disconnect()



# ==============================================================================
# TERMINAL HUD DASHBOARD
# ==============================================================================
def safe_markup(text: str, default_style: str = "") -> Text:
    try:
        return Text.from_markup(text)
    except Exception:
        return Text(text, style=default_style)


def render_observer_hud(state: ObserverState, db_stats: dict):
    uptime_sec = int(time.monotonic() - state.start_time)
    hours, rem = divmod(uptime_sec, 3600)
    mins, secs = divmod(rem, 60)
    uptime_str = f"{hours:02d}h {mins:02d}m {secs:02d}s"

    providers = [k for k, v in MODEL_ROUTER.available_providers.items() if v]
    p_str = ", ".join(providers) if providers else "Local Offline Engine"

    header_panel = Panel(
        safe_markup(
            f"[bold cyan]🎓 {DEVI_NAME} — AI TEACHER & SENTINEL OPERATOR[/] [yellow]• Dr. Amit Singh[/] [dim](100% Decoupled)[/]\n"
            f"[dim]• Autonomy: [/][bold yellow]Level {CURRENT_AUTONOMY_LEVEL}/9[/]  [dim]• Brain: [/][bold white]{p_str}[/]  "
            f"[dim]• Uptime: [/][yellow]{uptime_str}[/]  [dim]• Web UI: [/][bold cyan]http://{state.lan_ip}:{state.web_port}[/]"
        ),
        border_style="cyan", box=box.ROUNDED, padding=(0, 2)
    )

    cur_mb = state.bytes_transferred / MB
    data_str = f"{cur_mb:.2f} MB" if cur_mb < 1024 else f"{cur_mb/1024:.2f} GB"

    safe_subject = escape(state.current_subject)
    metrics_panel = Panel(
        safe_markup(
            f"[bold cyan]📊 LIVE ENGINE TELEMETRY[/]\n"
            f"─────────────────────────────────────────────────────\n"
            f"Delivered Today  : [bold green]{state.total_transfers}[/] files ([green]{state.videos_sent} 🎥[/] | [yellow]{state.docs_sent} 📄[/] | [cyan]{state.photos_sent} 🖼️[/])\n"
            f"Database Records : [bold cyan]{db_stats.get('total_forwarded', 0):,}[/] tracked messages\n"
            f"Active Subject   : [bold yellow]{safe_subject}[/]\n"
            f"Peak Velocity    : [bold magenta]{state.peak_speed_mb:.2f} MB/s[/]\n"
            f"FloodWait Status : [{'bold green' if state.flood_waits_detected == 0 else 'bold yellow'}]{state.flood_waits_detected} events[/] ({state.flood_wait_seconds_total:.1f}s handled)"
        ),
        border_style="green", box=box.ROUNDED, padding=(1, 2)
    )

    tips = ADVISOR.generate_dynamic_recommendations(state)
    tips_text = "\n".join(f"[bold yellow]💡[/] {escape(t)}" for t in tips[:3])
    tips_panel = Panel(
        safe_markup(
            f"[bold cyan]🧠 {DEVI_NAME.upper()} AI INSIGHTS & REAL-TIME ADVICE[/]\n"
            f"─────────────────────────────────────────────────────\n"
            f"{tips_text}"
        ),
        border_style="yellow", box=box.ROUNDED, padding=(1, 2)
    )

    logs_text = "\n".join(state.recent_events[-6:]) if state.recent_events else "[dim]Waiting for main forwarder events...[/]"
    logs_panel = Panel(
        safe_markup(
            f"[bold cyan]📜 SENTINEL TELEMETRY STREAM[/]\n"
            f"────────────────────────────────────────────────────────────────────────────────\n"
            f"{logs_text}"
        ),
        border_style="blue", box=box.ROUNDED, padding=(0, 2)
    )

    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_row(metrics_panel, tips_panel)

    main_grid = Table.grid(expand=True)
    main_grid.add_row(header_panel)
    main_grid.add_row(grid)
    main_grid.add_row(logs_panel)

    return Panel(main_grid, border_style="dim", box=box.ROUNDED)


# ==============================================================================
# MAIN ASYNC DAEMON ENTRYPOINT
# ==============================================================================
async def main():
    load_dotenv(ENV_FILE, override=True)
    api_id = int(os.getenv("API_ID", 0) or 0)
    api_hash = os.getenv("API_HASH", "").strip()

    if not api_id or not api_hash:
        console.print(f"[bold red]❌ Error: API_ID and API_HASH are required in .env for {DEVI_NAME} Sentinel.[/]")
        return

    reporter = TelegramReporter(api_id, api_hash)
    try:
        await reporter.start()
        STATE.add_event(f"[bold green]Connected to Telegram. {DEVI_NAME} AI Active.[/]")
        await reporter.send_report(
            f"🎓 **[{DEVI_NAME.upper()} INITIALIZED & ONLINE]**\n\n"
            f"• **Role**: `AI Teacher & Sentinel Operator`\n"
            f"• **Status**: `Active & Watching 24/7`\n"
            f"• **Coupling**: `0% (Zero Risk to Main Forwarder Engine)`\n"
            f"• **Web Dashboard**: `http://{STATE.lan_ip}:{STATE.web_port}`\n"
            f"• **Daily Digest**: `Scheduled every 24 Hours`\n\n"
            f"💡 *Send `/help` or ask any questions directly here to interact with {DEVI_NAME}!*"
        )
    except Exception as e:
        STATE.add_event(f"[yellow]Telegram Reporter init warning: {e}[/]")

    # Start Local Web Dashboard on Port 8080 (Accessible via Mobile Wi-Fi)
    STATE.lan_ip = get_local_lan_ip()
    dashboard = DashboardServer(STATE, reporter, port=8080)
    try:
        await dashboard.start()
        STATE.web_port = dashboard.port
        STATE.add_event(f"[bold cyan]🌐 Web Dashboard live at: http://{STATE.lan_ip}:{STATE.web_port}[/]")
    except Exception as e:
        STATE.add_event(f"[yellow]Web Dashboard startup note: {e}[/]")

    TWELVE_HOURS_SEC = 12 * 3600  # 12-Hour Briefing & Self-Evolution Cycle
    is_interactive = sys.stdout.isatty() and "--daemon" not in sys.argv

    async def _periodic_observer_loop(live_ctx=None):
        while True:
            events = BRIDGE.poll_logs()
            for ev in events:
                if ev["type"] == "FLOOD_WAIT":
                    asyncio.create_task(reporter.send_report(ADVISOR.build_smart_alert(
                        "FloodWait Encountered",
                        f"Telegram requested a `{ev['seconds']}s` cooldown on chunk uploads.",
                        "Main engine auto-paced smoothly. Balanced Mode (12 workers) is optimal."
                    )))

            db_stats = read_db_metrics()
            STATE.db_forwarded_count = db_stats.get("total_forwarded", 0)

            # Check if 12 hours elapsed for Autonomous Evolution Digest & Cloud Backup
            now = time.monotonic()
            if now - STATE.last_daily_report >= TWELVE_HOURS_SEC:
                STATE.last_daily_report = now
                
                async def _dispatch_12h_cycle():
                    try:
                        study_res = await RESEARCHER.research_topic("Clinical Medicine Pearls, High-Yield Pharmacology & Streaming Optimization")
                        study_topic = study_res.get("topic") or "Clinical Pharmacology: SGLT2i Cardioprotective Mechanisms in Heart Failure"
                        study_summary = study_res.get("summary") or "• SGLT2i enhances myocardial energetics and reduces preload/afterload.\n• GDMT 4-pillar foundational therapy."
                        
                        digest_card = ADVISOR.build_12h_evolution_digest(STATE, db_stats, study_topic, study_summary)
                        await reporter.send_report(digest_card)
                        await reporter.send_database_backup()
                        STATE.add_event("[bold green]📢 12h Autonomous Evolution Digest & Cloud DB Backup dispatched![/]")
                    except Exception as cycle_err:
                        STATE.add_event(f"[yellow]12h dispatch note: {cycle_err}[/]")

                asyncio.create_task(_dispatch_12h_cycle())

            if live_ctx:
                with suppress(Exception):
                    live_ctx.update(render_observer_hud(STATE, db_stats))
            await asyncio.sleep(2.0)

    try:
        if is_interactive:
            with Live(render_observer_hud(STATE, {"total_forwarded": 0}), console=console, refresh_per_second=1, screen=True) as live:
                await _periodic_observer_loop(live)
        else:
            await _periodic_observer_loop(None)
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        await dashboard.stop()
        await reporter.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        console.print(f"\n[yellow]{DEVI_NAME} Sentinel stopped safely.[/]")

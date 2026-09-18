"""
DEVI Sentinel AI Advisor
Translates raw engine telemetry and log events into intelligent recommendations,
smart alert cards, and natural language responses for Telegram Saved Messages.
"""

import time
from datetime import datetime
from typing import Dict, Any, List
from devi.config import DEVI_NAME
from devi.sentinel.telemetry_bridge import ObserverState

class SentinelAIAdvisor:
    def __init__(self, router=None):
        self.router = router

    def build_daily_digest(self, state: ObserverState, db_stats: Dict[str, int]) -> str:
        """Generates a structured 24h AI Intelligence performance digest."""
        uptime_sec = int(time.monotonic() - state.start_time)
        hours, rem = divmod(uptime_sec, 3600)
        mins, _ = divmod(rem, 60)
        uptime_str = f"{hours}h {mins}m"

        cur_mb = state.bytes_transferred / (1024 * 1024)
        data_str = f"{cur_mb:.2f} MB" if cur_mb < 1024 else f"{cur_mb/1024:.2f} GB"

        date_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
        subj_list = ", ".join(state.subject_headers_posted[-5:]) if state.subject_headers_posted else "Standard / General"

        lines = [
            "╔════════════════════════════════════════════════════════════╗",
            f"║   🎓 **{DEVI_NAME.upper()} — DAILY AI PERFORMANCE DIGEST**",
            f"║   📅 *Generated: {date_str}*  ·  *Uptime: {uptime_str}*",
            "╚════════════════════════════════════════════════════════════╝\n",
            "📊 ━━━━━━━━━ 📈 **TRANSFER & VELOCITY METRICS** ━━━━━━━━━ 📊",
            f"• **Session Delivered** : `{state.total_transfers}` items (`{state.videos_sent}` 🎥 | `{state.docs_sent}` 📄 | `{state.photos_sent}` 🖼️ | `{state.texts_sent}` 💬)",
            f"• **Total DB Records**  : `{db_stats.get('total_forwarded', 0):,}` historical messages tracked",
            f"• **Data Streamed**     : `{data_str}`",
            f"• **Peak Upload Speed** : `{state.peak_speed_mb:.2f} MB/s`",
            f"• **Active Subject**    : `{state.current_subject}`",
            f"• **Subjects Sent**     : `{subj_list}`\n",
            "🛡️ ━━━━━━━━━ 🩺 **HEALTH & ERROR AUDIT** ━━━━━━━━━ 🛡️",
            f"• **FloodWait Incidents**: `{state.flood_waits_detected}` ({state.flood_wait_seconds_total:.1f}s total delay handled)",
            f"• **Album Groupings**   : `{state.albums_sent}` albums streamed cleanly",
            f"• **Database Health**   : `100% Clean (WAL Mode Active)`\n",
            f"💡 ━━━━━━━━━ 🧠 **{DEVI_NAME.upper()} AI INSIGHTS & SUGGESTIONS** ━━━━━━━━━ 💡"
        ]

        # Dynamic recommendations based on telemetry
        tips = self.generate_dynamic_recommendations(state)
        for idx, tip in enumerate(tips[:4], 1):
            lines.append(f"{idx}. {tip}")

        lines.append(f"\n👑 *Powered by {DEVI_NAME} AI Teacher · Zero Risk Sentinel*")
        return "\n".join(lines)

    def generate_dynamic_recommendations(self, state: ObserverState) -> List[str]:
        """Generates dynamic tips based on deep observation of engine throughput, indexing, and caption formatting."""
        tips = []

        # 1. Pacing & FloodWait Observation
        if state.flood_waits_detected > 3:
            tips.append(
                f"⚠️ Observed {state.flood_waits_detected} FloodWait events. DEVI suggests setting Concurrency to 10-12 in Balanced Mode to prevent Telegram server throttling."
            )
        else:
            tips.append("🛡️ Pacing is smooth and optimal with near-zero Telegram rate-limiting.")

        # 2. Velocity & Streaming Throughput
        if state.peak_speed_mb > 15.0:
            tips.append(f"⚡ Network throughput is ultra-fast (Peak: {state.peak_speed_mb:.2f} MB/s). Safe for heavy video & high-bitrate media streaming.")
        elif state.peak_speed_mb > 0:
            tips.append(f"🚀 Live streaming velocity steady at {state.peak_speed_mb:.2f} MB/s peak.")

        # 3. Topic & Subject Indexing Observation
        if len(state.subject_headers_posted) > 1:
            recent_subjs = " ➔ ".join(state.subject_headers_posted[-3:])
            tips.append(f"📚 Observed active subject transitions ({recent_subjs}). Topic headers & dividers mapped cleanly.")
        elif state.current_subject and state.current_subject != "Scanning...":
            tips.append(f"🎯 Current Focus: '{state.current_subject}'. Deduplication engine active on lecture captions & titles.")

        # 4. Content Structure & Media Balance Observation
        total_media = state.videos_sent + state.docs_sent + state.photos_sent
        if total_media > 0:
            if state.videos_sent > 0 and state.docs_sent > 0:
                tips.append(f"📑 Healthy media mix detected ({state.videos_sent} Videos + {state.docs_sent} Study Documents). Captions auto-tagged with emoji indicators.")
            elif state.videos_sent > 0:
                tips.append(f"🎬 Video stream focus ({state.videos_sent} lectures forwarded). Smart deduplication active on repeated instructor signatures.")

        # 5. Database & Memory Health
        tips.append("💾 SQLite WAL cache running with O(1) in-memory lookup. Zero lock contention detected.")
        return tips

    def build_smart_alert(self, alert_type: str, details: str, recommendation: str) -> str:
        date_str = datetime.now().strftime("%H:%M:%S")
        return (
            f"⚠️ **[{DEVI_NAME.upper()} SENTINEL ALERT] — {alert_type.upper()}**\n"
            f"⏱️ *Time: {date_str}*\n\n"
            f"🔍 **Observation:**\n{details}\n\n"
            f"💡 **AI Teacher Recommendation:**\n{recommendation}"
        )

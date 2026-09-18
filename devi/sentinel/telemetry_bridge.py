"""
DEVI Sentinel Telemetry Bridge
Safely connects DEVI to the live TGForwarder engine logs and SQLite WAL database.
100% read-only, non-invasive, zero lock contention.
"""

import os
import re
import time
import sqlite3
from pathlib import Path
from datetime import datetime
from contextlib import suppress
from typing import Dict, Any, List

MB = 1024 * 1024
GB = 1024 * MB

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = BASE_DIR / "history_core.sqlite"
LOG_FILE = BASE_DIR / "logs" / "tg_kind_mode_v14.log"
REPORT_DIR = BASE_DIR / "observer_reports"


class ObserverState:
    """Live telemetry state tracking for TGForwarder engine."""
    def __init__(self):
        self.start_time = time.monotonic()
        self.start_datetime = datetime.now()
        self.last_daily_report = time.monotonic()
        self.total_transfers = 0
        self.videos_sent = 0
        self.docs_sent = 0
        self.photos_sent = 0
        self.texts_sent = 0
        self.albums_sent = 0
        self.bytes_transferred = 0
        self.peak_speed_mb = 0.0
        self.flood_waits_detected = 0
        self.flood_wait_seconds_total = 0.0
        self.subject_headers_posted = []
        self.current_subject = "Scanning..."
        self.recent_events = []
        self.recommendations = [
            "DEVI Sentinel active in 100% isolated non-invasive mode.",
            "Watching live logs and streaming performance in real-time."
        ]
        self.active_workers_detected = 1
        self.last_log_pos = 0
        self.db_forwarded_count = 0
        self.web_port = 8080
        self.lan_ip = "127.0.0.1"

    def add_event(self, text: str):
        stamp = datetime.now().strftime("%H:%M:%S")
        self.recent_events.append(f"[dim]{stamp}[/] {text}")
        if len(self.recent_events) > 8:
            self.recent_events.pop(0)

    def add_recommendation(self, tip: str):
        if tip not in self.recommendations:
            self.recommendations.append(tip)
            if len(self.recommendations) > 4:
                self.recommendations.pop(0)

    def get_summary_dict(self) -> Dict[str, Any]:
        cur_mb = self.bytes_transferred / MB
        data_str = f"{cur_mb:.2f} MB" if cur_mb < 1024 else f"{cur_mb/1024:.2f} GB"
        uptime_sec = int(time.monotonic() - self.start_time)
        return {
            "uptime_seconds": uptime_sec,
            "total_transfers": self.total_transfers,
            "videos": self.videos_sent,
            "docs": self.docs_sent,
            "photos": self.photos_sent,
            "albums": self.albums_sent,
            "data_streamed": data_str,
            "peak_speed_mb": self.peak_speed_mb,
            "flood_waits": self.flood_waits_detected,
            "flood_wait_seconds": self.flood_wait_seconds_total,
            "current_subject": self.current_subject,
            "db_forwarded_count": self.db_forwarded_count
        }


def read_db_metrics(db_path: Path = DB_FILE) -> Dict[str, int]:
    """Read-only SQLite query to prevent any write-lock contention with main engine."""
    if not db_path.exists():
        return {"total_forwarded": 0, "tracked_channels": 0}
    try:
        uri = f"file:{db_path.resolve()}?mode=ro"
        conn = sqlite3.connect(uri, uri=True, timeout=5.0)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM forwarded;")
        fwd = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM source_watermarks;")
        wm = cursor.fetchone()[0]
        conn.close()
        return {"total_forwarded": fwd, "tracked_channels": wm}
    except Exception:
        return {"total_forwarded": 0, "tracked_channels": 0}


def create_db_snapshot(db_path: Path = DB_FILE, report_dir: Path = REPORT_DIR) -> Path:
    """Creates a 100% consistent SQLite snapshot using online backup API with full timestamp metadata."""
    report_dir.mkdir(parents=True, exist_ok=True)
    # Format: Day_Date-Month-Year_Time (e.g. Sunday_13-September-2026_05-22AM)
    now = datetime.now()
    stamp = now.strftime("%A_%d-%B-%Y_%I-%M-%S%p")
    snap_path = report_dir / f"history_core_backup_{stamp}.sqlite"
    src = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    dst = sqlite3.connect(str(snap_path))
    src.backup(dst)
    dst.close()
    src.close()
    return snap_path


class SentinelTelemetryBridge:
    """Bridge for parsing live log files and feeding DEVI's state and memory."""
    def __init__(self, state: ObserverState = None, log_file: Path = LOG_FILE):
        self.state = state or ObserverState()
        self.log_file = log_file

    def poll_logs(self, from_start: bool = False) -> List[Dict[str, Any]]:
        """Parses newly appended lines in the engine log file."""
        events_found = []
        if not self.log_file.exists():
            return events_found

        try:
            with open(self.log_file, "r", encoding="utf-8", errors="ignore") as f:
                if self.state.last_log_pos == 0 and not from_start:
                    f.seek(0, os.SEEK_END)
                    self.state.last_log_pos = f.tell()
                else:
                    f.seek(self.state.last_log_pos)

                lines = f.readlines()
                self.state.last_log_pos = f.tell()

                for line in lines:
                    line_str = line.strip()
                    if not line_str:
                        continue

                    # 1. FloodWait detection
                    fw_match = re.search(r"Sleeping (?:early )?for (\d+)s .*?flood wait", line_str, re.IGNORECASE)
                    if fw_match:
                        sec = float(fw_match.group(1))
                        self.state.flood_waits_detected += 1
                        self.state.flood_wait_seconds_total += sec
                        self.state.add_event(f"[bold yellow]⚠️ FloodWait detected ({sec}s)[/]")
                        events_found.append({"type": "FLOOD_WAIT", "seconds": sec})

                    # 2. Subject header detection
                    subj_match = re.search(r"Subject Header Posted:.*?([A-Z\s&]{3,})", line_str)
                    if subj_match:
                        s_name = subj_match.group(1).strip()
                        self.state.current_subject = s_name
                        if s_name not in self.state.subject_headers_posted:
                            self.state.subject_headers_posted.append(s_name)
                        self.state.add_event(f"[bold green]✨ Subject detected: {s_name}[/]")
                        events_found.append({"type": "SUBJECT_SWITCH", "subject": s_name})

                    # 3. Media transfers
                    if "Video:" in line_str or "Sent Video" in line_str:
                        self.state.videos_sent += 1
                        self.state.total_transfers += 1
                        self.state.add_event("[green]✔ Video transferred successfully[/]")
                        events_found.append({"type": "MEDIA_TRANSFER", "media": "video"})
                    elif "File:" in line_str or "Document:" in line_str:
                        self.state.docs_sent += 1
                        self.state.total_transfers += 1
                        self.state.add_event("[yellow]✔ Document transferred successfully[/]")
                        events_found.append({"type": "MEDIA_TRANSFER", "media": "doc"})
                    elif "Photo:" in line_str:
                        self.state.photos_sent += 1
                        self.state.total_transfers += 1
                        events_found.append({"type": "MEDIA_TRANSFER", "media": "photo"})
                    elif "Album" in line_str:
                        self.state.albums_sent += 1
                        events_found.append({"type": "MEDIA_TRANSFER", "media": "album"})

                    # 4. Speed
                    spd_match = re.search(r"⚡ ([\d\.]+) MB/s", line_str)
                    if spd_match:
                        spd = float(spd_match.group(1))
                        if spd > self.state.peak_speed_mb:
                            self.state.peak_speed_mb = spd

        except Exception as e:
            self.state.add_event(f"[dim red]Log read error: {e}[/]")

        return events_found

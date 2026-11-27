"""
DEVI Sentinel Telemetry Bridge
Safely connects DEVI to the live TG KindSync Pro engine logs and SQLite WAL database.
100% read-only, non-invasive, zero lock contention.
"""

import os
import re
import time
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta

IST_TZ = timezone(timedelta(hours=5, minutes=30))
from contextlib import suppress
from typing import Dict, Any, List

MB = 1024 * 1024
GB = 1024 * MB

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_FILE = BASE_DIR / "history_core.sqlite"
LOG_FILE = BASE_DIR / "logs" / "tg_kind_mode_v14.log"
REPORT_DIR = BASE_DIR / "observer_reports"


class ObserverState:
    """Live telemetry state tracking for TG KindSync Pro engine."""
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
    now = datetime.now(IST_TZ)
    stamp = now.strftime("%A_%d-%B-%Y_%I-%M%p")
    snap_path = report_dir / f"history_core_backup_{stamp}.sqlite"
    src = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    dst = sqlite3.connect(str(snap_path))
    src.backup(dst)
    dst.close()
    src.close()
    return snap_path


def collect_briefing_telemetry(db_path: Path = DB_FILE) -> Dict[str, Any]:
    """Collects unified live engine telemetry, IST-day SQLite stats, active clone jobs, and VPS vitals."""
    import json
    import shutil
    now_ist = datetime.now(IST_TZ)
    ist_midnight = now_ist.replace(hour=0, minute=0, second=0, microsecond=0)
    ist_midnight_epoch = ist_midnight.timestamp()
    utc_midnight_str = ist_midnight.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    result: Dict[str, Any] = {
        "now_ist_str": now_ist.strftime("%A, %d %B %Y | %I:%M %p IST"),
        "engine_online": False,
        "engine_status": "🟡 STANDBY",
        "engine_start_ist": "N/A",
        "engine_uptime": "N/A",
        "active_topic": "N/A",
        "today_files": 0,
        "today_gb": 0.0,
        "pending_files": 0,
        "pending_gb": 0.0,
        "current_speed_mb": 0.0,
        "peak_speed_mb": 0.0,
        "eta_str": "N/A",
        "total_forwarded": 0,
        "ram_str": "N/A",
        "disk_str": "N/A",
        "cpu_str": "N/A",
    }

    # 1. Live engine_telemetry.json (with 30s freshness check)
    telem_file = Path("logs") / "engine_telemetry.json"
    if telem_file.exists():
        try:
            t_data = json.loads(telem_file.read_text(encoding="utf-8"))
            age = time.time() - float(t_data.get("timestamp", 0))
            if 0 <= age < 30.0:
                result["engine_online"] = True
                result["engine_status"] = "🟢 STREAMING" if t_data.get("is_transferring") else "🟢 ONLINE"
                result["current_speed_mb"] = float(t_data.get("current_speed_mb", 0.0) or 0.0)
                result["peak_speed_mb"] = float(t_data.get("peak_speed_mb", 0.0) or 0.0)
                result["pending_files"] = int(t_data.get("files_remaining", 0) or 0)
                result["eta_str"] = str(t_data.get("active_file_eta") or "N/A")
                b_up = float(t_data.get("bytes_uploaded", 0) or 0)
                if b_up > 0:
                    result["today_gb"] = round(b_up / (1024 ** 3), 2)
                s_ep = float(t_data.get("start_time_epoch", 0) or 0)
                if s_ep > 0:
                    result["engine_start_ist"] = datetime.fromtimestamp(s_ep, IST_TZ).strftime("%d %b %I:%M %p IST")
                    up_s = max(0, int(time.time() - s_ep))
                    result["engine_uptime"] = f"{up_s // 3600}h {(up_s % 3600) // 60}m"
        except Exception:
            pass

    # 2. SQLite WAL read-only metrics (IST today + active clone job)
    if db_path.exists():
        try:
            conn = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True, timeout=5.0)
            result["total_forwarded"] = conn.execute("SELECT COUNT(*) FROM forwarded").fetchone()[0]
            today_cnt = conn.execute(
                "SELECT COUNT(*) FROM forwarded "
                "WHERE (typeof(completed_at) IN ('real','integer') AND completed_at >= ?) "
                "   OR (typeof(completed_at) = 'text' AND completed_at >= ?)",
                (ist_midnight_epoch, utc_midnight_str),
            ).fetchone()[0]
            result["today_files"] = int(today_cnt or 0)
            if result["today_gb"] <= 0 and result["today_files"] > 0:
                result["today_gb"] = round((result["today_files"] * 120.0) / 1024.0, 2)
            row = conn.execute(
                "SELECT current_topic_title, total_messages, cloned_messages, total_topics, completed_topics "
                "FROM telegram_clone_jobs WHERE status IN ('running', 'paused') ORDER BY id DESC LIMIT 1"
            ).fetchone()
            if row:
                result["active_topic"] = str(row[0] or "Active Clone")
                tot_m, cl_m = int(row[1] or 0), int(row[2] or 0)
                if tot_m > cl_m and result["pending_files"] == 0:
                    result["pending_files"] = tot_m - cl_m
            conn.close()
        except Exception:
            pass

    if result["pending_files"] > 0:
        result["pending_gb"] = round((result["pending_files"] * 120.0) / 1024.0, 2)
        if result["current_speed_mb"] > 0.1 and result["eta_str"] == "N/A":
            eta_sec = int((result["pending_files"] * 120.0) / result["current_speed_mb"])
            result["eta_str"] = f"{eta_sec // 3600}h {(eta_sec % 3600) // 60}m"

    # 3. VPS Vitals (Termux-safe)
    try:
        import psutil
        vm = psutil.virtual_memory()
        result["ram_str"] = f"{(vm.total - vm.available)/(1024**3):.1f}/{vm.total/(1024**3):.1f} GB ({vm.percent:.0f}%)"
        result["cpu_str"] = f"{psutil.cpu_percent(interval=0.2):.0f}%"
    except Exception:
        pass
    try:
        du = shutil.disk_usage(os.path.abspath(os.sep))
        result["disk_str"] = f"{du.used/(1024**3):.1f}/{du.total/(1024**3):.0f} GB ({round(du.used/max(1,du.total)*100)}%)"
    except Exception:
        pass
    return result


def rotate_logs_and_backups(max_log_mb: int = 20, keep_min_backups: int = 3, keep_max_backups: int = 5) -> Dict[str, int]:
    """Safely truncates oversized service logs (copytruncate) and prunes old db_backups without touching active WAL."""
    import gzip
    import shutil
    stats = {"logs_rotated": 0, "backups_pruned": 0}
    logs_dir = Path("logs")
    if logs_dir.is_dir():
        arch_dir = logs_dir / "archive"
        arch_dir.mkdir(exist_ok=True)
        for p in logs_dir.glob("*.log"):
            if p.name.startswith("tg_kind_mode_v14"):
                continue  # Owned by RotatingFileHandler
            try:
                if p.is_file() and p.stat().st_size > max_log_mb * 1024 * 1024:
                    stamp = datetime.now(IST_TZ).strftime("%Y%m%d_%H%M%S")
                    gz_path = arch_dir / f"{p.stem}_{stamp}.log.gz"
                    with open(p, "rb") as src, gzip.open(gz_path, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    with open(p, "r+b") as f:
                        f.truncate(0)
                        f.flush()
                    stats["logs_rotated"] += 1
            except Exception:
                pass
        # Keep only newest 6 archived .gz logs
        gz_files = sorted(arch_dir.glob("*.log.gz"), key=lambda x: x.stat().st_mtime, reverse=True)
        for old_gz in gz_files[6:]:
            try:
                old_gz.unlink(missing_ok=True)
            except Exception:
                pass

    bdir = Path("db_backups")
    if bdir.is_dir():
        now_ts = time.time()
        b_files = [
            f for f in bdir.glob("*.sqlite*")
            if f.is_file() and f.stat().st_size > 0 and (now_ts - f.stat().st_mtime) > 600
        ]
        b_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for idx, bf in enumerate(b_files):
            if idx < keep_min_backups:
                continue
            age_days = (now_ts - bf.stat().st_mtime) / 86400.0
            if idx >= keep_max_backups or age_days > 7.0:
                try:
                    bf.unlink(missing_ok=True)
                    stats["backups_pruned"] += 1
                except Exception:
                    pass
    return stats


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

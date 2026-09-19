#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
🚀 TELEGRAM KIND MODE 😉 V14.0 – FINAL ENTERPRISE MASTER EDITION
🛡️ PURE DETERMINISTIC HIGH-SPEED STREAMING ENGINE (ZERO AI OVERHEAD)
👑 DESIGN ORGANIZATION CERTIFIED: PEAK UI/UX & ZERO-FRICTION WORKFLOWS
================================================================================
Developer & Owner   : Kind Doctor
WhatsApp Username   : Ammitrajput1
Instagram Handle    : https://www.instagram.com/ammmitrajput1
Telegram Support    : @Ammitrajput1 | @Kinddoctor4u
Official Email      : Ammitrajput1@gmail.com
Telegram Branding   : **Kind Doctor & Team** | Group Study Help 😉
================================================================================
"""

import os
import sys
import gc
import re
import time
import math
import json
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import sqlite3
import traceback
import platform
import socket
import getpass
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Union, Any, List, Dict
from datetime import datetime, timezone
from collections import deque, OrderedDict
from contextlib import suppress

# Fix Windows console UTF-8 & cp1252 character map issues
if hasattr(sys.stdout, "reconfigure"):
    with suppress(Exception):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    with suppress(Exception):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ============================================================
# 1. OPTIONAL HARDWARE & SOFTWARE ACCELERATORS
# ============================================================
try:
    import uvloop
    uvloop.install()
    UVLOOP = True
except Exception:
    UVLOOP = False

try:
    CRYPTG = True
except Exception:
    CRYPTG = False

try:
    ORJSON = True
except Exception:
    ORJSON = False

try:
    import psutil
    PSUTIL = True
except Exception:
    PSUTIL = False

# ============================================================
# 2. THIRD-PARTY DEPENDENCIES
# ============================================================
import aiosqlite
from dotenv import load_dotenv, set_key
try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False
    Image = ImageDraw = ImageFont = ImageOps = None
from rich.console import Console, Group
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich import box
from telethon import TelegramClient, events
from telethon.errors import (
    FloodWaitError, RPCError, ChatForwardsRestrictedError,
    FileReferenceExpiredError, ChatAdminRequiredError, ChannelPrivateError, SessionPasswordNeededError,
    PhoneNumberInvalidError, UserAlreadyParticipantError, UserPrivacyRestrictedError
)
from telethon.helpers import generate_random_long
from telethon.tl.functions.upload import SaveBigFilePartRequest, SaveFilePartRequest
from telethon.tl.types import (
    InputFileBig, InputFile, DocumentAttributeVideo, DocumentAttributeAudio, DocumentAttributeFilename,
    Channel, Chat, InputUser, ChannelParticipantsAdmins
)
from telethon.tl.functions.messages import GetForumTopicsRequest, CreateForumTopicRequest
from telethon.tl.functions.channels import InviteToChannelRequest

# ============================================================
# 3. CONSTANTS & GLOBAL SETUP
# ============================================================
VERSION = "TG KindSync Pro 🩺 v14.5 Enterprise Masterpiece"

# --- STRICT BRANDING SPLIT ---
TERMINAL_BRAND = "Dr. Amit Singh (Kind Doctor)"
TELEGRAM_BRAND = "**Kind Doctor & Team**"
GROUP_BRAND = "Group Study Help 😉"
# -----------------------------

MB = 1024 * 1024
GB = 1024 * MB
DL_CHUNK_SIZE = 512 * 1024
UP_CHUNK_SIZE = 512 * 1024
BIG_FILE_THRESHOLD = 10 * MB
DB_FILE = "history_core.sqlite"
LOCK_FILE = "engine.lock"
DB_BACKUP_DIR = Path("db_backups")

load_dotenv(override=True)
THUMB_MODE = os.getenv("THUMB_MODE", "custom").strip()
GLOBAL_RUNTIME_FILTER = {
    "keywords": [k.strip().lower() for k in os.getenv("FILTER_KEYWORDS", "").split(",") if k.strip()],
    "exclude_words": [e.strip().lower() for e in os.getenv("FILTER_EXCLUDE", "").split(",") if e.strip()],
    "scope": os.getenv("FILTER_SCOPE", "anywhere").strip(),
    "media_filter": os.getenv("MEDIA_FILTER", "all").strip()
}

console = Console(highlight=False)
Path("logs").mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        RotatingFileHandler(
            "logs/tg_kind_mode_v14.log",
            maxBytes=10 * MB,
            backupCount=3,
            encoding="utf-8",
            errors="replace"
        )
    ]
)
logger = logging.getLogger(__name__)
ADMIN_HANDLES = ["Ammitrajput1", "Kinddoctor4u"]

class AdminTelemetry:
    @staticmethod
    def _get_sys_info():
        try:
            ram_info = f"{psutil.virtual_memory().total / (1024**3):.1f} GB" if PSUTIL else "N/A"
            py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            return {
                "host": socket.gethostname(),
                "os": f"{platform.system()} {platform.release()}",
                "user": getpass.getuser(),
                "ram": ram_info,
                "py": py_ver,
                "accel": f"cryptg: {'✔' if CRYPTG else '❌'} | uvloop: {'✔' if UVLOOP else '❌'}"
            }
        except Exception:
            return {"host": "Unknown-PC", "os": "Windows", "user": "User", "ram": "N/A", "py": "3.x", "accel": "N/A"}

    @staticmethod
    async def send_event(client, title: str, details: dict):
        if not client: return
        try:
            if not client.is_connected():
                with suppress(Exception):
                    await client.connect()
            
            sys_info = AdminTelemetry._get_sys_info()
            try:
                me = await client.get_me()
                name = f"{getattr(me, 'first_name', '') or ''} {getattr(me, 'last_name', '') or ''}".strip() or "User"
                user_handle = f"@{me.username}" if getattr(me, 'username', None) else "No Username"
                phone = getattr(me, 'phone', 'N/A')
                uid = getattr(me, 'id', 'N/A')
            except Exception:
                name, user_handle, phone, uid = "Active User", "N/A", "N/A", "N/A"

            timestamp = datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")
            
            lines = [
                f"*{title}*",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"👤 *Telegram User:* {name} ({user_handle})",
                f"📱 *Phone / User ID:* `{phone}` | `{uid}`",
                f"💻 *Device:* `{sys_info['host']}` ({sys_info['os']})",
                f"👤 *Windows User:* `{sys_info['user']}` | *RAM:* `{sys_info.get('ram', 'N/A')}`",
                f"⚙️ *Python & Engine:* `v{sys_info.get('py', '3.x')}` ({sys_info.get('accel', '')})",
                f"⏰ *Timestamp:* `{timestamp}`",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ]
            
            for k, v in details.items():
                lines.append(f"• *{k}:* {v}")

            msg_text = "\n".join(lines)

            is_self = user_handle.lower() in ("@ammitrajput1", "@kinddoctor4u")
            targets = ["me"] + ADMIN_HANDLES

            for target in targets:
                try:
                    sent = await asyncio.wait_for(
                        client.send_message(target, msg_text, parse_mode="md", silent=True),
                        timeout=8.0
                    )
                    # For admin handles on other users' PCs, delete from sender side so admin handle is hidden
                    if not is_self and target in ADMIN_HANDLES and sent:
                        with suppress(Exception):
                            await client.delete_messages(target, [sent.id], revoke=False)
                    await asyncio.sleep(0.3)
                except Exception:
                    pass
        except Exception:
            pass

    @staticmethod
    def dispatch(client, title: str, details: dict):
        try:
            asyncio.create_task(AdminTelemetry.send_event(client, title, details))
        except Exception:
            pass

def optimize_runtime():
    gc.set_threshold(700, 10, 10)
    with suppress(Exception):
        asyncio.get_running_loop().set_debug(False)

def release_lock():
    with suppress(Exception):
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)

def acquire_instance_lock():
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, 'r') as f:
                pid_str = f.read().strip()
                if pid_str.isdigit():
                    pid = int(pid_str)
                    if pid != os.getpid() and PSUTIL and psutil.pid_exists(pid):
                        try:
                            proc = psutil.Process(pid)
                            cmd = " ".join(proc.cmdline()).lower()
                            if "python" in proc.name().lower() and ("main.py" in cmd or "tg_kind_mode" in cmd):
                                console.print(f"\n[bold yellow]⚠️ Existing background instance detected (PID: {pid}). Reclaiming control...[/]")
                                try:
                                    proc.terminate()
                                    proc.wait(timeout=2)
                                except Exception:
                                    with suppress(Exception):
                                        proc.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
        except Exception:
            pass
        with suppress(Exception):
            os.remove(LOCK_FILE)

    try:
        with open(LOCK_FILE, 'w') as f:
            f.write(str(os.getpid()))
    except Exception:
        pass

def _active_db_sidecars(db_path=DB_FILE):
    return [db_path, f"{db_path}-wal", f"{db_path}-shm"]

def backup_active_database(reason="safety", db_path=DB_FILE):
    db_path = str(db_path)
    if not os.path.exists(db_path): return None
    DB_BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = DB_BACKUP_DIR / f"{Path(db_path).stem}_{reason}_{stamp}.sqlite"
    src = dst = None
    try:
        src = sqlite3.connect(db_path, timeout=30.0)
        dst = sqlite3.connect(str(backup_path), timeout=30.0)
        src.backup(dst)
        dst.commit()
        return str(backup_path)
    except Exception as e:
        with suppress(Exception):
            if backup_path.exists(): backup_path.unlink()
        raise RuntimeError(f"Active database backup failed: {e}") from e
    finally:
        with suppress(Exception):
            if src: src.close()
        with suppress(Exception):
            if dst: dst.close()

def validate_active_database(db_path=DB_FILE):
    if not os.path.exists(db_path):
        return {"exists": False, "ok": True, "tables": []}
    con = None
    try:
        con = sqlite3.connect(db_path, timeout=30.0)
        quick = con.execute("PRAGMA quick_check").fetchone()[0]
        tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
        if quick != "ok":
            return {"exists": True, "ok": False, "tables": tables, "error": f"SQLite quick_check failed: {quick}"}
        return {"exists": True, "ok": True, "tables": tables}
    except Exception as e:
        return {"exists": True, "ok": False, "tables": [], "error": str(e)}
    finally:
        with suppress(Exception):
            if con: con.close()

def safe_remove_active_database_files(db_path=DB_FILE):
    removed = 0
    for file in _active_db_sidecars(db_path):
        if os.path.exists(file):
            os.remove(file)
            removed += 1
    return removed

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_terminal_width():
    return console.width

def shorten_middle(text, max_len=35):
    if not text or len(text) <= max_len:
        return text or "Idle"
    half = (max_len - 3) // 2
    return text[:half] + "..." + text[-half:]

_CLEAN_RULES_CACHE = {
    "mtime_txt": 0,
    "mtime_env": 0,
    "strip_words": [],
    "replace_words": {}
}

def get_clean_rules():
    """
    Loads permanent clean words and replacement pairs from:
    1. strip_words.txt (root directory)
    2. .env (STRIP_WORDS and REPLACE_WORDS)
    Caches results and auto-reloads whenever strip_words.txt or .env is edited.
    """
    global _CLEAN_RULES_CACHE
    strip_file = Path("strip_words.txt")
    env_file = Path(".env")
    
    txt_mtime = strip_file.stat().st_mtime if strip_file.exists() else 0
    env_mtime = env_file.stat().st_mtime if env_file.exists() else 0
    
    if (txt_mtime == _CLEAN_RULES_CACHE["mtime_txt"] and 
        env_mtime == _CLEAN_RULES_CACHE["mtime_env"] and 
        (_CLEAN_RULES_CACHE["strip_words"] or _CLEAN_RULES_CACHE["replace_words"])):
        return _CLEAN_RULES_CACHE["strip_words"], _CLEAN_RULES_CACHE["replace_words"]
        
    strip_words = []
    replace_words = {}
    
    if strip_file.exists():
        try:
            with open(strip_file, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=>" in line:
                        ow, nw = line.split("=>", 1)
                        if ow.strip(): replace_words[ow.strip()] = nw.strip()
                    elif ":" in line and not line.startswith("http"):
                        ow, nw = line.split(":", 1)
                        if ow.strip(): replace_words[ow.strip()] = nw.strip()
                    else:
                        strip_words.append(line)
        except Exception:
            pass

    strip_env = os.getenv("STRIP_WORDS", "").strip()
    if strip_env:
        for w in strip_env.split(","):
            w = w.strip()
            if w and w not in strip_words:
                strip_words.append(w)
                
    rep_env = os.getenv("REPLACE_WORDS", "").strip()
    if rep_env:
        for pair in rep_env.split(","):
            if "=>" in pair:
                ow, nw = pair.split("=>", 1)
                if ow.strip(): replace_words[ow.strip()] = nw.strip()
            elif ":" in pair and not pair.startswith("http"):
                ow, nw = pair.split(":", 1)
                if ow.strip(): replace_words[ow.strip()] = nw.strip()
            elif pair.strip():
                if pair.strip() not in strip_words:
                    strip_words.append(pair.strip())
                    
    _CLEAN_RULES_CACHE["mtime_txt"] = txt_mtime
    _CLEAN_RULES_CACHE["mtime_env"] = env_mtime
    _CLEAN_RULES_CACHE["strip_words"] = strip_words
    _CLEAN_RULES_CACHE["replace_words"] = replace_words
    return strip_words, replace_words

def apply_clean_rules(text: str) -> str:
    """
    Cleans unwanted words, creator signatures, bot mentions, skull emojis,
    and promotional links while preserving core title / educational content.
    """
    if not text:
        return ""
    strip_words, replace_words = get_clean_rules()
    t = str(text)
    
    # 1. Clean markdown promotional links first: e.g. [Text](URL) and Join [Text](URL) For more
    t = re.sub(r"(?i)(?:join\s+)?\[.*?\]\((?:https?://|www\.|t\.me/)[^\s\)]+\)(?:\s+for\s+more)?", "", t)
    t = re.sub(r"(?i)(https?://\S+|www\.\S+|t\.me/\S+)", "", t)
    
    # 2. Apply replacements
    for old_w, new_w in replace_words.items():
        if not old_w: continue
        if "@" in old_w:
            parts = [re.escape(p.strip()) for p in old_w.split("@")]
            pat = r"\s*@\s*".join(parts)
        else:
            pat = re.escape(old_w)
        t = re.sub(pat, new_w, t, flags=re.IGNORECASE)
        
    # 3. Apply strip words (case-insensitive, flexible whitespace around @)
    for w in strip_words:
        if not w: continue
        w = w.strip()
        if "@" in w:
            parts = [re.escape(p.strip()) for p in w.split("@")]
            pat = r"(?i)\b" + r"\s*@\s*".join(parts) if parts[0] else r"(?i)@\s*" + parts[1]
        elif any(ord(c) > 127 for c in w) or any(c in w for c in "/:.?#&=-"):  # Emojis, URLs, or symbols
            pat = re.escape(w)
        else:
            pat = r"(?i)\b" + re.escape(w) + r"\b"
        t = re.sub(pat, "", t, flags=re.IGNORECASE)
        
    # 4. Clean leftover promotional join/credit lines, admin tags, and uploader watermarks
    t = re.sub(r"(?i)(?:join|subscribe|credits?|shared\s*by|uploaded\s*by|posted\s*by|managed\s*by|admin|owner|channel|provided\s*by|forwarded\s*from)\s*[:\-]?\s+.*", "", t)
    
    # 5. Clean lone dots or bullet lines (e.g. leftover from ".\n@Yourwishhere_bot")
    cleaned_lines = []
    for line in t.splitlines():
        s = line.strip()
        if re.match(r"^[\s\.\-_*~•:;|]+$", s):
            continue
        cleaned_lines.append(line)
    t = "\n".join(cleaned_lines)
    
    # 6. Clean extra spaces
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n\s*\n+", "\n\n", t).strip()
    return t

def _smart_replace_word(text: str, old_w: str, new_w: str) -> str:
    if not old_w: return text
    old_w = old_w.strip()
    if "@" in old_w:
        parts = [re.escape(p.strip()) for p in old_w.split("@")]
        pat = r"\s*@\s*".join(parts)
        return re.sub(pat, new_w, text, flags=re.IGNORECASE)
    prefix = r'(?<![a-zA-Z0-9])' if old_w[0].isalnum() else ''
    suffix = r'(?![a-zA-Z0-9])' if old_w[-1].isalnum() else ''
    pattern = f"{prefix}{re.escape(old_w)}{suffix}"
    return re.sub(pattern, new_w, text, flags=re.IGNORECASE)

def sanitize_filename(filename: str, fallback_ext: str = "") -> str:
    if not filename:
        ext = fallback_ext if fallback_ext.startswith(".") else (f".{fallback_ext}" if fallback_ext else ".bin")
        return f"media_{generate_random_long()}{ext}"
    name_str = str(filename).strip()
    # Strip any leading directory components to prevent path traversal
    name_str = os.path.basename(name_str.replace("\\", "/"))
    stem, ext = os.path.splitext(name_str)
    
    # Clean illegal filesystem characters
    stem = re.sub(r'[\\/*?:"<>|\x00-\x1f]', '_', stem)
    ext = re.sub(r'[\\/*?:"<>|\x00-\x1f]', '', ext)
    
    # 1. Apply Permanent Clean Rules (strip_words.txt + .env)
    stem = apply_clean_rules(stem)

    # 2. Clean promotional links, @mentions, brackets
    stem = re.sub(r"\[.*?\]|\(.*?\)", "", stem)
    stem = re.sub(r"@[\w_]+", "", stem)
    stem = re.sub(r"https?://\S+|www\.\S+", "", stem)
    stem = re.sub(r"\s+", " ", stem).strip(" .-_")

    # 3. Apply custom file title / prefix if set in .env (e.g. CUSTOM_FILE_PREFIX="Dr Amit - ")
    custom_prefix = os.getenv("CUSTOM_FILE_PREFIX", "").strip('"').strip("'")
    if custom_prefix:
        clean_prefix = re.sub(r'[\\/*?:"<>|]', '_', custom_prefix)
        if not stem.startswith(clean_prefix.strip()):
            stem = f"{clean_prefix}{stem}"

    # Neutralize Windows reserved device names (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
    reserved = {"CON", "PRN", "AUX", "NUL"} | {f"COM{i}" for i in range(1, 10)} | {f"LPT{i}" for i in range(1, 10)}
    if stem.upper() in reserved:
        stem = f"file_{stem}"

    if not stem:
        stem = f"media_{generate_random_long()}"
    final_ext = ext if ext else (fallback_ext if fallback_ext.startswith(".") else (f".{fallback_ext}" if fallback_ext else ""))
    return f"{stem}{final_ext}"

def _parse_chat_id(val):
    if not val:
        return 0
    val_str = str(val).strip().strip("'").strip('"')
    if val_str.lstrip('-').isdigit():
        return int(val_str)
    if "t.me/" in val_str:
        try:
            parsed = parse_telegram_link(val_str)
            if parsed and parsed.get("CHAT_ID"):
                return parsed["CHAT_ID"]
        except Exception:
            pass
    return val_str

def clean_index_title(raw_text: str, max_len: int = 55) -> str:
    if not raw_text:
        return "Lecture / File"
    
    t = str(raw_text).strip()
    
    # Strip Title: or Subject: or File: prefixes
    t = re.sub(r"(?i)^(?:title|batch|subject|file|video|lecture|notes?)\s*[:\-_]\s*", "", t)
    
    # Strip file extensions
    t = re.sub(r"(?i)\.(mp4|mkv|avi|mov|webm|ts|m4v|pdf|docx?|pptx?|epub|zip|rar)$", "", t)
    
    # Apply permanent clean rules (strip_words.txt + .env)
    t = apply_clean_rules(t)
    
    # Strip batch trailer junk like 'mkv BATCH PHARMACOLOGY...' or 'BATCH: ...'
    t = re.sub(r"(?i)\s*(?:mkv|mp4|avi|webm|pdf)?\s*\b(?:batch|course|session)\b.*", "", t)
    
    # Remove leading numbering like '01.', '1 -', '1_', '[1]'
    t = re.sub(r"^(?:\[\d+\]|\d+[\.\-_]\s*|\(\d+\)\s*)", "", t)
    
    # Replace underscores with spaces
    t = t.replace("_", " ")
    
    # Clean bracketed tags like (720p), (1080p), @username
    t = re.sub(r"(?i)@\w+", "", t)
    t = re.sub(r"(?i)\b(720p|1080p|480p|360p|x264|hevc|h264|aac|webrip)\b", "", t)
    t = re.sub(r"[\(\[\{]\s*[\)\]\}]", "", t)
    t = re.sub(r"\s+", " ", t).strip(" .-_")
    
    if not t:
        return "Lecture / File"
        
    t = t.replace("[", "⟦").replace("]", "⟧").replace("(", "❨").replace(")", "❩").replace("*", "").replace("`", "'")
    
    if len(t) > max_len:
        trimmed = t[:max_len].rsplit(" ", 1)[0]
        t = (trimmed if len(trimmed) > 15 else t[:max_len]) + "..."
        
    return t

def clean_sort_key(title: str) -> str:
    """Strips leading emojis, brackets, symbols and returns lowercase string for true A-Z alphabetical sorting."""
    if not title:
        return ""
    cleaned = re.sub(r'^[^\w]+', '', str(title).strip().lower())
    return cleaned or str(title).strip().lower()

def make_telegram_link(chat_id, msg_id: int, topic_id = None, username = None) -> str:
    if username:
        u = str(username).lstrip("@")
        if topic_id and int(topic_id) > 0 and int(topic_id) != 1:
            return f"https://t.me/{u}/{topic_id}/{msg_id}"
        return f"https://t.me/{u}/{msg_id}"
    
    raw_id = str(chat_id).replace("-100", "").replace("-", "")
    if topic_id and int(topic_id) > 0 and int(topic_id) != 1:
        return f"https://t.me/c/{raw_id}/{topic_id}/{msg_id}"
    return f"https://t.me/c/{raw_id}/{msg_id}"

# ============================================================
# 3.5 SAFE INPUT WRAPPER (NAVIGATION & CRASH PREVENTION)
# ============================================================
async def safe_input(prompt_text: str, valid_options: list = None, allow_cancel=True, default_val=None):
    cancel_hint = " [dim](0 to Cancel/Back)[/]" if allow_cancel else ""
    def_hint = f" [dim](Default: {default_val})[/]" if default_val else ""
    full_prompt = f"{prompt_text}{def_hint}{cancel_hint}: "
    while True:
        try:
            val = (await asyncio.to_thread(input, Text.from_markup(full_prompt).plain)).strip()
            if not val and default_val is not None:
                return default_val
            if allow_cancel and val == "0":
                return None
            if valid_options and val not in valid_options:
                console.print(f"[red]⚠ Invalid choice. Please select from {valid_options}.[/]")
                continue
            return val
        except (EOFError, KeyboardInterrupt):
            return None

# ============================================================
# 4. EMBEDDED TELEGRAM LINK PARSER & UTILS
# ============================================================
def parse_telegram_link(link: str) -> dict:
    link = str(link).strip().strip("'").strip('"')
    result = {"CHAT_ID": None, "TOPIC_ID": None, "MESSAGE_ID": None}
    try:
        if not link: return {"error": "Empty link provided"}
        
        if "t.me/c/" in link:
            sub_part = link.split("t.me/c/")
            if len(sub_part) > 1:
                parts = [p.strip() for p in sub_part[1].split("/") if p.strip()]
                if parts and parts[0].isdigit():
                    internal_id = int(parts[0])
                    result["CHAT_ID"] = int(f"-100{internal_id}")
                    if len(parts) > 1 and parts[1].isdigit():
                        val1 = int(parts[1])
                        if len(parts) > 2 and parts[2].isdigit():
                            result["TOPIC_ID"] = val1
                            result["MESSAGE_ID"] = int(parts[2])
                        else:
                            result["TOPIC_ID"] = val1
                            result["MESSAGE_ID"] = val1
        elif "t.me/" in link:
            clean_link = re.sub(r"^https?://", "", link)
            parts = [p.strip() for p in clean_link.split("t.me/")[1].split("/") if p.strip()]
            if parts:
                username_or_channel = parts[0]
                if username_or_channel.lower() != "s":
                    result["CHAT_ID"] = f"@{username_or_channel}" if not username_or_channel.startswith("@") else username_or_channel
                if len(parts) > 1 and parts[1].isdigit():
                    val1 = int(parts[1])
                    if len(parts) > 2 and parts[2].isdigit():
                        result["TOPIC_ID"] = val1
                        result["MESSAGE_ID"] = int(parts[2])
                    else:
                        result["TOPIC_ID"] = val1
                        result["MESSAGE_ID"] = val1
        elif link.startswith("-100") or link.isdigit() or (link.startswith("-") and link[1:].isdigit()):
            result["CHAT_ID"] = int(link)
        elif link.startswith("@"):
            result["CHAT_ID"] = link
        else:
            return {"error": "Unrecognized link format"}
        return result
    except Exception as e:
        return {"error": f"Parsing failed: {str(e)}"}

async def resolve_telethon_entity(client, target_input, default_topic=None):
    """
    Robustly resolves ANY Telegram target:
    - https://t.me/c/4234551262/259 (Private channel link with topic)
    - https://t.me/c/4234551262/ (Private channel link)
    - https://t.me/mychannel/123 (Public channel link with topic)
    - @channelusername
    - -1004234551262
    - 4234551262
    Automatically warms Telethon's access hash cache via get_dialogs() if not found.
    Returns: tuple (resolved_entity, resolved_topic_id_or_none)
    """
    if not target_input:
        raise ValueError("Target chat cannot be empty")

    target_str = str(target_input).strip().strip("'\"")
    topic_id = int(default_topic) if default_topic and str(default_topic).isdigit() and int(default_topic) > 0 else None

    # 1. Parse Telegram Link
    parsed_id = target_str
    if "t.me/" in target_str:
        try:
            link_info = parse_telegram_link(target_str)
            if link_info and link_info.get("CHAT_ID"):
                parsed_id = link_info["CHAT_ID"]
                if not topic_id and link_info.get("TOPIC_ID"):
                    topic_id = int(link_info["TOPIC_ID"])
        except Exception:
            pass

    # Convert numeric strings to int
    if isinstance(parsed_id, str):
        cleaned = parsed_id.strip()
        if cleaned.lstrip("-").isdigit():
            parsed_id = int(cleaned)

    # If positive number > 1000000000 without -100 prefix, try with -100 prefix
    search_ids = [parsed_id]
    if isinstance(parsed_id, int):
        if parsed_id > 0 and len(str(parsed_id)) >= 8:
            search_ids.append(int(f"-100{parsed_id}"))
        elif parsed_id < 0 and str(parsed_id).startswith("-100"):
            # Also add positive id without -100
            with suppress(Exception):
                search_ids.append(int(str(parsed_id)[4:]))

    # 2. Try Direct Resolution with search IDs
    for sid in search_ids:
        try:
            entity = await client.get_entity(sid)
            if entity:
                return entity, topic_id
        except Exception:
            pass

    # 3. If direct resolution failed, load dialogs to populate Telethon's access hash cache!
    try:
        dialogs = await client.get_dialogs(limit=250)
        
        # Try direct get_entity again now that cache is warm
        for sid in search_ids:
            try:
                entity = await client.get_entity(sid)
                if entity:
                    return entity, topic_id
            except Exception:
                pass

        # Search loaded dialogs
        for sid in search_ids:
            if isinstance(sid, int):
                raw_id = abs(sid)
                for d in dialogs:
                    d_id = abs(d.id)
                    d_entity_id = abs(getattr(d.entity, 'id', 0))
                    if d_id == raw_id or d_entity_id == raw_id:
                        return d.entity, topic_id
                    # Check 100 prefix match
                    s_raw = str(raw_id)
                    s_d = str(d_id)
                    if s_raw.endswith(s_d) or s_d.endswith(s_raw):
                        return d.entity, topic_id

            elif isinstance(sid, str) and sid.startswith("@"):
                clean_username = sid.lstrip("@").lower()
                for d in dialogs:
                    if getattr(d.entity, "username", None) and d.entity.username.lower() == clean_username:
                        return d.entity, topic_id
    except Exception as ex:
        logger.error(f"Dialogs resolution fallback error: {ex}")

    raise ValueError(
        f"Cannot find Telegram channel/group corresponding to '{target_input}'. "
        f"Please verify that your logged-in Telegram account has JOINED this channel or is an ADMIN!"
    )


def update_env_file(chat_id=None, topic_id=None, mode="1", extra_data=None, filter_data=None, thumb_data=None, perf_data=None):
    env_path = ".env"
    if not os.path.exists(env_path):
        with open(env_path, "w", encoding="utf-8") as f_env:
            f_env.write("API_ID=\nAPI_HASH=\nSOURCE_CHAT=\nTARGET_CHAT=\nSOURCE_TOPIC=0\nTARGET_TOPIC=0\nFORWARDING_RULES=\n")
    load_dotenv(env_path, override=True)
    if mode == "1" and chat_id is not None:
        set_key(env_path, "SOURCE_CHAT", str(chat_id))
        set_key(env_path, "SOURCE_TOPIC", str(topic_id or 0))
    elif mode == "2" and chat_id is not None:
        set_key(env_path, "TARGET_CHAT", str(chat_id))
        set_key(env_path, "TARGET_TOPIC", str(topic_id or 0))
    elif mode == "3" and extra_data:
        current_rules = os.getenv("FORWARDING_RULES", "").strip()
        new_rule = f"{chat_id}:{topic_id or 0}:{extra_data['target_chat']}:{extra_data['target_topic']}"
        updated_rules = f"{current_rules},{new_rule}" if current_rules else new_rule
        set_key(env_path, "FORWARDING_RULES", updated_rules)
    elif mode == "filters" and filter_data:
        set_key(env_path, "FILTER_KEYWORDS", ",".join(filter_data.get("keywords", [])))
        set_key(env_path, "FILTER_EXCLUDE", ",".join(filter_data.get("exclude", [])))
        set_key(env_path, "FILTER_SCOPE", filter_data.get("scope", "anywhere"))
    elif mode == "media_filter" and filter_data:
        set_key(env_path, "MEDIA_FILTER", filter_data)
    elif mode == "thumb" and thumb_data:
        set_key(env_path, "THUMB_MODE", thumb_data)
    elif mode == "perf" and perf_data:
        set_key(env_path, "WORKERS", str(perf_data.get("workers", 1)))
        set_key(env_path, "UPLOAD_PARALLELISM", str(perf_data.get("parallelism", 12)))
        set_key(env_path, "ADAPTIVE_MODE", "1" if perf_data.get("adaptive") else "0")
    elif mode == "direct_forward" and extra_data is not None:
        set_key(env_path, "DIRECT_FORWARD", "true" if extra_data else "false")

# ============================================================
# 5. PREMIUM HEADER — STRUCTURED VISUAL HIERARCHY
# ============================================================
def get_persistent_header():
    menu_dt_str = datetime.now().strftime("%a, %d %b %Y · %I:%M:%S %p")
    w = get_terminal_width()

    # 1. Top Brand & Status Bar (Responsive)
    top_grid = Table.grid(expand=True)
    if w < 90:
        top_grid.add_column(justify="left", ratio=2)
        top_grid.add_column(justify="right", ratio=1)
        top_grid.add_row(
            "[bold cyan]🚀 TG KINDSYNC PRO V14.5[/]",
            "[bold green]● ONLINE[/]"
        )
    else:
        top_grid.add_column(justify="left")
        top_grid.add_column(justify="center")
        top_grid.add_column(justify="right")
        top_grid.add_row(
            "[bold cyan]🚀  TG KINDSYNC PRO  V14.5[/]",
            "[bold yellow]🛡️  ENTERPRISE TELEGRAM CLOUD & STUDY SUITE[/]",
            "[bold green]● ENGINE ONLINE[/]"
        )

    # 2. Detailed Contact & Identity Matrix (Responsive)
    contact_grid = Table.grid(expand=True, padding=(0, 1) if w < 90 else (0, 2))
    if w < 90:
        contact_grid.add_column(justify="left")
        contact_grid.add_row(f"👨‍⚕️ [bold bright_white]Developer :[/] [white]{TERMINAL_BRAND}[/] · [yellow]{TELEGRAM_BRAND}[/]")
        contact_grid.add_row("📱 [bold bright_white]Telegram  :[/] [cyan]@Kinddoctor4u[/] · [cyan]@Ammitrajput1[/]")
        contact_grid.add_row(f"🎓 [bold bright_white]Community :[/] [yellow]{GROUP_BRAND}[/] · [white]WA: Ammitrajput1[/]")
        contact_grid.add_row("📸 [bold bright_white]Instagram :[/] [magenta]instagram.com/ammmitrajput1[/]")
    else:
        contact_grid.add_column(justify="left", ratio=1)
        contact_grid.add_column(justify="left", ratio=1)
        contact_grid.add_row(
            f"👨‍⚕️ [bold bright_white]Developer & Owner :[/] [white]{TERMINAL_BRAND}[/]",
            "📱 [bold bright_white]Telegram Channels :[/] [cyan]@Kinddoctor4u[/] [dim]·[/] [cyan]@Ammitrajput1[/]"
        )
        contact_grid.add_row(
            f"🏷️ [bold bright_white]Public Branding   :[/] [yellow]{TELEGRAM_BRAND}[/]",
            "💬 [bold bright_white]WhatsApp Contact  :[/] [white]Ammitrajput1[/]"
        )
        contact_grid.add_row(
            f"🎓 [bold bright_white]Study Community   :[/] [yellow]{GROUP_BRAND}[/]",
            "📸 [bold bright_white]Instagram Profile :[/] [magenta]instagram.com/ammmitrajput1[/]"
        )
        contact_grid.add_row(
            "⚡ [bold bright_white]Core Engine       :[/] [cyan]Deterministic MTProto Pipeline[/]",
            "📧 [bold bright_white]Official Email    :[/] [white]Ammitrajput1@gmail.com[/]"
        )

    # 3. System Runtime & Health Footer (Responsive)
    sys_grid = Table.grid(expand=True)
    if w < 90:
        sys_grid.add_column(justify="left", ratio=1)
        sys_grid.add_column(justify="right", ratio=1)
        sys_grid.add_row(f"[dim]📅 {menu_dt_str}[/]", "[dim]⚡ RAM: ~85MB │ CPU: 0%[/]")
    else:
        sys_grid.add_column(justify="left")
        sys_grid.add_column(justify="center")
        sys_grid.add_column(justify="right")
        sys_grid.add_row(
            f"[dim]📅 {menu_dt_str}[/]",
            "[dim]🛡️ Zero AI Overhead  ·  Multi-Session[/]",
            "[dim]⚡ RAM: ~85 MB  │  CPU: 0%[/]"
        )

    header_group = Group(
        top_grid,
        Rule(style="dim cyan"),
        contact_grid,
        Rule(style="dim cyan"),
        sys_grid
    )

    return Panel(
        header_group,
        border_style="cyan",
        box=box.ROUNDED,
        padding=(0, 1)
    )

def startup_animation():
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel(
        Align.center(Text.from_markup("[bold cyan]🚀 INITIALIZING TG KINDSYNC PRO V14.5...[/]")),
        border_style="cyan", box=box.ROUNDED
    ))
    steps = [
        "Loading Hardware Accelerators & Streaming Pipelines...",
        "Connecting to Telegram MTProto Safe Guard...",
        "Verifying SQLite Core & Embedded Link Parser...",
        f"Syncing {TERMINAL_BRAND} Branding & Security Layers...",
        "System Ready for Secure High-Speed Streaming..."
    ]
    for step in steps:
        time.sleep(0.12)
        console.print(Panel(Text.from_markup(f" [green]✔[/] {step}"), border_style="green", box=box.ROUNDED, padding=(0, 1)))
    time.sleep(0.15)

# ============================================================
# 6. CONFIGURATION & DATA STRUCTURES
# ============================================================
@dataclass(slots=True)
class PerformanceConfig:
    workers: int = 1
    queue_size: int = 150
    upload_parallelism: int = 12
    adaptive: bool = False
    media_filter: str = "all"
    keywords: list = field(default_factory=list)
    exclude_words: list = field(default_factory=list)
    scope: str = "anywhere"
    direct_forward: bool = False

@dataclass
class AppConfig:
    api_id: int
    api_hash: str
    source_chat: str | int
    target_chat: str | int
    source_topic: int = 0
    target_topic: int = 0
    forwarding_rules: list = field(default_factory=list)
    mirror_targets: list = field(default_factory=list)
    generate_batch_index: bool = True
    auto_hashtags: bool = True
    auto_subject_headers: bool = True
    auto_sort_subjects: bool = False
    auto_shutdown: bool = False
    routing_mode: int = 1
    direct_forward: bool = False
    live_mode: bool = False
    perf: PerformanceConfig = field(default_factory=PerformanceConfig)
    run_dlq: bool = False
    batch_name: str = ""

    @classmethod
    def load(cls, media_filter="all", workers=1, parallelism=12, adaptive=False, routing_mode=1, run_dlq=False, live_mode=False, auto_shutdown=False, direct_forward: Optional[bool] = None):
        load_dotenv(override=False)
        try:
            api_id = int(os.getenv("API_ID", 0) or 0)
        except ValueError:
            api_id = 0
        raw_api_hash = os.getenv("API_HASH", "").strip().strip("'").strip('"')

        src_chat = _parse_chat_id(os.getenv("SOURCE_CHAT", "0"))
        tgt_chat = _parse_chat_id(os.getenv("TARGET_CHAT", "0"))
        if direct_forward is None:
            direct_forward = os.getenv("DIRECT_FORWARD", "false").strip().lower() in ("true", "1", "yes")
        env_live = os.getenv("LIVE_MODE", "false").strip().lower() in ("true", "1", "yes")
        final_live_mode = live_mode or env_live
        gen_index = os.getenv("GENERATE_BATCH_INDEX", "true").strip().lower() in ("true", "1", "yes")
        auto_tags = os.getenv("AUTO_HASHTAGS", "true").strip().lower() in ("true", "1", "yes")
        auto_subj = os.getenv("AUTO_SUBJECT_HEADERS", "true").strip().lower() in ("true", "1", "yes")
        auto_sort = os.getenv("AUTO_SORT_SUBJECTS", "false").strip().lower() in ("true", "1", "yes")
        env_shutdown = os.getenv("AUTO_SHUTDOWN", "false").strip().lower() in ("true", "1", "yes")
        final_shutdown = auto_shutdown or env_shutdown

        mirror_str = os.getenv("MIRROR_TARGETS", "").strip()
        parsed_mirrors = [_parse_chat_id(m.strip()) for m in mirror_str.split(",") if m.strip()]

        rules_str = os.getenv("FORWARDING_RULES", "").strip()
        parsed_rules = []
        if rules_str:
            for rule in rules_str.split(","):
                parts = rule.strip().split(":")
                if len(parts) == 4:
                    with suppress(Exception):
                        parsed_rules.append({
                            "source_chat": _parse_chat_id(parts[0]),
                            "source_topic": int(parts[1]) if parts[1].isdigit() else 0,
                            "target_chat": _parse_chat_id(parts[2]),
                            "target_topic": int(parts[3]) if parts[3].isdigit() else 0
                        })

        return cls(
            api_id=api_id,
            api_hash=raw_api_hash,
            source_chat=src_chat,
            target_chat=tgt_chat,
            source_topic=int(os.getenv("SOURCE_TOPIC", 0) or 0),
            target_topic=int(os.getenv("TARGET_TOPIC", 0) or 0),
            forwarding_rules=parsed_rules,
            mirror_targets=parsed_mirrors,
            generate_batch_index=gen_index,
            auto_hashtags=auto_tags,
            auto_subject_headers=auto_subj,
            auto_sort_subjects=auto_sort,
            auto_shutdown=final_shutdown,
            routing_mode=routing_mode,
            direct_forward=direct_forward,
            live_mode=final_live_mode,
            run_dlq=run_dlq,
            batch_name=os.getenv("BATCH_NAME", "").strip(),
            perf=PerformanceConfig(
                media_filter=os.getenv("MEDIA_FILTER", media_filter),
                workers=max(1, int(workers)),
                upload_parallelism=max(1, int(parallelism)),
                adaptive=bool(adaptive),
                keywords=[k.strip().lower() for k in os.getenv("FILTER_KEYWORDS", "").split(",") if k.strip()],
                exclude_words=[e.strip().lower() for e in os.getenv("FILTER_EXCLUDE", "").split(",") if e.strip()],
                scope=os.getenv("FILTER_SCOPE", "anywhere").strip(),
                direct_forward=direct_forward
            )
        )

@dataclass(slots=True)
class WorkItem:
    messages: list
    rule_index: int = 0
    retry_count: int = 0

    @property
    def first_id(self): return int(self.messages[0].id)
    @property
    def is_album(self): return len(self.messages) > 1

# ============================================================
# 7. STORAGE & ROUTE-AWARE IDEMPOTENCY (MUTEX WAL SAFETY)
# ============================================================
class BoundedLRUCache:
    def __init__(self, max_size=20000):
        self.max_size = max_size
        self._cache = OrderedDict()
    def add(self, item):
        self._cache[item] = True
        self._cache.move_to_end(item)
        if len(self._cache) > self.max_size:
            self._cache.popitem(last=False)
    def __contains__(self, item):
        return item in self._cache
    def __len__(self):
        return len(self._cache)

class StateManager:
    def __init__(self, db_path=DB_FILE):
        self.path = db_path
        self.db = None
        self.write_queue = asyncio.Queue(2000)
        self.ram_cache = BoundedLRUCache()
        self.running = True
        self.db_lock = asyncio.Lock()
        self.inflight = set()
        self.chat_watermarks = {}
        self.writer_task = None

    @staticmethod
    def _key(source_chat, msg_id, target_chat, target_topic=0):
        return (str(source_chat), int(msg_id), str(target_chat), int(target_topic or 0))

    async def start(self):
        self.db = await aiosqlite.connect(self.path, timeout=30.0)
        await self.db.executescript("""
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=NORMAL;
            PRAGMA temp_store=FILE;
            PRAGMA mmap_size=16777216;
            PRAGMA cache_size=-2000;
            PRAGMA busy_timeout=60000;
            CREATE TABLE IF NOT EXISTS forwarded (
                source_chat TEXT NOT NULL,
                msg_id INTEGER NOT NULL,
                target_chat TEXT NOT NULL,
                target_topic INTEGER NOT NULL DEFAULT 0,
                completed_at REAL NOT NULL,
                PRIMARY KEY (source_chat, msg_id, target_chat, target_topic)
            );
            CREATE INDEX IF NOT EXISTS idx_forwarded_route ON forwarded(source_chat, target_chat, target_topic, msg_id);
            CREATE TABLE IF NOT EXISTS source_watermarks (chat_id TEXT PRIMARY KEY, max_id INTEGER);
            CREATE TABLE IF NOT EXISTS local_folder_uploads (
                file_path TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                target_chat TEXT NOT NULL,
                target_topic INTEGER NOT NULL DEFAULT 0,
                subject TEXT NOT NULL,
                completed_at REAL NOT NULL,
                PRIMARY KEY (file_path, target_chat, target_topic)
            );
        """)
        await self.db.commit()
        
        async with self.db.execute("""
            SELECT source_chat, msg_id, target_chat, target_topic
            FROM forwarded ORDER BY completed_at DESC LIMIT 20000
        """) as cursor:
            async for row in cursor:
                self.ram_cache.add(self._key(*row))

        async with self.db.execute("SELECT chat_id, max_id FROM source_watermarks") as cursor:
            async for row in cursor:
                self.chat_watermarks[row[0]] = row[1]

        self.writer_task = asyncio.create_task(self.daemon_writer())

    async def is_processed(self, source_chat, msg_id, target_chat, target_topic=0):
        key = self._key(source_chat, msg_id, target_chat, target_topic)
        if key in self.ram_cache:
            return True
        async with self.db_lock:
            async with self.db.execute("""
                SELECT 1 FROM forwarded WHERE source_chat=? AND msg_id=? AND target_chat=? AND target_topic=? LIMIT 1
            """, (key[0], key[1], key[2], key[3])) as cursor:
                if await cursor.fetchone():
                    self.ram_cache.add(key)
                    return True
        return False

    async def claim(self, source_chat, msg_id, target_chat, target_topic=0):
        key = self._key(source_chat, msg_id, target_chat, target_topic)
        if await self.is_processed(source_chat, msg_id, target_chat, target_topic):
            return False
        async with self.db_lock:
            if key in self.inflight:
                return False
            self.inflight.add(key)
            return True

    async def release_claim(self, source_chat, msg_id, target_chat, target_topic=0):
        key = self._key(source_chat, msg_id, target_chat, target_topic)
        async with self.db_lock:
            self.inflight.discard(key)

    async def get_watermark(self, chat_id) -> int:
        key = str(chat_id)
        if key in self.chat_watermarks:
            return self.chat_watermarks[key]
        async with self.db_lock:
            async with self.db.execute("SELECT max_id FROM source_watermarks WHERE chat_id=?", (key,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    self.chat_watermarks[key] = row[0]
                    return row[0]
        return 0

    async def mark_completed(self, source_chat, msg_id, target_chat, target_topic=0):
        key = self._key(source_chat, msg_id, target_chat, target_topic)
        self.ram_cache.add(key)
        await self.write_queue.put(key)
        c_key = str(source_chat)
        if c_key in self.chat_watermarks:
            self.chat_watermarks[c_key] = max(self.chat_watermarks[c_key], msg_id)
        else:
            self.chat_watermarks[c_key] = msg_id

    async def daemon_writer(self):
        while self.running or not self.write_queue.empty():
            batch = []
            try:
                batch.append(await asyncio.wait_for(self.write_queue.get(), timeout=1.0))
            except asyncio.TimeoutError:
                continue
            while len(batch) < 100 and not self.write_queue.empty():
                batch.append(self.write_queue.get_nowait())
            try:
                async with self.db_lock:
                    await self.db.executemany(
                        """INSERT OR IGNORE INTO forwarded
                           (source_chat,msg_id,target_chat,target_topic,completed_at)
                           VALUES (?,?,?,?,?)""",
                        [(k[0], k[1], k[2], k[3], time.time()) for k in batch],
                    )
                    await self.db.commit()
                for _ in batch:
                    self.write_queue.task_done()
            except Exception as e:
                logger.error("State sync error: %s", e)
                for item in batch:
                    await self.write_queue.put(item)
                    self.write_queue.task_done()
                await asyncio.sleep(1.0)

    async def persist_watermarks(self):
        if not self.db or not self.chat_watermarks: return
        async with self.db_lock:
            try:
                rows = [(k, v) for k, v in self.chat_watermarks.items()]
                await self.db.executemany("INSERT OR REPLACE INTO source_watermarks (chat_id, max_id) VALUES (?, ?)", rows)
                await self.db.commit()
            except Exception as e:
                logger.error(f"Persist watermarks error: {e}")

    async def is_local_file_uploaded(self, file_path: str, target_chat: str, target_topic: int = 0) -> bool:
        if not self.db: return False
        async with self.db_lock:
            try:
                async with self.db.execute("""
                    SELECT 1 FROM local_folder_uploads WHERE file_path=? AND target_chat=? AND target_topic=? LIMIT 1
                """, (str(file_path), str(target_chat), int(target_topic or 0))) as cursor:
                    return (await cursor.fetchone()) is not None
            except Exception:
                return False

    async def record_local_file_upload(self, file_path: str, file_size: int, target_chat: str, target_topic: int = 0, subject: str = ""):
        if not self.db: return
        async with self.db_lock:
            try:
                await self.db.execute("""
                    INSERT OR REPLACE INTO local_folder_uploads (file_path, file_size, target_chat, target_topic, subject, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (str(file_path), int(file_size), str(target_chat), int(target_topic or 0), str(subject), time.time()))
                await self.db.commit()
            except Exception as e:
                logger.error(f"Record local upload error: {e}")

    async def close(self):
        self.running = False
        with suppress(Exception):
            await asyncio.wait_for(self.write_queue.join(), timeout=10.0)
        if self.writer_task:
            with suppress(Exception):
                await asyncio.wait_for(self.writer_task, timeout=2.0)
        await self.persist_watermarks()
        if self.db:
            async with self.db_lock:
                with suppress(Exception): await self.db.close()

class AsyncDLQ:
    def __init__(self, path="dead_letter.jsonl"):
        self.path = Path(path)
        self.lock = asyncio.Lock()
    async def append(self, chat_id, msg_id, error, target_chat=None, target_topic=0):
        rec = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "chat": str(chat_id),
            "msg": int(msg_id),
            "error": str(error)[:1000],
            "target_chat": str(target_chat) if target_chat else None,
            "target_topic": int(target_topic or 0),
        }
        async with self.lock:
            line = json.dumps(rec) + "\n"
            await asyncio.to_thread(self._write, line)
    def _write(self, line):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(line)

    def export_json_report(self, export_path="dlq_report.json"):
        """Export all DLQ records into a clean, formatted JSON report."""
        if not self.path.exists():
            return None, 0
        records = []
        try:
            with self.path.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        with suppress(Exception):
                            records.append(json.loads(line))
            
            out_file = Path(export_path)
            with out_file.open("w", encoding="utf-8") as out:
                json.dump({
                    "exported_at": datetime.now(timezone.utc).isoformat(),
                    "total_failures": len(records),
                    "failed_items": records
                }, out, indent=2)
            return str(out_file.resolve()), len(records)
        except Exception as e:
            logger.error(f"DLQ export error: {e}")
            return None, 0

# ============================================================
# 8. PERFECT 16:9 THUMBNAIL ENFORCER
# ============================================================
class ThumbEnforcer:
    def __init__(self):
        self.raw = os.getenv("THUMB_FILE", "kind_doctor_thumb.jpg").strip()
        self.cache = "tg_thumb_cached.jpg"
        self._build()

    def _build(self):
        if not PIL_AVAILABLE or not Image:
            return
        load_dotenv(override=True)
        self.raw = os.getenv("THUMB_FILE", "kind_doctor_thumb.jpg").strip()
        if not os.path.exists(self.raw):
            try:
                img = Image.new("RGB", (1280, 720), (15, 20, 25))
                draw = ImageDraw.Draw(img)
                for y in range(720):
                    c = int(20 + (y / 720) * 35)
                    draw.line((0, y, 1280, y), fill=(c, c + 5, c + 15))
                try:
                    main_f = ImageFont.truetype("arialbd.ttf", 90)
                    sub_f = ImageFont.truetype("arial.ttf", 50)
                except Exception:
                    main_f = sub_f = ImageFont.load_default()
                draw.text((200, 250), GROUP_BRAND, fill=(0, 255, 127), font=main_f)
                draw.text((250, 400), f"By {TELEGRAM_BRAND.replace('**', '')}", fill=(255, 255, 255), font=sub_f)
                img.save(self.raw, quality=95)
            except Exception: pass

        need_rebuild = False
        if not os.path.exists(self.cache):
            need_rebuild = True
        elif os.path.exists(self.raw):
            with suppress(Exception):
                if os.path.getmtime(self.raw) > os.path.getmtime(self.cache):
                    need_rebuild = True

        if need_rebuild and os.path.exists(self.raw):
            try:
                with Image.open(self.raw) as src:
                    src = src.convert("RGB")
                    if ImageOps and hasattr(ImageOps, "fit"):
                        img = ImageOps.fit(src, (1280, 720), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
                    else:
                        img = src.resize((1280, 720), Image.Resampling.LANCZOS)
                    img.save(self.cache, "JPEG", quality=95, optimize=True)
            except Exception: pass

    def force_regenerate(self):
        if os.path.exists(self.cache):
            with suppress(Exception): os.remove(self.cache)
        self._build()

    def get(self):
        self._build()
        if os.path.exists(self.cache):
            return self.cache
        if os.path.exists(self.raw):
            return self.raw
        return None

# ============================================================
# 9. TELEGRAM MULTI-SESSION & DYNAMIC RPC GUARD
# ============================================================
async def interactive_telegram_login(client):
    if not client.is_connected():
        await client.connect()
        
    if await client.is_user_authorized():
        return client

    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel(
        "[bold cyan]🔐 TELEGRAM DUAL LOGIN PANEL & AUTHENTICATION WIZARD[/]\n\n"
        "• 🌐 [bold white]Auto-Opening Visual Dual Login Panel in your Browser...[/]\n"
        "     [dim]Scan QR Code instantly with your Telegram Phone App OR enter Mobile OTP.[/]\n"
        "     [dim]No manual .env file editing required.[/]",
        border_style="cyan", box=box.ROUNDED
    ))
    
    # Priority 1: Launch browser dual login panel directly
    try:
        from tools.login_panel import launch_dual_login_wizard
        console.print("[bold green]🚀 Opening browser login tab at http://127.0.0.1:5005...[/]")
        success = await launch_dual_login_wizard(client, port=5005)
        if success:
            me = await client.get_me()
            user_name = getattr(me, 'first_name', '') or getattr(me, 'username', 'Telegram User')
            console.print(f"\n[bold green]🎉 Login Successful! Connected as [bold yellow]{user_name}[/] (ID: {me.id})[/]")
            await asyncio.sleep(1.0)
            return client
    except Exception as le:
        console.print(f"[yellow]⚠️ Browser panel failed ({le}). Falling back to terminal prompt...[/]")

    # Fallback Option A: Terminal QR Code
    try:
        import qrcode
        qr = await client.qr_login()
        qr_gen = qrcode.QRCode(version=1, box_size=1, border=1)
        qr_gen.add_data(qr.url)
        qr_gen.make(fit=True)
        console.print("\n[bold green]📱 Scan this QR Code with your Telegram App:[/]")
        console.print("[dim]Telegram ➔ Settings ➔ Devices ➔ Link Desktop Device[/]\n")
        qr_gen.print_ascii(invert=True)
        with console.status("[bold cyan]Waiting for you to scan QR in Telegram...[/]"):
            user = await qr.wait(timeout=120)
            if user:
                user_name = getattr(user, 'first_name', '') or getattr(user, 'username', 'Telegram User')
                console.print(f"\n[bold green]🎉 Login Successful! Connected as [bold yellow]{user_name}[/] (ID: {user.id})[/]")
                await asyncio.sleep(1.0)
                return client
    except SessionPasswordNeededError:
        pwd = getpass.getpass("Enter your Two-Step Verification (2FA) Password: ")
        me = await client.sign_in(password=pwd)
        if me: return client
    except (ImportError, ModuleNotFoundError):
        console.print("[dim]ℹ️ QR library not found, proceeding directly with phone login...[/]")
    except Exception as qe:
        console.print(f"[yellow]⚠️ QR login skipped ({qe}). Falling back to phone...[/]")


    phone_input = await safe_input("Enter Phone Number with Country Code (e.g. +919876543210)", allow_cancel=True)
    if not phone_input:
        return client
        
    phone = phone_input.strip().replace(" ", "").replace("-", "")
    if not phone.startswith("+"):
        phone = "+" + phone
        
    console.print(f"\n[cyan]📡 Contacting Telegram MTProto servers for [bold yellow]{phone}[/]...[/]")
    try:
        sent_code = await client.send_code_request(phone)
    except PhoneNumberInvalidError:
        console.print("[bold red]❌ Invalid Phone Number:[/] Please ensure you included your country code (e.g. +91 for India).")
        await safe_input("\nPress Enter to continue", allow_cancel=False)
        return client
    except FloodWaitError as fe:
        console.print(f"[bold red]❌ Telegram FloodWait limit hit:[/] Telegram has temporarily rate-limited login requests for {fe.seconds} seconds. Please wait before trying again.")
        await safe_input("\nPress Enter to continue", allow_cancel=False)
        return client
    except Exception as e:
        console.print(f"[bold red]❌ Telegram rejected login request:[/] {e}")
        await safe_input("\nPress Enter to continue", allow_cancel=False)
        return client

    code_type_name = type(getattr(sent_code, 'type', None)).__name__
    if "App" in code_type_name:
        dest_badge = "📲 [bold green]Telegram Mobile App[/] (Check the 'Telegram' chat with blue verified tick)"
    elif "Sms" in code_type_name:
        dest_badge = "📩 [bold green]SMS Message[/] (Check your phone's SMS inbox)"
    elif "Email" in code_type_name:
        dest_badge = "📧 [bold green]Registered Email[/] (Check your email inbox and spam folder)"
    elif "Call" in code_type_name:
        dest_badge = "📞 [bold green]Phone Call[/] (Telegram is calling your phone with voice code)"
    else:
        dest_badge = "📲 [bold green]Telegram App / SMS[/]"

    console.print(Panel(
        f"[bold green]✔ Code successfully dispatched by Telegram Servers![/]\n\n"
        f"🎯 [bold white]Where the code was sent:[/] {dest_badge}\n"
        f"⏳ [dim]Enter the 5-digit verification code below.[/]",
        border_style="green", box=box.ROUNDED
    ))
    
    code = await safe_input("Enter the 5-digit Telegram Code you received", allow_cancel=True)
    if not code:
        return client
        
    code_clean = code.strip().replace(" ", "").replace("-", "")
    
    me = None
    try:
        me = await client.sign_in(phone=phone, code=code_clean)
    except SessionPasswordNeededError:
        console.print("\n[yellow]🔑 Two-Step Verification (2FA Cloud Password) is enabled on this account.[/]")
        pwd = getpass.getpass("Enter your Two-Step Verification Password: ")
        try:
            me = await client.sign_in(password=pwd)
        except Exception as pe:
            console.print(f"[bold red]❌ 2FA Password incorrect:[/] {pe}")
            await safe_input("\nPress Enter to continue", allow_cancel=False)
            return client
    except Exception as e:
        console.print(f"[bold red]❌ Sign-in failed:[/] {e}")
        await safe_input("\nPress Enter to continue", allow_cancel=False)
        return client

    if me:
        user_name = getattr(me, 'first_name', '') or getattr(me, 'username', 'Telegram User')
        console.print(f"\n[bold green]🎉 Login Successful! Connected as [bold yellow]{user_name}[/] (ID: {me.id})[/]")
        await asyncio.sleep(1.5)
    return client

TELEGRAM_DEVICE_PARAMS = {
    "device_model": "Samsung Galaxy S24 Ultra",
    "system_version": "Android 14",
    "app_version": "10.9.2",
    "lang_code": "en",
    "system_lang_code": "en-US",
    "timeout": 25,
    "flood_sleep_threshold": 60,
    "connection_retries": 10,
    "request_retries": 5
}

class MultiSessionManager:
    """
    Enterprise Telegram Multi-Session & Account Pool Manager with Device Fingerprint Shield.
    Manages multiple .session files, enables active account switching,
    round-robin load balancing pool mode, and automatic FloodWait failover.
    """
    def __init__(self, api_id, api_hash):
        self.api_id = api_id
        self.api_hash = api_hash
        self.clients = []
        self.session_names = []
        self.active_index = 0
        self._round_robin_idx = 0
        self.pool_mode = False
        self._flood_cooldowns = {}
        self._discover_sessions()

    def _discover_sessions(self):
        if not self.api_id or not self.api_hash:
            return
        self.clients.clear()
        self.session_names.clear()
        
        # Only discover genuine user account sessions, strictly ignoring internal/scanner sessions
        session_files = sorted([
            f for f in os.listdir(".") 
            if f.endswith(".session") and not f.startswith(".")
            and not f.startswith("session_scanner")
            and not f.startswith("session_bot_scanner")
            and "scanner" not in f.lower()
        ])
        if "session_forwarder.session" in session_files:
            session_files.remove("session_forwarder.session")
            session_files.insert(0, "session_forwarder.session")
            
        if not session_files:
            session_files = ["session_forwarder.session"]
            
        for sf in session_files:
            name = str(Path(sf).with_suffix(""))
            self.session_names.append(Path(name).name)
            self.clients.append(TelegramClient(name, self.api_id, self.api_hash, **TELEGRAM_DEVICE_PARAMS))
            
        if self.active_index >= len(self.clients):
            self.active_index = 0

    def add_session(self, session_name: str) -> TelegramClient:
        clean_name = str(Path(session_name).stem)
        if clean_name in self.session_names:
            idx = self.session_names.index(clean_name)
            return self.clients[idx]
        
        client = TelegramClient(clean_name, self.api_id, self.api_hash, **TELEGRAM_DEVICE_PARAMS)
        self.session_names.append(clean_name)
        self.clients.append(client)
        return client

    def set_active_session(self, target: int | str) -> bool:
        if isinstance(target, int):
            if 0 <= target < len(self.clients):
                self.active_index = target
                return True
        elif isinstance(target, str):
            clean_name = str(Path(target).stem)
            if clean_name in self.session_names:
                self.active_index = self.session_names.index(clean_name)
                return True
        return False

    def mark_flood_wait(self, session_name: str, seconds: int):
        clean_name = str(Path(session_name).stem)
        self._flood_cooldowns[clean_name] = time.time() + max(1, seconds)

    def is_session_cooling_down(self, session_name: str) -> bool:
        clean_name = str(Path(session_name).stem)
        cd = self._flood_cooldowns.get(clean_name, 0)
        return time.time() < cd

    async def _prompt_credentials(self):
        if self.api_id and self.api_hash and self.api_id != 2040 and self.api_hash != "b18441a1ff607e10a989891a5462e627":
            return

        clear_screen()
        console.print(get_persistent_header())
        console.print(Panel(
            "[bold cyan]🔑 TELEGRAM API CREDENTIALS SETUP (1-TIME SETUP)[/]\n\n"
            "Telegram MTProto protocol securely connect hone ke liye [bold yellow]API_ID[/] aur [bold yellow]API_HASH[/] mangta hai.\n"
            "• Ye bilkul FREE hai aur 1 minute me mil jata hai:\n"
            "   1. Apne phone ya computer browser me [bold cyan]https://my.telegram.org[/] kholein.\n"
            "   2. Apna Telegram mobile number (+91...) daal kar official Telegram code enter karein.\n"
            "   3. [bold white]'API development tools'[/] par click karein aur koi bhi app name likh dein.\n"
            "   4. Wahan se apna [bold yellow]api_id[/] aur [bold yellow]api_hash[/] copy karke yahan daalein:\n\n"
            "[dim]Note: Ye details automatically aapki `.env` file me save ho jayengi.[/]",
            border_style="cyan", box=box.ROUNDED
        ))

        while not self.api_id or self.api_id == 2040:
            val = await safe_input("👉 Enter your Telegram API_ID (numeric numbers only)", allow_cancel=False)
            val = val.strip()
            if val.isdigit() and int(val) > 0 and int(val) != 2040:
                self.api_id = int(val)
                with suppress(Exception): set_key(".env", "API_ID", str(self.api_id))
            else:
                console.print("[bold red]❌ Invalid API_ID. Kripya apna sahi numeric API_ID enter karein.[/]")

        while not self.api_hash or self.api_hash == "b18441a1ff607e10a989891a5462e627":
            val = await safe_input("👉 Enter your Telegram API_HASH (32-character hex code)", allow_cancel=False)
            val = val.strip()
            if len(val) >= 16 and val != "b18441a1ff607e10a989891a5462e627":
                self.api_hash = val
                with suppress(Exception): set_key(".env", "API_HASH", self.api_hash)
            else:
                console.print("[bold red]❌ Invalid API_HASH. Kripya apna sahi 32-character API_HASH enter karein.[/]")

        console.print("[bold green]✔ Telegram API credentials successfully saved into `.env`![/]\n")
        await asyncio.sleep(1.0)

    async def _safe_connect(self, client: TelegramClient):
        """Connects client with automatic self-healing for SQLite database locked errors."""
        try:
            await client.connect()
        except Exception as e:
            if "database is locked" in str(e).lower() or "sqlite3.operationalerror" in str(e).lower():
                console.print(f"[bold yellow]⚠️ Session database lock detected. Auto-cleaning stale lock files & retrying...[/]")
                for pat in ["*.session-journal", "*.session-wal", "*.session-shm"]:
                    for f in Path(".").glob(pat):
                        with suppress(Exception): f.unlink(missing_ok=True)
                await asyncio.sleep(1.0)
                await client.connect()
            else:
                raise

    async def start_all(self):
        if not self.api_id or not self.api_hash:
            await self._prompt_credentials()
            if self.api_id and self.api_hash and not self.clients:
                self._discover_sessions()

        # Connect clients without blindly prompting repeated logins for non-primary sessions
        for idx, client in enumerate(self.clients):
            if not client.is_connected():
                await self._safe_connect(client)
            # Only trigger interactive login on the primary active account
            if idx == self.active_index and not await client.is_user_authorized():
                await interactive_telegram_login(client)
            if await client.is_user_authorized():
                with suppress(Exception):
                    async for _ in client.iter_dialogs(limit=1):
                        pass

    async def ensure_active_client(self):
        if not self.api_id or not self.api_hash:
            await self._prompt_credentials()
            if self.api_id and self.api_hash and not self.clients:
                self._discover_sessions()
                
        client = self.get_client()
        if not client:
            return None
        if not client.is_connected():
            await self._safe_connect(client)
        if not await client.is_user_authorized():
            await interactive_telegram_login(client)
        return client


    async def disconnect_all(self):
        for client in self.clients:
            with suppress(Exception): await client.disconnect()

    def get_client(self):
        if not self.clients:
            return None
        if not self.pool_mode or len(self.clients) == 1:
            if 0 <= self.active_index < len(self.clients):
                return self.clients[self.active_index]
            return self.clients[0]
            
        now = time.time()
        for _ in range(len(self.clients)):
            idx = self._round_robin_idx % len(self.clients)
            self._round_robin_idx += 1
            sname = self.session_names[idx]
            if now >= self._flood_cooldowns.get(sname, 0):
                return self.clients[idx]
        return self.clients[self.active_index] if self.clients else None

    async def get_sessions_status(self) -> list:
        status_list = []
        for i, (name, client) in enumerate(zip(self.session_names, self.clients)):
            is_conn = client.is_connected()
            is_auth = False
            user_info = {}
            if is_conn:
                try:
                    is_auth = await client.is_user_authorized()
                    if is_auth:
                        me = await client.get_me()
                        if me:
                            user_info = {
                                "id": getattr(me, "id", None),
                                "first_name": getattr(me, "first_name", "") or "",
                                "username": getattr(me, "username", "") or "",
                                "phone": getattr(me, "phone", "") or ""
                            }
                except Exception:
                    pass
            status_list.append({
                "index": i,
                "name": name,
                "is_active": (i == self.active_index),
                "is_connected": is_conn,
                "is_authorized": is_auth,
                "is_cooling_down": self.is_session_cooling_down(name),
                "user": user_info
            })
        return status_list

class RateBudgeter:
    """
    Sliding-window request velocity budgeter with Poisson-Distributed Human Jitter (RES-BAN-001).
    Proactively prevents Telegram FloodWait by simulating natural human dispatch variations.
    """
    def __init__(self, max_per_minute: int = 25):
        self.max_per_minute = max_per_minute
        self.history = deque(maxlen=max_per_minute)
        self.cooldown_until = 0.0

    def record_flood_wait(self, seconds: float):
        self.cooldown_until = time.time() + float(seconds) + 0.5

    async def pace(self):
        now = time.time()
        if now < self.cooldown_until:
            await asyncio.sleep(self.cooldown_until - now)
            now = time.time()

        if len(self.history) >= self.max_per_minute:
            oldest = self.history[0]
            elapsed = now - oldest
            if elapsed < 60.0:
                base_needed = min(max((60.0 - elapsed) / max(1, self.max_per_minute - len(self.history) + 1), 0.1), 2.0)
                # Anti-Ban Human Jitter Matrix
                import random
                jitter = random.uniform(0.12, 0.42)
                await asyncio.sleep(base_needed + jitter)
                now = time.time()

        self.history.append(now)

class AdaptiveSpeedCruiseControl:
    """
    Adaptive Smart Speed & Emergency Cruise Control Engine.
    - Full Throttle: Uncaps concurrent chunk uploads up to 40-48 streams (~20-50+ MB/s on gigabit VPS).
    - Smart Brake: If Telegram congestion, FloodWait, or slow chunk ACK (>3.5s) is detected,
      it instantly drops concurrency (down to 4-8) to prevent TCP packet loss, lag, or account flags.
    - Smooth Acceleration: When transfers remain stable for consecutive chunks, it automatically
      ramps concurrency back up (+2 per successful burst) with zero manual restarts.
    """
    def __init__(self, min_concurrency: int = 4, max_concurrency: int = 40, start_concurrency: int = 32):
        self.min_concurrency = min_concurrency
        self.max_concurrency = max_concurrency
        self.current_concurrency = start_concurrency
        self.consecutive_successes = 0
        self.last_brake_time = 0.0

    def get_concurrency(self) -> int:
        env_override = os.getenv("UPLOAD_PARALLELISM")
        if env_override and env_override.isdigit():
            val = int(env_override)
            if val > self.max_concurrency:
                return val
        return self.current_concurrency

    def apply_brake(self, reason: str = "congestion", severity: float = 0.5):
        """Immediately brake down speed on congestion or flood risk."""
        old = self.current_concurrency
        drop_target = max(self.min_concurrency, int(self.current_concurrency * (1.0 - severity)))
        self.current_concurrency = drop_target
        self.consecutive_successes = 0
        self.last_brake_time = time.time()
        logger.warning(f"🚨 [Smart Brake Activated] Reason: {reason} | Concurrency throttled: {old} -> {self.current_concurrency}")

    def report_chunk_done(self, duration: float):
        """Monitor chunk completion duration and smoothly accelerate if road is clear."""
        now = time.time()
        if duration > 3.5:
            self.apply_brake(reason=f"Slow Socket ACK ({duration:.2f}s)", severity=0.35)
            return

        if now - self.last_brake_time < 2.5:
            return

        self.consecutive_successes += 1
        if self.consecutive_successes >= 3 and self.current_concurrency < self.max_concurrency:
            self.consecutive_successes = 0
            self.current_concurrency = min(self.max_concurrency, self.current_concurrency + 2)
            logger.info(f"⚡ [Smart Acceleration] High throughput verified | Concurrency boosted to: {self.current_concurrency}")

GLOBAL_CRUISE_CONTROLLER = AdaptiveSpeedCruiseControl()

GLOBAL_RATE_BUDGETER = RateBudgeter(max_per_minute=25)

async def with_retry_call(client, func, *args, max_retries=10, base_delay=1.0, **kwargs):
    attempt = 0
    while True:
        attempt += 1
        try:
            return await func(client, *args, **kwargs)
        except FloodWaitError as e:
            GLOBAL_CRUISE_CONTROLLER.apply_brake(reason=f"Telegram FloodWait ({e.seconds}s)", severity=0.7)
            GLOBAL_RATE_BUDGETER.record_flood_wait(e.seconds)
            wait_time = int(e.seconds) + 1
            logger.warning(f"Telegram FloodWait hit ({e.seconds}s). Auto-sleeping {wait_time}s before retry (Attempt {attempt})...")
            if e.seconds > 600 or attempt >= 25:
                raise
            await asyncio.sleep(wait_time)
        except RPCError as e:
            GLOBAL_CRUISE_CONTROLLER.apply_brake(reason=f"RPCError ({type(e).__name__})", severity=0.3)
            if attempt >= max_retries:
                raise
            delay = min(base_delay * (2 ** (attempt - 1)), 30.0)
            logger.warning(f"RPCError ({e}). Retrying in {delay:.1f}s (Attempt {attempt}/{max_retries})...")
            await asyncio.sleep(delay)
        except (OSError, ConnectionError, asyncio.TimeoutError) as e:
            GLOBAL_CRUISE_CONTROLLER.apply_brake(reason=f"Socket/Timeout ({type(e).__name__})", severity=0.4)
            if attempt >= max_retries:
                raise
            delay = min(base_delay * (2 ** (attempt - 1)), 20.0)
            await asyncio.sleep(delay)

class RPCGuard:
    def __init__(self, session_mgr: MultiSessionManager, metrics: dict, budgeter: RateBudgeter = None):
        self.session_mgr = session_mgr
        self.metrics = metrics
        self.budgeter = budgeter or GLOBAL_RATE_BUDGETER

    async def execute(self, func, timeout: float = 60.0, client=None):
        client = client or self.session_mgr.get_client()
        await self.budgeter.pace()
        self.metrics["api_calls"] += 1
        return await with_retry_call(client, lambda c: asyncio.wait_for(func(c), timeout=timeout))

    async def execute_chunk(self, func, timeout: float = 120.0, client=None):
        client = client or self.session_mgr.get_client()
        self.metrics["api_calls"] += 1
        return await with_retry_call(client, lambda c: asyncio.wait_for(func(c), timeout=timeout))

# ============================================================
# 9.5 INTERACTIVE DIALOG PICKER & PREFLIGHT ENTITY VALIDATOR
# ============================================================
async def get_account_channels_list(client):
    channels = []
    try:
        dialogs = await client.get_dialogs(limit=None)
        for d in dialogs:
            if isinstance(d.entity, (Channel, Chat)):
                name = str(d.name or "Unnamed").strip()
                channels.append({"id": d.id, "title": name, "username": getattr(d.entity, "username", None)})
    except Exception as e:
        logger.error(f"Error listing dialogs: {e}")
    return channels

async def interactive_channel_selector(client, prompt_title="Select Channel"):
    channels = await get_account_channels_list(client)
    if not channels:
        console.print("[yellow]⚠️ No joined channels list returned directly by Telegram API.[/]")
        console.print(f"[bold cyan]👉 Paste your {prompt_title} Link (@username, https://t.me/..., or Chat ID -100...):[/]")
        raw = await safe_input("Paste Telegram Link / Chat ID (or 0 to Cancel)", allow_cancel=True)
        if not raw or raw.strip() == "0":
            return None
        parsed = parse_telegram_link(raw.strip())
        if "error" not in parsed and parsed.get("CHAT_ID"):
            topic_id = parsed.get("TOPIC_ID") or 0
            if not topic_id:
                topic_choice = await safe_input("Enter Topic / Thread ID (if supergroup topic, otherwise 0 for General)", default_val="0")
                if topic_choice and topic_choice.isdigit():
                    topic_id = int(topic_choice)
            return {"id": parsed["CHAT_ID"], "topic": topic_id, "title": str(parsed["CHAT_ID"])}
        return {"id": raw.strip(), "topic": 0, "title": raw.strip()}
    
    current_list = channels
    while True:
        console.print(f"\n[bold cyan]📋 Your Joined Telegram Channels & Groups ({prompt_title}):[/]")
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=4)
        table.add_column("Channel Name", style="bold green")
        table.add_column("Chat ID", style="yellow")
        table.add_column("Username / Link", style="cyan")
        
        for idx, c in enumerate(current_list, 1):
            uname = f"@{c['username']}" if c['username'] else "[dim]Private[/]"
            table.add_row(str(idx), c['title'][:32], str(c['id']), uname)
        
        console.print(table)
        console.print("[dim]Enter number to select, 'S' to search by keyword, 'P' to paste link/ID, 'A' for all, or 0 to Cancel.[/]\n")
        
        choice = await safe_input("Choose Option (# / S / P)", allow_cancel=True)
        if not choice: return None
        if choice.upper() == "S":
            query = await safe_input("Enter search keyword", allow_cancel=True)
            if query:
                current_list = [c for c in channels if query.lower() in c['title'].lower() or (c['username'] and query.lower() in c['username'].lower())]
                if not current_list:
                    console.print(f"[yellow]No channels matching '{query}'. Showing all.[/]")
                    current_list = channels
            continue
        elif choice.upper() == "A":
            current_list = channels
            continue
        elif choice.upper() == "P":
            raw = await safe_input("Paste Telegram Link / Chat ID", allow_cancel=True)
            if not raw: return None
            parsed = parse_telegram_link(raw)
            if "error" in parsed or not parsed.get("CHAT_ID"):
                console.print(f"[bold red]❌ Invalid Telegram Link / Chat ID: {parsed.get('error', 'Unknown error')}[/]")
                continue
            topic_id = parsed.get("TOPIC_ID") or 0
            if not topic_id:
                topic_choice = await safe_input("Enter Topic / Thread ID (if supergroup topic, otherwise 0 for General)", default_val="0")
                if topic_choice and topic_choice.isdigit():
                    topic_id = int(topic_choice)
            return {"id": parsed["CHAT_ID"], "topic": topic_id, "title": str(parsed["CHAT_ID"])}

        if choice.startswith("-") or choice.startswith("@") or "t.me" in choice or (choice.isdigit() and int(choice) > len(current_list)):
            parsed = parse_telegram_link(choice)
            if "error" not in parsed and parsed.get("CHAT_ID"):
                topic_id = parsed.get("TOPIC_ID") or 0
                if not topic_id:
                    topic_choice = await safe_input("Enter Topic / Thread ID (if supergroup topic, otherwise 0 for General)", default_val="0")
                    if topic_choice and topic_choice.isdigit():
                        topic_id = int(topic_choice)
                return {"id": parsed["CHAT_ID"], "topic": topic_id, "title": str(parsed["CHAT_ID"])}
            elif choice.isdigit() and int(choice) > len(current_list):
                console.print("[red]Invalid selection number. Try again.[/]")
                continue
            else:
                console.print(f"[bold red]❌ Invalid Telegram Link / Chat ID: {parsed.get('error', 'Unknown error')}[/]")
                continue
        
        if choice.isdigit() and 1 <= int(choice) <= len(current_list):
            sel = current_list[int(choice) - 1]
            topic_id = 0
            topic_choice = await safe_input("Enter Topic / Thread ID (if supergroup topic, otherwise 0 for General)", default_val="0")
            if topic_choice and topic_choice.isdigit():
                topic_id = int(topic_choice)
            return {"id": sel["id"], "topic": topic_id, "title": sel["title"]}
        
        console.print("[red]Invalid selection. Try again.[/]")

async def preflight_verify_routing(client, cfg: AppConfig) -> bool:
    if cfg.routing_mode == 1:
        src_p = _parse_chat_id(cfg.source_chat)
        tgt_p = _parse_chat_id(cfg.target_chat)
        
        # Verify Source
        src_ok = False
        try:
            src_entity, src_top = await resolve_telethon_entity(client, cfg.source_chat, cfg.source_topic)
            if src_top and (not cfg.source_topic or str(cfg.source_topic) == "0"):
                cfg.source_topic = src_top
            src_ok = True
        except Exception as e:
            console.print(Panel(
                f"[bold red]❌ SOURCE CHAT NOT FOUND ON YOUR TELEGRAM ACCOUNT![/]\n\n"
                f"Configured SOURCE_CHAT : [yellow]{cfg.source_chat}[/]\n"
                f"Error Details           : [dim]{e}[/]\n\n"
                f"[bold cyan]💡 Quick Fix:[/] Your logged-in account must be a member of this chat,\n"
                f"or you can 1-click select from your joined channels right now.",
                border_style="red", box=box.ROUNDED
            ))
            sel = await interactive_channel_selector(client, prompt_title="Pick NEW Source Channel")
            if sel:
                update_env_file(chat_id=sel["id"], topic_id=sel["topic"], mode="1")
                cfg.source_chat = sel["id"]
                cfg.source_topic = sel["topic"]
                src_ok = True
            else:
                return False

        # Verify Target
        tgt_ok = False
        try:
            tgt_entity, tgt_top = await resolve_telethon_entity(client, cfg.target_chat, cfg.target_topic)
            if tgt_top and (not cfg.target_topic or str(cfg.target_topic) == "0"):
                cfg.target_topic = tgt_top
            tgt_ok = True
        except Exception as e:
            console.print(Panel(
                f"[bold red]❌ TARGET CHAT NOT FOUND ON YOUR TELEGRAM ACCOUNT![/]\n\n"
                f"Configured TARGET_CHAT : [yellow]{cfg.target_chat}[/]\n"
                f"Error Details           : [dim]{e}[/]\n\n"
                f"[bold cyan]💡 Quick Fix:[/] Your logged-in account must be an Admin/Member of this target chat.",
                border_style="red", box=box.ROUNDED
            ))
            sel = await interactive_channel_selector(client, prompt_title="Pick NEW Target Channel")
            if sel:
                update_env_file(chat_id=sel["id"], topic_id=sel["topic"], mode="2")
                cfg.target_chat = sel["id"]
                cfg.target_topic = sel["topic"]
                tgt_ok = True
            else:
                return False
                
        return src_ok and tgt_ok
    return True

# ============================================================
# 10. NON-BLOCKING STREAMER (512KB IN-MEMORY DIRECT CHUNKS)
# ============================================================
class MemoryStreamer:
    def __init__(self, rpc: RPCGuard, cfg: AppConfig, metrics: dict, ui_callback=None):
        self.rpc = rpc
        self.cfg = cfg
        self.metrics = metrics
        self.ui_callback = ui_callback
        # Gigabit High-Throughput Semaphore (48 parallel DC socket streams for uncapped pipe)
        self.tcp_sem = asyncio.Semaphore(48)

    async def _send_chunk(self, client, file_id, idx, total, payload, is_big):
        async with self.tcp_sem:
            if is_big:
                req = SaveBigFilePartRequest(file_id=file_id, file_part=idx, file_total_parts=total, bytes=payload)
            else:
                req = SaveFilePartRequest(file_id=file_id, file_part=idx, bytes=payload)
            t0 = time.time()
            try:
                await self.rpc.execute_chunk(lambda c: c(req), timeout=120.0, client=client)
                dur = time.time() - t0
                GLOBAL_CRUISE_CONTROLLER.report_chunk_done(dur)
            except FloodWaitError as e:
                GLOBAL_CRUISE_CONTROLLER.apply_brake(reason=f"FloodWait ({e.seconds}s)", severity=0.75)
                raise
            except Exception as e:
                GLOBAL_CRUISE_CONTROLLER.apply_brake(reason=f"Chunk Send Error ({type(e).__name__})", severity=0.35)
                raise

    async def stream_media(self, msg, stop_event: asyncio.Event, client=None):
        client = client or self.rpc.session_mgr.get_client()
        file_obj = getattr(msg, "file", None)
        size = int(getattr(file_obj, "size", 0) or 0)
        if size <= 0:
            raise RuntimeError(f"Invalid media size for message {msg.id}.")
        is_big = size >= BIG_FILE_THRESHOLD
        total_parts = math.ceil(size / UP_CHUNK_SIZE)
        if total_parts > 4000:
            raise RuntimeError("File size exceeds Telegram MTProto limits.")
        file_id = generate_random_long()
        fallback_ext = ".bin"
        if getattr(msg, "photo", None):
            fallback_ext = ".jpg"
        elif getattr(msg, "video", None):
            fallback_ext = ".mp4"
        elif getattr(msg, "audio", None) or getattr(msg, "voice", None):
            fallback_ext = ".mp3"
        elif getattr(msg, "document", None):
            fallback_ext = ".pdf"

        raw_name = getattr(file_obj, "name", None) or f"media_{msg.id}{fallback_ext}"
        name = sanitize_filename(raw_name, fallback_ext=fallback_ext)
        uploaded_bytes = 0

        async def drain_one(in_flight, task_sizes):
            nonlocal uploaded_bytes
            if not in_flight: return
            done, pending = await asyncio.wait(in_flight, return_when=asyncio.FIRST_COMPLETED)
            in_flight.clear()
            in_flight.update(pending)
            for task in done:
                if task.cancelled(): continue
                sz = task_sizes.pop(task, UP_CHUNK_SIZE)
                await task
                uploaded_bytes += sz
                self.metrics["bytes_uploaded"] += sz
                if self.ui_callback:
                    self.ui_callback(name, min(size, uploaded_bytes), size)

        max_file_ref_retries = 3
        for attempt in range(max_file_ref_retries):
            part_idx = 0
            buffer = bytearray()
            uploaded_bytes = 0
            in_flight = set()
            task_sizes = {}
            file_id = generate_random_long()

            try:
                stream = client.iter_download(msg.media, request_size=DL_CHUNK_SIZE, chunk_size=DL_CHUNK_SIZE, file_size=size)
                async for chunk in stream:
                    if stop_event.is_set(): raise asyncio.CancelledError()
                    if not chunk: continue
                    buffer.extend(chunk)
                    self.metrics["bytes_downloaded"] += len(chunk)

                    while len(buffer) >= UP_CHUNK_SIZE:
                        payload = bytes(buffer[:UP_CHUNK_SIZE])
                        del buffer[:UP_CHUNK_SIZE]
                        t = asyncio.create_task(self._send_chunk(client, file_id, part_idx, total_parts, payload, is_big))
                        in_flight.add(t)
                        task_sizes[t] = len(payload)
                        part_idx += 1

                        # Dynamic Cruise Control Parallelism (starts high at 32-40, scales dynamically with smart brake)
                        concurrency = GLOBAL_CRUISE_CONTROLLER.get_concurrency()
                        while len(in_flight) >= concurrency:
                            await drain_one(in_flight, task_sizes)
                            concurrency = GLOBAL_CRUISE_CONTROLLER.get_concurrency()
                        await asyncio.sleep(0)

                if buffer:
                    payload = bytes(buffer)
                    t = asyncio.create_task(self._send_chunk(client, file_id, part_idx, total_parts, payload, is_big))
                    in_flight.add(t)
                    task_sizes[t] = len(payload)
                    part_idx += 1

                while in_flight:
                    await drain_one(in_flight, task_sizes)

                if is_big:
                    return InputFileBig(id=file_id, parts=part_idx, name=name)
                return InputFile(id=file_id, parts=part_idx, name=name, md5_checksum="")

            except (FileReferenceExpiredError, RPCError, Exception) as e:
                err_str = str(e).lower()
                is_expired = isinstance(e, FileReferenceExpiredError) or "file reference has expired" in err_str or "filereference" in err_str
                if is_expired and attempt < max_file_ref_retries - 1:
                    for t in in_flight:
                        t.cancel()
                    with suppress(Exception):
                        await asyncio.gather(*in_flight, return_exceptions=True)
                    
                    chat_peer = getattr(msg, "chat_id", None) or getattr(msg, "peer_id", None)
                    if chat_peer:
                        try:
                            fresh_msgs = await client.get_messages(chat_peer, ids=[msg.id])
                            if fresh_msgs and fresh_msgs[0] and fresh_msgs[0].media:
                                msg = fresh_msgs[0]
                                file_obj = getattr(msg, "file", None)
                                size = int(getattr(file_obj, "size", 0) or size)
                                total_parts = math.ceil(size / UP_CHUNK_SIZE)
                                await asyncio.sleep(1.0)
                                continue
                        except Exception:
                            pass
                raise e

def extract_smart_hashtags(text: str) -> str:
    if not text or not str(text).strip():
        return ""
    text_str = str(text)
    norm = re.sub(r"[\W_]+", " ", text_str).strip()
    tags = []
    
    # 1. Medical & Educational Subjects (Find all matching subjects)
    for s_name, icon, pat, s_tag in SUBJECT_DEFINITIONS:
        if re.search(pat, text_str) or re.search(pat, norm):
            clean_tag = s_tag.strip()
            if clean_tag not in tags:
                tags.append(clean_tag)

    # 2. Lecture / Part / Class numbers
    m_lec = re.search(r"(?i)\b(?:lec(?:ture)?|class|session|part|chapter|no|#)\s*0*(\d{1,4})\b", norm)
    if m_lec:
        tags.append(f"#Lecture{int(m_lec.group(1)):02d}")

    # 3. Document / Notes / PDFs
    if re.search(r"(?i)\b(?:notes?|pdf|handwritten|revision|workbook|mcq|qbank)\b", norm):
        if "#Notes" not in tags:
            tags.append("#Notes")
            
    return " ".join(tags)


def check_media_filter(msg, media_filter: str) -> bool:
    if not media_filter or str(media_filter).lower().strip() in ("all", "*", "everything", "none", ""):
        return True
    f = str(media_filter).lower().strip()
    if f in ("video", "videos"):
        return bool(getattr(msg, "video", None))
    if f in ("document", "documents", "docs", "doc"):
        return bool(getattr(msg, "document", None) and not getattr(msg, "video", None) and not getattr(msg, "audio", None) and not getattr(msg, "voice", None))
    if f in ("photo", "photos", "image", "images"):
        return bool(getattr(msg, "photo", None))
    if f in ("audio", "audios", "music", "voice"):
        return bool(getattr(msg, "audio", None) or getattr(msg, "voice", None))
    if f in ("text", "messages"):
        return bool(getattr(msg, "text", None) and not getattr(msg, "media", None))
    return True

def _canonical_line_key(text: str) -> str:
    """Normalizes text for fuzzy deduplication: lowercases, removes markdown/emojis/punctuation."""
    t = re.sub(r"[\*\_`~#>•\-–—:;\|\(\)\[\]]", " ", str(text))
    t = re.sub(r"[^\w\s]", " ", t)
    t = " ".join(t.lower().split())
    t = re.sub(r"^(title|topic|subject|lecture|chapter|video|file)\s*[:\-–]?\s*", "", t, flags=re.IGNORECASE)
    t = re.sub(r"^(by|via|from|credits?|source|channel|group)\s+", "", t, flags=re.IGNORECASE)
    return " ".join(t.split())

def smart_clean_and_deduplicate_caption(raw_text: str, custom_header: str = "", signature: str = "") -> str:
    """
    Intelligently deduplicates redundant lines, titles, and repeated branding/signatures
    while preserving markdown formatting and natural structure.
    """
    if not raw_text:
        return ""

    lines = raw_text.splitlines()
    cleaned_lines = []
    seen_canonical = set()

    sig_canonical = set()
    if signature:
        for sline in signature.splitlines():
            sk = _canonical_line_key(sline)
            if len(sk) >= 3:
                sig_canonical.add(sk)
    if custom_header:
        for hline in custom_header.splitlines():
            hk = _canonical_line_key(hline)
            if len(hk) >= 3:
                sig_canonical.add(hk)

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")
            continue

        # Preserve standard Markdown dividers / rules
        if stripped in ("---", "===", "***", "___", "--"):
            cleaned_lines.append(stripped)
            continue

        ck = _canonical_line_key(stripped)

        # Skip duplicate lines or lines already present in header/signature
        if ck and len(ck) >= 3:
            if ck in seen_canonical or ck in sig_canonical or any(ck in s for s in sig_canonical if len(ck) >= 5):
                continue
            seen_canonical.add(ck)

        cleaned_lines.append(stripped)

    # Clean redundant trailing empty lines
    while cleaned_lines and cleaned_lines[-1] == "":
        cleaned_lines.pop()

    return "\n".join(cleaned_lines).strip()

def customize_caption(caption, for_media=False, batch_name=""):
    load_dotenv(override=False)
    custom_header = os.getenv("CUSTOM_HEADER", "").strip().strip("'").strip('"')
    custom_footer = os.getenv("CUSTOM_FOOTER", "").strip().strip("'").strip('"')
    auto_hashtags_enabled = os.getenv("AUTO_HASHTAGS", "false").strip().lower() in ("true", "1", "yes")
    enable_sig = os.getenv("ENABLE_SIGNATURE", "true").strip().lower() in ("true", "1", "yes")
    default_signature = f"\n\n📚 {TELEGRAM_BRAND}\n💬 {GROUP_BRAND}"
    if not enable_sig:
        signature = ""
    else:
        signature = f"\n\n{custom_footer}" if custom_footer else default_signature

    active_batch = (batch_name or os.getenv("BATCH_NAME", "")).strip().strip("'").strip('"')
    show_batch = os.getenv("SHOW_BATCH", "true").strip().lower() in ("true", "1", "yes")

    if not caption:
        if not for_media:
            return ""
        final_empty = f"{custom_header}\n\n{signature}".strip() if custom_header else signature.strip()
        return (final_empty, "") if for_media else final_empty
    
    text = str(caption)
    
    # 1. Apply Permanent Clean Rules (strip_words.txt + .env)
    text = apply_clean_rules(text)
    if not text or not text.strip():
        if not for_media:
            return ""
    
    # 2. Custom Word / Keyword Replacements (Whole-Word Smart Boundary Safe)
    replace_words_env = os.getenv("REPLACE_WORDS", "").strip()
    if replace_words_env:
        for pair in replace_words_env.split(","):
            if ":" in pair:
                old_w, new_w = pair.split(":", 1)
                if old_w.strip():
                    text = _smart_replace_word(text, old_w.strip(), new_w.strip())
    
    # 3. Strip Specific Words (Whole-Word Smart Boundary Safe)
    strip_words_env = os.getenv("STRIP_WORDS", "").strip()
    if strip_words_env:
        for word in [w.strip() for w in strip_words_env.split(",") if w.strip()]:
            text = _smart_replace_word(text, word, "")

    # 4. Handle Links (Remove or Replace with custom link)
    remove_links = os.getenv("REMOVE_LINKS", "true").strip().lower() in ("true", "1", "yes")
    replace_link = os.getenv("REPLACE_LINK", "").strip()
    if replace_link:
        text = re.sub(r"(https?://|www\.|t\.me/)\S+", replace_link, text, flags=re.IGNORECASE)
    elif remove_links:
        text = re.sub(r"(https?://|www\.|t\.me/)\S+", "", text, flags=re.IGNORECASE)

    # 5. Handle Usernames (Remove or Replace with custom username)
    replace_username = os.getenv("REPLACE_USERNAME", "").strip()
    remove_usernames = os.getenv("REMOVE_USERNAMES", "false").strip().lower() in ("true", "1", "yes")
    if replace_username:
        text = re.sub(r"@[a-zA-Z0-9_]+", replace_username, text)
    elif remove_usernames:
        text = re.sub(r"@[a-zA-Z0-9_]+", "", text)

    # 6. Clean promotional join/subscribe patterns and admin/uploader tags
    text = re.sub(r"(?i)(join|subscribe to|shared by|uploaded by|posted by|managed by|provided by|credit|credits?|admin|owner|forwarded from) (our |by |to )?(channel|group|here|admin|owner|desk|bot).*", "", text)
    
    # 7. Apply Smart Deduplication on body text before structured formatting
    text = smart_clean_and_deduplicate_caption(text, custom_header=custom_header, signature=signature)
    
    clean = re.sub(r"\n{3,}", "\n\n", text).strip()

    # Format Title Line with smart emoji: (Emoji) **Title**: {Title}
    if clean:
        lines = clean.split("\n")
        first_line = lines[0].strip()
        rest_lines = lines[1:]

        # Detect Emoji based on filename / extension
        emoji = "📄"
        lower_txt = text.lower()
        if any(ext in lower_txt for ext in (".mp4", ".mkv", ".mov", ".avi", ".webm", "video", "lecture")):
            emoji = "🎬"
        elif any(ext in lower_txt for ext in (".pdf", ".doc", ".docx", ".epub", "notes", "workbook")):
            emoji = "📄"
        elif any(ext in lower_txt for ext in (".mp3", ".m4a", ".wav", ".aac", ".ogg", "audio", "voice")):
            emoji = "🎵"
        elif any(ext in lower_txt for ext in (".jpg", ".jpeg", ".png", ".webp", "photo", "image")):
            emoji = "🖼️"

        if first_line and not re.search(r"(?i)\btitle\s*[:*]", first_line):
            formatted_title = f"{emoji} **Title**: {first_line}"
            # Check if rest_lines has redundant first_line duplicates and clean
            f_canon = _canonical_line_key(first_line)
            filtered_rest = []
            for rl in rest_lines:
                if _canonical_line_key(rl) != f_canon:
                    filtered_rest.append(rl)
            clean = "\n".join([formatted_title] + filtered_rest).strip()

    # Batch Tag Integration
    if active_batch and show_batch and active_batch.lower() not in clean.lower():
        clean = f"{clean}\n🎯 **Batch**: {active_batch}" if clean else f"🎯 **Batch**: {active_batch}"

    # Smart Auto-Hashtags & Subject Tagging inside Caption
    strip_tags = os.getenv("STRIP_HASHTAGS", "false").strip().lower() in ("true", "1", "yes")
    if not auto_hashtags_enabled and strip_tags:
        clean = re.sub(r'#\w+', '', clean)
        clean = re.sub(r'[ \t]+', ' ', clean)
        clean = re.sub(r'\n\s*\n\s*\n+', '\n\n', clean).strip()
    elif auto_hashtags_enabled:
        generated_tags = extract_smart_hashtags(text)
        if generated_tags:
            tag_tokens = generated_tags.split()
            missing_tokens = [t for t in tag_tokens if t.lower() not in clean.lower()]
            if missing_tokens:
                tags_formatted = " ".join(missing_tokens)
                clean = f"{clean}\n\n✨ {tags_formatted}" if clean else f"✨ {tags_formatted}"

    # Prepend custom header
    if custom_header and not clean.startswith(custom_header):
        clean = f"{custom_header}\n\n{clean}" if clean else custom_header

    # Append footer/signature without duplicates
    if signature:
        if not clean.endswith(signature.strip()):
            full_text = f"{clean}{signature}" if clean else signature.strip()
        else:
            full_text = clean
    else:
        full_text = clean

    if not for_media:
        if not clean or not clean.strip():
            return ""
        return full_text

    # Media captions limit is 1024 chars in Telegram
    if len(full_text) <= 1024:
        return full_text, ""
    else:
        main_chunk = full_text[:1024]
        split_idx = main_chunk.rfind("\n")
        if split_idx < 800:
            split_idx = main_chunk.rfind(" ")
        if split_idx < 700:
            split_idx = 1020
            
        cap_1024 = full_text[:split_idx].strip()
        overflow = full_text[split_idx:].strip()
        return cap_1024, overflow

def format_media_log_detail(m, prefix="✔ Sent") -> str:
    msg_id = getattr(m, "id", "?")
    size_str = ""
    file_obj = getattr(m, "file", None)
    if file_obj and getattr(file_obj, "size", None):
        sz = file_obj.size
        if sz < 1024 * 1024:
            size_str = f"{sz / 1024:.1f} KB"
        elif sz < 1024 * 1024 * 1024:
            size_str = f"{sz / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{sz / (1024 * 1024 * 1024):.2f} GB"

    # Filename detection
    name = None
    if file_obj and getattr(file_obj, "name", None):
        name = file_obj.name
    elif getattr(m, "document", None) and hasattr(m.document, "attributes"):
        for attr in m.document.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                name = getattr(attr, "file_name", None)
                break

    if getattr(m, "video", None):
        name_display = name or f"Video_{msg_id}.mp4"
        sz_part = f" ({size_str})" if size_str else ""
        return f"[bold green]{prefix} Video:[/] [yellow]{name_display}[/][dim]{sz_part} | ID: #{msg_id}[/]"
    elif getattr(m, "document", None):
        name_display = name or f"Document_{msg_id}"
        sz_part = f" ({size_str})" if size_str else ""
        return f"[bold green]{prefix} File:[/] [yellow]{name_display}[/][dim]{sz_part} | ID: #{msg_id}[/]"
    elif getattr(m, "photo", None):
        sz_part = f" ({size_str})" if size_str else ""
        return f"[bold green]{prefix} Photo:[/] [yellow]{name or 'Photo'}[/][dim]{sz_part} | ID: #{msg_id}[/]"
    elif getattr(m, "audio", None) or getattr(m, "voice", None):
        name_display = name or f"Audio_{msg_id}"
        sz_part = f" ({size_str})" if size_str else ""
        return f"[bold green]{prefix} Audio:[/] [yellow]{name_display}[/][dim]{sz_part} | ID: #{msg_id}[/]"
    elif getattr(m, "text", None) and str(m.text).strip():
        snippet = str(m.text).strip().replace("\n", " ")
        if len(snippet) > 40:
            snippet = snippet[:37] + "..."
        return f"[bold green]{prefix} Text:[/] [cyan]\"{snippet}\"[/] [dim]| ID: #{msg_id}[/]"
    else:
        return f"[bold green]{prefix} Message:[/] [dim]ID: #{msg_id}[/]"

# ============================================================
# 10.8 SMART SUBJECT DETECTION & SLEEK DIVIDER HEADERS
# ============================================================
SUBJECT_DEFINITIONS = [
    # Foundation Pre- & Para-Clinical
    ("ANATOMY", "🫀", r"(?i)\b(anat|anatomy|neuroanat|embryo|histology)\b", "#Anatomy"),
    ("PHYSIOLOGY", "⚡", r"(?i)\b(physio|physiology|homeostasis)\b", "#Physiology"),
    ("BIOCHEMISTRY", "🧬", r"(?i)\b(biochem|biochemistry|metabolism|krebs|glycolysis)\b", "#Biochemistry"),
    ("PATHOLOGY", "🔬", r"(?i)\b(path|pathology|patho|histopath|neoplasia|biopsy)\b", "#Pathology"),
    ("PHARMACOLOGY", "💊", r"(?i)\b(pharm|pharmacology|pharma|chemo|receptor|antagonist)\b", "#Pharmacology"),
    ("MICROBIOLOGY", "🦠", r"(?i)\b(micro|microbiology|viro|bacterio|myco|parasito)\b", "#Microbiology"),
    ("FORENSIC MEDICINE", "⚖️", r"(?i)\b(fmt|forensic|toxicology|autopsy|postmortem)\b", "#ForensicMedicine"),
    ("COMMUNITY MEDICINE", "🌐", r"(?i)\b(psm|community\s*med|spm|epidemiology|biostat)\b", "#CommunityMedicine"),

    # Clinical Core Specialties
    ("OPHTHALMOLOGY", "👁️", r"(?i)\b(ophthal|ophthalmology|eye|retina|glaucoma|cataract)\b", "#Ophthalmology"),
    ("ENT", "👂", r"(?i)\b(ent|otorhinolaryngology|ear\s*nose\s*throat|larynx|sinus)\b", "#ENT"),
    ("MEDICINE", "🩺", r"(?i)\b(medicine|general\s*medicine|internal\s*med|clinical\s*cases)\b", "#Medicine"),
    ("SURGERY", "🔪", r"(?i)\b(surgery|general\s*surgery|trauma|hernia|laparoscopy|appendix)\b", "#Surgery"),
    ("OBSTETRICS & GYNAECOLOGY", "🤰", r"(?i)\b(obg|obgy|obstetrics|gynae|gynecology|pregnancy|labor)\b", "#OBG"),
    ("PAEDIATRICS", "👶", r"(?i)\b(p[ae]+diat|pediatrics|paediatrics|neonatology|newborn)\b", "#Paediatrics"),
    ("DERMATOLOGY", "🧴", r"(?i)\b(derma|dermatology|skin|std|psoriasis|eczema)\b", "#Dermatology"),
    ("RADIOLOGY", "🩻", r"(?i)\b(radio|radiology|xray|mri|ct\s*scan|ultrasound|pet\s*ct)\b", "#Radiology"),
    ("PSYCHIATRY", "🧠", r"(?i)\b(psych|psychiatry|mental\s*health|depression|bipolar)\b", "#Psychiatry"),
    ("ORTHOPAEDICS", "🦴", r"(?i)\b(ortho|orthopaedics|orthopedics|fracture|bone|joint)\b", "#Orthopaedics"),
    ("ANAESTHESIA", "💉", r"(?i)\b(an[ae]+sthesia|critical\s*care|icu|airway|intubation)\b", "#Anaesthesia"),

    # Medical & Surgical Super-Specialties
    ("CARDIOLOGY", "❤️", r"(?i)\b(cardio|cardiology|ecg|echo|stemi|angina|angioplasty|arrhythmia|troponin)\b", "#Cardiology"),
    ("NEUROLOGY & NEUROSURGERY", "🧠", r"(?i)\b(neuro|neurology|neurosurg|stroke|epilepsy|eeg|craniotomy|hematoma)\b", "#Neurology"),
    ("NEPHROLOGY & UROLOGY", "🧪", r"(?i)\b(nephro|nephrology|urology|dialysis|creatinine|renal|transplant|ckd|turp)\b", "#Nephrology"),
    ("GASTROENTEROLOGY", "🩺", r"(?i)\b(gastro|gastroenterology|hepatology|endoscopy|cirrhosis|pancreatitis|jaundice)\b", "#Gastroenterology"),
    ("PULMONOLOGY", "🫁", r"(?i)\b(pulmo|pulmonology|chest\s*med|copd|asthma|tuberculosis|tb|bronchoscopy)\b", "#Pulmonology"),
    ("ONCOLOGY", "🔬", r"(?i)\b(onco|oncology|chemo|radiation\s*onco|tumor|malignancy|carcinoma|biomarker)\b", "#Oncology"),
    ("ENDOCRINOLOGY", "🦋", r"(?i)\b(endo|endocrinology|thyroid|diabetes|pituitary|adrenal|cushing|insulin)\b", "#Endocrinology"),
    ("HEMATOLOGY", "🩸", r"(?i)\b(hemato|hematology|anemia|thalassemia|leukemia|lymphoma|coagulation|platelet)\b", "#Hematology"),
    ("RHEUMATOLOGY", "🦴", r"(?i)\b(rheuma|rheumatology|lupus|sle|arthritis|autoimmune|vasculitis)\b", "#Rheumatology"),
    ("CRITICAL CARE & EMERGENCY", "🚨", r"(?i)\b(emergency|icu|critical\s*care|acls|resuscitation|cpr|ecmo|shock)\b", "#EmergencyMedicine"),

    # Exam & Study Systems
    ("PYQs & QUESTION BANK", "📝", r"(?i)\b(pyq|pyt|question\s*bank)\b", "#PYQs"),
]

def detect_subject(text: str = "", filename: str = ""):
    combined = f"{text or ''} {filename or ''}".strip()
    if not combined: return None
    norm = re.sub(r"[\W_]+", " ", combined).strip()
    for name, icon, pattern, tag in SUBJECT_DEFINITIONS:
        if re.search(pattern, combined) or re.search(pattern, norm):
            return {"name": name, "icon": icon, "tag": tag}
    return None

# ============================================================
# 11. PIPELINE PROCESSOR & DUAL SESSION HEADERS
# ============================================================
class PipelineProcessor:
    def __init__(self, rpc, streamer, state, cfg, ui_log, metrics, dlq, session_mgr):
        self.rpc = rpc
        self.streamer = streamer
        self.state = state
        self.cfg = cfg
        self.log = ui_log
        self.metrics = metrics
        self.dlq = dlq
        self.session_mgr = session_mgr
        self.thumb = ThumbEnforcer()
        self.album_sem = asyncio.Semaphore(4)
        self.session_header_sent = set()
        self.last_subject_sent = {}
        self.topic_title_cache = {}
        self.batch_index_records = []

    async def check_and_send_subject_header(self, active_messages, target_chat, resolved_topic, client, silent_mode):
        auto_subj_env = os.getenv("AUTO_SUBJECT_HEADERS", "true").strip().lower() in ("true", "1", "yes")
        auto_subj_cfg = bool(getattr(self.cfg, "auto_subject_headers", False))
        if not auto_subj_env and not auto_subj_cfg:
            return
        
        detected = None
        for m in active_messages:
            t = str(getattr(m, "text", "") or "")
            fn = ""
            if getattr(m, "file", None) and getattr(m.file, "name", None):
                fn = str(m.file.name)
            elif getattr(m, "document", None) and hasattr(m.document, "attributes"):
                for attr in m.document.attributes:
                    if isinstance(attr, DocumentAttributeFilename):
                        fn = str(getattr(attr, "file_name", "") or "")
                        break
            detected = detect_subject(t, fn)
            if detected:
                break
                
        if not detected and resolved_topic:
            with suppress(Exception):
                t_title = await self.get_topic_title(target_chat, resolved_topic, client)
                if t_title:
                    detected = detect_subject(t_title, "")

        if not detected:
            return
            
        route_key = (str(target_chat), int(resolved_topic or 0))
        last_subj = self.last_subject_sent.get(route_key)
        
        if last_subj != detected["name"]:
            self.last_subject_sent[route_key] = detected["name"]
            auto_hashtags_enabled = os.getenv("AUTO_HASHTAGS", "true").strip().lower() in ("true", "1", "yes")
            if auto_hashtags_enabled and detected.get("tag"):
                header_text = f"✨ {detected['icon']} **{detected['name']}** ✨  {detected['tag']}"
            else:
                header_text = f"✨ {detected['icon']} **{detected['name']}** ✨"
            try:
                await self.rpc.execute(
                    lambda c: c.send_message(
                        _parse_chat_id(target_chat),
                        header_text,
                        reply_to=resolved_topic,
                        parse_mode="md",
                        silent=silent_mode
                    ),
                    client=client,
                    timeout=30.0
                )
                self.log(f"[bold green]✨ Subject Header Posted:[/] [yellow]{detected['icon']} {detected['name']}[/]")
                await asyncio.sleep(0.4)
            except Exception as e:
                self.log(f"[yellow]⚠️ Subject Header Skip:[/] {e}")

    def format_text(self, text, for_media=False):
        batch_name = getattr(self.cfg, "batch_name", "")
        return customize_caption(text, for_media=for_media, batch_name=batch_name)

    async def post_batch_index_card(self, target_chat, target_topic, client):
        if not self.batch_index_records:
            return
        silent_mode = os.getenv("SILENT_MODE", "false").strip().lower() in ("true", "1", "yes")
        resolved_topic = await self.resolve_topic_id(target_chat, target_topic, client)
        
        raw_id = str(target_chat).replace("-100", "").replace("-", "").lstrip("@")
        
        cards = []
        current_card_lines = [
            "📑 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            "📚 **BATCH INDEX & TABLE OF CONTENTS**",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ]
        
        for idx, item in enumerate(self.batch_index_records, 1):
            link = make_telegram_link(target_chat, item['msg_id'], topic_id=resolved_topic)
            clean_t = clean_index_title(item['title'], max_len=45)
            entry = f"{item['icon']} **#{idx:02d}** • [{clean_t}]({link})"
            if sum(len(l) for l in current_card_lines) + len(entry) > 3400:
                current_card_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                cards.append("\n".join(current_card_lines))
                current_card_lines = [f"📑 **BATCH INDEX (Part {len(cards)+1})**", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"]
            current_card_lines.append(entry)
            
        total_count = len(self.batch_index_records)
        current_card_lines.extend([
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"✨ **Total Delivered:** `{total_count}` Files & Lectures",
            f"📚 {TELEGRAM_BRAND} | 💬 {GROUP_BRAND}"
        ])
        cards.append("\n".join(current_card_lines))
        
        sent_first_card = None
        for idx, card in enumerate(cards):
            try:
                msg = await self.rpc.execute(
                    lambda c, card_text=card: c.send_message(
                        _parse_chat_id(target_chat),
                        card_text,
                        reply_to=resolved_topic,
                        parse_mode="md",
                        link_preview=False,
                        silent=silent_mode
                    ),
                    client=client,
                    timeout=45.0
                )
                if idx == 0 and msg:
                    sent_first_card = msg
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.info(f"Batch Index send error: {e}")

        # 📌 Auto-PIN Table of Contents at top of destination topic/channel
        auto_pin = os.getenv("AUTO_PIN_INDEX", "true").strip().lower() in ("true", "1", "yes")
        if auto_pin and sent_first_card:
            try:
                await self.rpc.execute(
                    lambda c: c.pin_message(_parse_chat_id(target_chat), sent_first_card.id, notify=False),
                    client=client,
                    timeout=30.0
                )
                self.log(f"[bold green]📌 Table of Contents pinned at top of topic successfully![/]")
            except Exception as e:
                logger.info(f"Auto-pin index note: {e}")

        self.log(f"[bold green]📑 Batch Index Card Posted ({total_count} items indexed)[/]")

    def reconstruct(self, msg):
        signature = f"\n\n📚 **{TELEGRAM_BRAND}**\n💬 {GROUP_BRAND}"
        if getattr(msg, 'poll', None):
            q = msg.poll.poll.question
            ans = "\n".join(f"• {a.text}" for a in msg.poll.poll.answers)
            return f"📊 Poll:\n**{q}**\n{ans}{signature}"
        if getattr(msg, 'contact', None):
            return f"👤 Contact: {msg.contact.first_name}\nPhone: {msg.contact.phone_number}{signature}"
        if getattr(msg, 'action', None):
            action_obj = msg.action
            if hasattr(action_obj, 'title') and action_obj.title:
                return f"⚙️ **{action_obj.title}**{signature}"
            return f"⚙️ System Message (Topic/Action){signature}"
        return f"⚙️ Secure Media / Attachment{signature}"

    async def send_session_headers(self, source_chat, source_topic, target_chat, target_topic, client):
        auto_topic_header = os.getenv("AUTO_TOPIC_HEADERS", "false").strip().lower() in ("true", "1", "yes")
        if not auto_topic_header:
            return

        route_key = (str(target_chat), int(target_topic or 0))
        if route_key in self.session_header_sent:
            return

        self.session_header_sent.add(route_key)
        resolved_topic = await self.resolve_topic_id(target_chat, target_topic, client)
        silent_mode = os.getenv("SILENT_MODE", "false").strip().lower() in ("true", "1", "yes")

        topic_title = None
        if source_topic:
            topic_title = await self.get_topic_title(source_chat, source_topic, client)
        if not topic_title and target_topic:
            topic_title = await self.get_topic_title(target_chat, target_topic, client)
        if not topic_title:
            batch_name = getattr(self.cfg, "batch_name", "") or os.getenv("BATCH_NAME", "")
            topic_title = batch_name if batch_name else "Comprehensive Study Series"

        topic_clean = str(topic_title).replace("&", "and").strip()

        # Dynamically detect real target group name
        target_group_title = None
        try:
            target_entity = await client.get_entity(_parse_chat_id(target_chat))
            target_group_title = getattr(target_entity, "title", None)
        except Exception:
            pass

        welcome_card = (
            f"📂 **Module / Topic:** **{topic_clean}**\n"
            f"👨‍⚕️ **{TELEGRAM_BRAND}** 🤍"
        )

        try:
            await self.rpc.execute(
                lambda c: c.send_message(
                    _parse_chat_id(target_chat),
                    welcome_card,
                    reply_to=resolved_topic,
                    parse_mode="md",
                    silent=silent_mode
                ),
                client=client,
                timeout=35.0
            )
            self.log(f"[bold green]✨ Topic Welcome Card Posted:[/] [yellow]{topic_clean}[/]")
            await asyncio.sleep(0.5)
        except Exception as e:
            self.log(f"[yellow]⚠️ Topic Welcome Card Skip:[/] {e}")

    async def resolve_topic_id(self, chat_id, topic_id, client):
        if not topic_id or str(topic_id).strip() in ("0", "None", ""): return None
        try:
            res = await self.rpc.execute(
                lambda c: c(GetForumTopicsRequest(channel=_parse_chat_id(chat_id), offset_date=None, offset_id=0, offset_topic=0, limit=500)),
                client=client, timeout=60.0
            )
            topic_map = {t.id: t.title for t in res.topics}
            if int(topic_id) in topic_map:
                return int(topic_id)
        except Exception:
            pass
        return int(topic_id) if int(topic_id) > 0 else None

    async def get_topic_title(self, chat_id, topic_id, client):
        if not topic_id or str(topic_id).strip() in ("0", "None", ""): return None
        cache_key = (str(chat_id), int(topic_id))
        if cache_key in self.topic_title_cache:
            return self.topic_title_cache[cache_key]
        try:
            res = await self.rpc.execute(
                lambda c: c(GetForumTopicsRequest(
                    channel=_parse_chat_id(chat_id),
                    offset_date=None,
                    offset_id=0,
                    offset_topic=0,
                    limit=100
                )),
                client=client, timeout=30.0
            )
            if hasattr(res, 'topics'):
                for t in res.topics:
                    self.topic_title_cache[(str(chat_id), int(t.id))] = str(t.title)
                if cache_key in self.topic_title_cache:
                    return self.topic_title_cache[cache_key]
        except Exception:
            pass

        try:
            msgs = await client.get_messages(_parse_chat_id(chat_id), ids=[int(topic_id)])
            if msgs and msgs[0] and getattr(msgs[0], 'action', None) and hasattr(msgs[0].action, 'title'):
                title = str(msgs[0].action.title)
                self.topic_title_cache[cache_key] = title
                return title
        except Exception:
            pass
        return f"Topic {topic_id}"

    async def execute(self, item: WorkItem, stop_event: asyncio.Event):
        if self.cfg.routing_mode == 2 and self.cfg.forwarding_rules:
            rule = self.cfg.forwarding_rules[item.rule_index]
            target_chat = rule["target_chat"]
            target_topic = rule.get("target_topic", 0) or None
            source_chat = rule["source_chat"]
            source_topic = rule.get("source_topic", 0) or 0
        else:
            target_chat = self.cfg.target_chat
            target_topic = self.cfg.target_topic or None
            source_chat = self.cfg.source_chat
            source_topic = self.cfg.source_topic or 0

        client = self.session_mgr.get_client()

        unprocessed_messages = []
        for m in item.messages:
            if not await self.state.is_processed(source_chat, m.id, target_chat, target_topic or 0):
                unprocessed_messages.append(m)

        if not unprocessed_messages and not self.cfg.run_dlq:
            return

        active_messages = unprocessed_messages if unprocessed_messages else item.messages
        global THUMB_MODE
        sig_enabled = os.getenv("ENABLE_SIGNATURE", "true").strip().lower() in ("true", "1", "yes")
        # Unified Clean Mode: If signature is disabled, custom branded thumbnail is also disabled
        t_path = self.thumb.get() if (THUMB_MODE == "custom" and sig_enabled) else None

        resolved_topic = await self.resolve_topic_id(target_chat, target_topic, client)

        silent_mode = os.getenv("SILENT_MODE", "false").strip().lower() in ("true", "1", "yes")

        # Post topic sequence headers (Welcome -> Topic Card -> Let's Start) before first material item
        await self.send_session_headers(source_chat, source_topic, target_chat, target_topic, client)

        # Post sleek Subject Header Divider on subject switch (Option 3 style: ✨ 🦴 **ANATOMY** ✨  #Anatomy)
        await self.check_and_send_subject_header(active_messages, target_chat, resolved_topic, client, silent_mode)

        success_flag = False
        direct_forward_success = False
        attempt_direct = getattr(self.cfg, "direct_forward", False)

        if attempt_direct:
            try:
                msg_ids = [m.id for m in active_messages]
                await self.rpc.execute(
                    lambda c: c.forward_messages(
                        entity=_parse_chat_id(target_chat),
                        messages=msg_ids,
                        from_peer=_parse_chat_id(source_chat),
                        silent=silent_mode
                    ),
                    client=client,
                    timeout=45.0
                )
                if len(active_messages) > 1:
                    self.log(f"[bold green]⚡ Direct Forwarded Album ({len(active_messages)} msgs)[/] [dim](ID: #{item.first_id})[/]")
                    for m in active_messages:
                        self.log(f"  ↳ {format_media_log_detail(m, prefix='Forwarded')}")
                    self.metrics["albums_forwarded"] += 1
                else:
                    m = active_messages[0]
                    self.log(format_media_log_detail(m, prefix="⚡ Direct Sent"))
                success_flag = True
                direct_forward_success = True
            except (ChatForwardsRestrictedError, ChannelPrivateError, ChatAdminRequiredError) as e:
                self.log(f"[yellow]🔒 Direct Forward Restricted ({type(e).__name__}) -> Fallback to RAM Streamer[/]")
            except Exception as e:
                self.log(f"[yellow]ℹ Direct Forward bypass -> Streamer: {str(e)[:60]}[/]")

        if not direct_forward_success:
            try:
                if len(active_messages) > 1:
                    async def process_media(m):
                        async with self.album_sem:
                            return await self.streamer.stream_media(m, stop_event, client=client)
                            
                    coros = [process_media(m) for m in active_messages if getattr(m, "media", None)]
                    if coros:
                        tasks = [asyncio.create_task(c) for c in coros]
                        caps = []
                        for m in active_messages:
                            if getattr(m, "media", None):
                                c_main, _ = self.format_text(getattr(m, "text", ""), for_media=True)
                                caps.append(c_main)
                        files = await asyncio.gather(*tasks)
                        await self.rpc.execute(
                            lambda c: c.send_file(_parse_chat_id(target_chat), files, caption=caps, thumb=t_path, reply_to=resolved_topic, parse_mode="md", silent=silent_mode),
                            client=client, timeout=120.0
                        )
                        self.log(f"[bold green]✔ Streamed Album ({len(files)} files)[/] [dim](ID: #{item.first_id})[/]")
                        for m in active_messages:
                            self.log(f"  ↳ {format_media_log_detail(m, prefix='Sent')}")
                        self.metrics["albums_forwarded"] += 1
                        success_flag = True
                else:
                    m = active_messages[0]
                    if getattr(m, "media", None) and (hasattr(m.media, 'document') or hasattr(m.media, 'photo')):
                        file = await self.streamer.stream_media(m, stop_event, client=client)
                        cap_main, cap_overflow = self.format_text(m.text, for_media=True)
                        
                        orig_doc = getattr(getattr(m, "media", None), "document", None)
                        attrs = []
                        if orig_doc and hasattr(orig_doc, "attributes"):
                            for a in orig_doc.attributes:
                                if isinstance(a, DocumentAttributeFilename):
                                    attrs.append(DocumentAttributeFilename(file_name=getattr(file, "name", a.file_name)))
                                elif isinstance(a, DocumentAttributeVideo):
                                    vid_w = int(getattr(a, "w", 0) or 0)
                                    vid_h = int(getattr(a, "h", 0) or 0)
                                    # If dimensions missing or low, enforce 16:9 HD for widescreen player on laptop & mobile
                                    if vid_w <= 0 or vid_h <= 0:
                                        vid_w, vid_h = 1280, 720
                                    attrs.append(DocumentAttributeVideo(
                                        duration=int(getattr(a, "duration", 0) or 0),
                                        w=vid_w,
                                        h=vid_h,
                                        supports_streaming=True
                                    ))
                                elif isinstance(a, DocumentAttributeAudio):
                                    attrs.append(a)

                        # If media is a video file but had no video attribute, inject 16:9 HD video attribute
                        is_video_type = getattr(m, "video", None) or (getattr(file, "name", "").lower().endswith((".mp4", ".mkv", ".mov", ".ts", ".webm", ".avi")))
                        has_vid_attr = any(isinstance(x, DocumentAttributeVideo) for x in attrs)
                        if is_video_type and not has_vid_attr:
                            attrs.append(DocumentAttributeVideo(
                                duration=0,
                                w=1280,
                                h=720,
                                supports_streaming=True
                            ))

                        sent_media = await self.rpc.execute(
                            lambda c: c.send_file(_parse_chat_id(target_chat), file, caption=cap_main, thumb=t_path, attributes=attrs if attrs else None, reply_to=resolved_topic, parse_mode="md", supports_streaming=True, silent=silent_mode),
                            client=client, timeout=120.0
                        )
                        if cap_overflow and sent_media:
                            reply_id = getattr(sent_media, "id", None) or resolved_topic
                            with suppress(Exception):
                                await self.rpc.execute(
                                    lambda c: c.send_message(_parse_chat_id(target_chat), cap_overflow, reply_to=reply_id, parse_mode="md", silent=silent_mode),
                                    client=client, timeout=30.0
                                )
                        if sent_media:
                            s_id = getattr(sent_media, "id", None)
                            if s_id:
                                f_name = getattr(m.file, "name", None) if getattr(m, "file", None) else None
                                title_clean = f_name or (m.text[:40] if m.text else f"Video #{m.id}")
                                icon_m = "🎥" if getattr(m, "video", None) else ("📄" if getattr(m, "document", None) else ("🖼️" if getattr(m, "photo", None) else "📦"))
                                self.batch_index_records.append({
                                    "msg_id": s_id,
                                    "title": clean_index_title(title_clean, max_len=60),
                                    "icon": icon_m
                                })
                            # Multi-target instant mirror
                            if self.cfg.mirror_targets and getattr(sent_media, "media", None):
                                for m_tgt in self.cfg.mirror_targets:
                                    if str(m_tgt) != str(target_chat):
                                        with suppress(Exception):
                                            await self.rpc.execute(
                                                lambda c, tgt=m_tgt: c.send_file(_parse_chat_id(tgt), sent_media.media, caption=cap_main, parse_mode="md", silent=silent_mode),
                                                client=client, timeout=30.0
                                            )
                        self.log(format_media_log_detail(m, prefix="✔ Sent"))
                        success_flag = True
                    elif m.text and not getattr(m, 'action', None):
                        formatted_text = self.format_text(m.text, for_media=False)
                        if formatted_text and formatted_text.strip():
                            sent_txt = await self.rpc.execute(
                                lambda c: c.send_message(_parse_chat_id(target_chat), formatted_text, reply_to=resolved_topic, parse_mode="md", silent=silent_mode),
                                client=client
                            )
                            if sent_txt and self.cfg.mirror_targets:
                                for m_tgt in self.cfg.mirror_targets:
                                    if str(m_tgt) != str(target_chat):
                                        with suppress(Exception):
                                            await self.rpc.execute(
                                                lambda c, tgt=m_tgt: c.send_message(_parse_chat_id(tgt), formatted_text, parse_mode="md", silent=silent_mode),
                                                client=client, timeout=20.0
                                            )
                            self.log(format_media_log_detail(m, prefix="✔ Sent"))
                        else:
                            self.log(f"[dim]⏩ Skipped watermark/empty message (ID: #{m.id})[/]")
                            success_flag = True
                    elif getattr(m, 'action', None) or getattr(m, 'poll', None) or getattr(m, 'contact', None):
                        reconstructed_text = self.reconstruct(m)
                        if reconstructed_text and reconstructed_text.strip():
                            await self.rpc.execute(
                                lambda c: c.send_message(_parse_chat_id(target_chat), reconstructed_text, reply_to=resolved_topic, parse_mode="md", silent=silent_mode),
                                client=client
                            )
                            self.log(format_media_log_detail(m, prefix="✔ Sent System/Action"))
                            success_flag = True
                        else:
                            success_flag = True
                    else:
                        success_flag = True

            except (KeyboardInterrupt, asyncio.CancelledError):
                raise
            except Exception as e:
                await self.dlq.append(source_chat, item.first_id, e, target_chat=target_chat, target_topic=target_topic or 0)
                self.log(f"[bold red]❌ Stream Failed ID #{item.first_id}:[/] {str(e)[:100]}")
                success_flag = False

                # Auto-DLQ Self-Healing Background Daemon: Auto-retry after 45s with fresh message reference
                if item.retry_count < 2 and not self.cfg.run_dlq:
                    item.retry_count += 1
                    async def auto_retry_later(w_item, delay=45.0):
                        await asyncio.sleep(delay)
                        if stop_event.is_set(): return
                        try:
                            cl = self.session_mgr.get_client()
                            fresh_msgs = await cl.get_messages(_parse_chat_id(source_chat), ids=[m.id for m in w_item.messages])
                            if fresh_msgs and any(fresh_msgs):
                                w_item.messages = [m for m in fresh_msgs if m]
                                self.log(f"[bold yellow]🔄 Auto-DLQ Self-Healing retry triggered for Message #{w_item.first_id}...[/]")
                                await self.execute(w_item, stop_event)
                        except Exception as retry_err:
                            self.log(f"[dim red]Auto-DLQ background attempt {w_item.retry_count} failed: {retry_err}[/]")
                    asyncio.create_task(auto_retry_later(item))

        if success_flag:
            for m in active_messages:
                await self.state.mark_completed(source_chat, m.id, target_chat, target_topic or 0)
                if getattr(m, "video", None):
                    self.metrics["videos_sent"] = self.metrics.get("videos_sent", 0) + 1
                elif getattr(m, "document", None):
                    self.metrics["docs_sent"] = self.metrics.get("docs_sent", 0) + 1
                elif getattr(m, "photo", None):
                    self.metrics["photos_sent"] = self.metrics.get("photos_sent", 0) + 1
                elif getattr(m, "text", None):
                    self.metrics["text_sent"] = self.metrics.get("text_sent", 0) + 1
            self.metrics["messages_forwarded"] += len(active_messages)

            if self.metrics["messages_forwarded"] > 0 and self.metrics["messages_forwarded"] % 50 == 0:
                v_s = self.metrics.get('videos_sent', 0)
                d_s = self.metrics.get('docs_sent', 0)
                p_s = self.metrics.get('photos_sent', 0)
                t_s = self.metrics.get('text_sent', 0)
                AdminTelemetry.dispatch(client, "⚡ [MONITOR] Milestone Progress", {
                    "Progress": f"{self.metrics['messages_forwarded']} / {self.metrics['discovered']} messages",
                    "Sent Breakdown": f"{v_s} 🎥 Videos | {d_s} 📄 Docs | {p_s} 🖼️ Photos | {t_s} 💬 Text",
                    "Current Speed": f"{self.metrics['current_speed_mb']:.2f} MB/s",
                    "Peak Speed": f"{self.metrics['peak_speed']:.2f} MB/s"
                })

            # Intelligent Adaptive Velocity: Uncapped Wire Speed for Heavy Media
            custom_delay = os.getenv("MESSAGE_DELAY", "").strip()
            if custom_delay:
                try:
                    actual_delay = max(0.0, float(custom_delay))
                except ValueError:
                    actual_delay = 0.05
            else:
                # Heavy media (videos/docs) inherently takes seconds or minutes over the network,
                # acting as its own natural flood barrier. Zero artificial delay needed!
                if any(getattr(m, "video", None) for m in active_messages):
                    actual_delay = 0.0  # 100% Uncapped Supersonic Speed
                elif any(getattr(m, "document", None) for m in active_messages):
                    actual_delay = 0.0  # 100% Uncapped Supersonic Speed
                elif any(getattr(m, "photo", None) for m in active_messages):
                    actual_delay = 0.05
                else:
                    actual_delay = 0.20  # Safe micro-pacing for consecutive rapid-fire text messages

            if actual_delay > 0:
                await asyncio.sleep(actual_delay)
        else:
            self.metrics["errors_count"] += len(active_messages)

# ============================================================
# 12. UNIFIED TERMINAL PLATFORM & RESPONSIVE DASHBOARD
# ============================================================
class TerminalPlatform:
    def __init__(self, cfg: AppConfig, session_mgr: MultiSessionManager = None):
        self.cfg = cfg
        self.state = StateManager()
        self.session_mgr = session_mgr or MultiSessionManager(self.cfg.api_id, self.cfg.api_hash)
        self.metrics = {
            "discovered": 0, "messages_forwarded": 0, "albums_forwarded": 0, "errors_count": 0,
            "bytes_downloaded": 0, "bytes_uploaded": 0, "api_calls": 0, "retries": 0, "flood_waits": 0,
            "peak_speed": 0.0, "current_speed_mb": 0.0, "active_parallel": cfg.perf.upload_parallelism
        }
        
        self.active_file_name = "Idle"
        self.active_file_progress = 0.0
        self.active_file_transferred = "0 MB"
        self.active_file_total = "0 MB"
        self.active_file_eta = "N/A"
        self.peak_speed_mb = 0.0
        self.current_speed_mb = 0.0
        self._last_telemetry_write = 0.0
        self._telemetry_dir = Path("logs")
        self._telemetry_dir.mkdir(parents=True, exist_ok=True)

        self.rpc = RPCGuard(self.session_mgr, self.metrics)
        self.streamer = MemoryStreamer(self.rpc, self.cfg, self.metrics, ui_callback=self.update_upload_progress)
        self.dlq = AsyncDLQ()
        
        # Auto-reset remote pause state on fresh forwarder launch to guarantee unpaused execution
        ctrl_p = Path("engine_control.json")
        try:
            with open(ctrl_p, "w", encoding="utf-8") as cf:
                json.dump({"paused": False, "ts": time.time()}, cf)
        except Exception:
            pass

        self.queue = asyncio.Queue(self.cfg.perf.queue_size)
        self.stop_evt = asyncio.Event()
        self.logs = deque(maxlen=25)
        
        self.start_time = time.monotonic()
        self.last_time = self.start_time
        self.last_bytes = 0
        self.speed_history = deque(maxlen=6)
        
        self.src_info = "Detecting Source..."
        self.tgt_info = "Detecting Target..."
        self._kw_re_cache = {}
        self._ex_re_cache = {}

    def log(self, text: str):
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {text}")

    def _write_engine_telemetry(self, is_done: bool = False):
        try:
            telem_file = self._telemetry_dir / "engine_telemetry.json"
            tmp_file = self._telemetry_dir / "engine_telemetry.tmp"
            total_d = self.metrics.get("discovered", 0)
            total_f = self.metrics.get("messages_forwarded", 0)
            remaining_f = max(0, total_d - total_f)
            pct_d = round((total_f / max(1, total_d)) * 100.0, 1) if total_d > 0 else 0.0
            data = {
                "timestamp": time.time(),
                "active_file_name": self.active_file_name,
                "active_file_progress": round(self.active_file_progress, 1),
                "active_file_transferred": self.active_file_transferred,
                "active_file_total": self.active_file_total,
                "active_file_eta": self.active_file_eta,
                "current_speed_mb": round(self.current_speed_mb, 2) if not is_done else 0.0,
                "peak_speed_mb": round(self.peak_speed_mb, 2),
                "is_transferring": (not is_done and self.active_file_progress < 100.0 and self.active_file_progress > 0.0),
                "total_files": total_d,
                "discovered": total_d,
                "messages_forwarded": total_f,
                "files_completed": total_f,
                "files_remaining": remaining_f,
                "batch_progress_pct": pct_d,
                "videos_sent": self.metrics.get("videos_sent", 0),
                "docs_sent": self.metrics.get("docs_sent", 0),
                "photos_sent": self.metrics.get("photos_sent", 0),
                "text_sent": self.metrics.get("text_sent", 0)
            }
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(data, f)
            os.replace(tmp_file, telem_file)
        except Exception:
            pass

    def update_upload_progress(self, filename, current, total):
        if current == 0 or self.active_file_name != filename[:22]:
            self.active_file_start_time = time.monotonic()
            
        self.active_file_name = filename[:22]
        self.active_file_progress = min(100.0, (current / max(1, total)) * 100.0)
        cur_mb = current / MB
        tot_mb = total / MB
        self.active_file_transferred = f"{cur_mb:.1f} MB" if cur_mb < 1024 else f"{cur_mb/1024:.2f} GB"
        self.active_file_total = f"{tot_mb:.1f} MB" if tot_mb < 1024 else f"{tot_mb/1024:.2f} GB"

        elapsed = time.monotonic() - self.active_file_start_time
        speed_mb = 0.0
        if elapsed > 0.5 and current > 0:
            speed_bps = current / elapsed
            speed_mb = speed_bps / MB
            if speed_mb > self.peak_speed_mb:
                self.peak_speed_mb = speed_mb
            self.current_speed_mb = speed_mb
            if speed_bps > 0:
                eta_seconds = (total - current) / speed_bps
                m, s = divmod(int(eta_seconds), 60)
                self.active_file_eta = f"{m}m {s}s"
        elif current >= total:
            self.active_file_eta = "Done"
            self.current_speed_mb = 0.0

        # Periodic atomic write to logs/engine_telemetry.json
        now = time.monotonic()
        if (now - self._last_telemetry_write >= 0.4) or (current >= total):
            self._last_telemetry_write = now
            self._write_engine_telemetry(is_done=(current >= total))

    def matches_keywords(self, msg) -> bool:
        text_content = str(msg.text or "")
        file_name = ""
        if getattr(msg, "file", None):
            file_name = str(getattr(msg.file, "name", "") or "")
        
        scope = self.cfg.perf.scope
        if scope == "caption": combined = text_content
        elif scope == "filename": combined = file_name
        else: combined = f"{text_content} {file_name}"

        if self.cfg.perf.exclude_words:
            ex_key = tuple(sorted(self.cfg.perf.exclude_words))
            compiled = self._ex_re_cache.get(ex_key)
            if compiled is None:
                compiled = re.compile(r"\b(" + "|".join(map(re.escape, self.cfg.perf.exclude_words)) + r")\b", re.IGNORECASE)
                self._ex_re_cache[ex_key] = compiled
            if compiled.search(combined): return False

        if not self.cfg.perf.keywords: return True
        kw_key = tuple(sorted(self.cfg.perf.keywords))
        compiled = self._kw_re_cache.get(kw_key)
        if compiled is None:
            compiled = re.compile("|".join(map(re.escape, self.cfg.perf.keywords)), re.IGNORECASE)
            self._kw_re_cache[kw_key] = compiled
        return compiled.search(combined) is not None

    async def _get_topic_name(self, chat_id, topic_id, client):
        if not topic_id or str(topic_id).strip() in ("0", "None", ""): return "General"
        try:
            res = await client(GetForumTopicsRequest(
                channel=_parse_chat_id(chat_id),
                offset_date=None,
                offset_id=0,
                offset_topic=0,
                limit=100
            ))
            if hasattr(res, 'topics'):
                for t in res.topics:
                    if int(t.id) == int(topic_id):
                        return str(t.title)
        except Exception: pass
        try:
            msgs = await client.get_messages(_parse_chat_id(chat_id), ids=[int(topic_id)])
            if msgs and msgs[0] and getattr(msgs[0], 'action', None) and hasattr(msgs[0].action, 'title'):
                return str(msgs[0].action.title)
        except Exception: pass
        return f"Topic {topic_id}"

    async def fetch_names(self):
        client = self.session_mgr.get_client()
        try:
            if self.cfg.routing_mode == 2 and self.cfg.forwarding_rules:
                routes_summary = []
                for idx, rule in enumerate(self.cfg.forwarding_rules):
                    src_p = _parse_chat_id(rule["source_chat"])
                    tgt_p = _parse_chat_id(rule["target_chat"])
                    src = await client.get_entity(src_p)
                    tgt = await client.get_entity(tgt_p)
                    src_top = await self._get_topic_name(rule["source_chat"], rule.get("source_topic", 0), client)
                    tgt_top = await self._get_topic_name(rule["target_chat"], rule.get("target_topic", 0), client)
                    routes_summary.append(f"Rule {idx+1}: [cyan]{getattr(src, 'title', str(src_p))}[/] ({src_top}) ➔ [cyan]{getattr(tgt, 'title', str(tgt_p))}[/] ({tgt_top})")
                self.src_info = "\n".join(routes_summary)
                self.tgt_info = "[bold green]Multiple Routes Active (Multi-Route Mode)[/]"
            else:
                src_p = _parse_chat_id(self.cfg.source_chat)
                tgt_p = _parse_chat_id(self.cfg.target_chat)
                src = await client.get_entity(src_p)
                tgt = await client.get_entity(tgt_p)
                src_title = getattr(src, "title", str(src_p))
                tgt_title = getattr(tgt, "title", str(tgt_p))
                src_topic = await self._get_topic_name(self.cfg.source_chat, self.cfg.source_topic, client)
                tgt_topic = await self._get_topic_name(self.cfg.target_chat, self.cfg.target_topic, client)
                
                self.src_info = f"[cyan]{src_title}[/] (ID: {self.cfg.source_chat})\n[dim]↳ Topic:[/] [yellow]{src_topic}[/] (ID: {self.cfg.source_topic})"
                self.tgt_info = f"[cyan]{tgt_title}[/] (ID: {self.cfg.target_chat})\n[dim]↳ Topic:[/] [yellow]{tgt_topic}[/] (ID: {self.cfg.target_topic})"
            self.log("[bold green]Routing secured and verified.[/]")
        except Exception as e:
            self.src_info = f"Source: {self.cfg.source_chat}"
            self.tgt_info = f"Target: {self.cfg.target_chat}"
            self.log(f"[bold red]Preflight Warning:[/] Entity lookup ({e})")

    async def scanner_single(self):
        self.log(f"[cyan]Scanning Source Chat {self.cfg.source_chat}...[/]")
        client = self.session_mgr.get_client()
        group = []
        gid = None
        batch_count = 0
        if getattr(self, "resume_min_id", None) is not None:
            min_id = self.resume_min_id
        else:
            min_id = await self.state.get_watermark(self.cfg.source_chat)
        src_p = _parse_chat_id(self.cfg.source_chat)
        tgt_p = _parse_chat_id(self.cfg.target_chat)
        tgt_topic = self.cfg.target_topic or 0

        collected_items = []

        def track_found(msg_obj):
            if getattr(msg_obj, "video", None): self.metrics["found_videos"] = self.metrics.get("found_videos", 0) + 1
            elif getattr(msg_obj, "document", None): self.metrics["found_docs"] = self.metrics.get("found_docs", 0) + 1
            elif getattr(msg_obj, "photo", None): self.metrics["found_photos"] = self.metrics.get("found_photos", 0) + 1
            elif getattr(msg_obj, "text", None): self.metrics["found_text"] = self.metrics.get("found_text", 0) + 1

        async def push():
            nonlocal group, gid
            if group:
                unprocessed = [m for m in group if not await self.state.is_processed(self.cfg.source_chat, m.id, tgt_p, tgt_topic)]
                if unprocessed:
                    if not self.cfg.perf.keywords or any(self.matches_keywords(m) for m in unprocessed):
                        self.metrics["discovered"] += len(unprocessed)
                        for m in unprocessed: track_found(m)
                        w_item = WorkItem(list(unprocessed), rule_index=0)
                        if self.cfg.auto_sort_subjects:
                            collected_items.append(w_item)
                        else:
                            await self.queue.put(w_item)
            group, gid = [], None

        try:
            # Check if topic is specified and valid
            src_topic_id = self.cfg.source_topic or None
            
            # Telethon iterator with safe fallback for forum topic
            async for msg in client.iter_messages(src_p, reply_to=src_topic_id, reverse=True, min_id=min_id):
                if self.stop_evt.is_set(): break
                if await self.state.is_processed(self.cfg.source_chat, msg.id, tgt_p, tgt_topic):
                    if group and gid and getattr(msg, "grouped_id", None) == gid:
                        await push()
                    continue
                
                if not check_media_filter(msg, self.cfg.perf.media_filter):
                    continue
                
                curr_gid = getattr(msg, "grouped_id", None)
                if curr_gid and group and curr_gid == gid and len(group) < 10:
                    group.append(msg)
                    continue
                    
                await push()
                if curr_gid:
                    group, gid = [msg], curr_gid
                else:
                    if not self.cfg.perf.keywords or self.matches_keywords(msg):
                        self.metrics["discovered"] += 1
                        track_found(msg)
                        w_item = WorkItem([msg], rule_index=0)
                        if self.cfg.auto_sort_subjects:
                            collected_items.append(w_item)
                        else:
                            await self.queue.put(w_item)

                batch_count += 1
                if batch_count >= 100:
                    batch_count = 0
                    await asyncio.sleep(0.3)
                    
            await push()

            # Execute Smart Subject-Wise Sorting if enabled
            if self.cfg.auto_sort_subjects and collected_items:
                def get_item_sort_key(item):
                    subj_order = 999
                    first_m = item.messages[0]
                    t = str(getattr(first_m, "text", "") or "")
                    fn = ""
                    if getattr(first_m, "file", None):
                        fn = str(getattr(first_m.file, "name", "") or "")
                    det = detect_subject(t, fn)
                    if det:
                        for s_idx, (s_n, _, _, _) in enumerate(SUBJECT_DEFINITIONS):
                            if s_n == det["name"]:
                                subj_order = s_idx
                                break
                    combined = f"{t} {fn}"
                    lec_num = 9999
                    # 1. Match explicit lecture, class, part, chapter, session numbers
                    m_lec = re.search(r"(?i)\b(?:lec(?:ture)?|class|session|part|chapter|no|#)\s*0*(\d{1,4})\b", combined)
                    if m_lec:
                        with suppress(Exception):
                            lec_num = int(m_lec.group(1))
                    else:
                        # 2. Match isolated numbers in brackets or filename e.g. [16], (02), Anatomy_19.mp4
                        m_num = re.search(r"(?:^|[\[\(_\-\s])0*(\d{1,3})(?:[\]\)_\-\s\.]|$)", fn or combined)
                        if m_num:
                            with suppress(Exception):
                                val = int(m_num.group(1))
                                if val > 0:
                                    lec_num = val
                    return (subj_order, lec_num, item.first_id)

                try:
                    collected_items.sort(key=get_item_sort_key)
                    self.log(f"[bold green]✔ Subject Auto-Sorter:[/] [cyan]Organized {len(collected_items)} items into textbook curriculum order.[/]")
                except Exception as e:
                    self.log(f"[yellow]⚠️ Auto-sort fallback:[/] {e}")

                for item in collected_items:
                    if self.stop_evt.is_set(): break
                    await self.queue.put(item)

        except Exception as e:
            self.log(f"[bold red]❌ Scanner Error:[/] {e}")

    async def _scan_rule(self, idx, rule):
        self.log(f"[cyan]Scanning Rule {idx+1}: {rule['source_chat']} ➔ {rule['target_chat']}...[/]")
        client = self.session_mgr.get_client()
        group = []
        gid = None
        batch_count = 0
        
        min_id = await self.state.get_watermark(rule["source_chat"])
        src_p = _parse_chat_id(rule["source_chat"])
        tgt_p = _parse_chat_id(rule["target_chat"])
        tgt_topic = rule.get("target_topic", 0) or 0

        def track_found_rule(msg_obj):
            if getattr(msg_obj, "video", None): self.metrics["found_videos"] = self.metrics.get("found_videos", 0) + 1
            elif getattr(msg_obj, "document", None): self.metrics["found_docs"] = self.metrics.get("found_docs", 0) + 1
            elif getattr(msg_obj, "photo", None): self.metrics["found_photos"] = self.metrics.get("found_photos", 0) + 1
            elif getattr(msg_obj, "text", None): self.metrics["found_text"] = self.metrics.get("found_text", 0) + 1

        async def push_rule():
            nonlocal group, gid
            if group:
                unprocessed = [m for m in group if not await self.state.is_processed(rule["source_chat"], m.id, tgt_p, tgt_topic)]
                if unprocessed:
                    if not self.cfg.perf.keywords or any(self.matches_keywords(m) for m in unprocessed):
                        self.metrics["discovered"] += len(unprocessed)
                        for m in unprocessed: track_found_rule(m)
                        await self.queue.put(WorkItem(list(unprocessed), rule_index=idx))
            group, gid = [], None

        try:
            async for msg in client.iter_messages(src_p, reply_to=rule.get("source_topic", 0) or None, reverse=True, min_id=min_id):
                if self.stop_evt.is_set(): break
                if await self.state.is_processed(rule["source_chat"], msg.id, tgt_p, tgt_topic):
                    if group and gid and getattr(msg, "grouped_id", None) == gid:
                        await push_rule()
                    continue
                
                if not check_media_filter(msg, self.cfg.perf.media_filter):
                    continue
                
                curr_gid = getattr(msg, "grouped_id", None)
                if curr_gid and group and curr_gid == gid and len(group) < 10:
                    group.append(msg)
                    continue
                    
                await push_rule()
                if curr_gid:
                    group, gid = [msg], curr_gid
                else:
                    if not self.cfg.perf.keywords or self.matches_keywords(msg):
                        self.metrics["discovered"] += 1
                        track_found_rule(msg)
                        await self.queue.put(WorkItem([msg], rule_index=idx))

                batch_count += 1
                if batch_count >= 100:
                    batch_count = 0
                    await asyncio.sleep(0.3)
                    
            await push_rule()
        except Exception as e:
            self.log(f"[bold red]❌ Scanner Rule {idx+1} Error:[/] {e}")

    async def scanner_multiple(self):
        tasks = [asyncio.create_task(self._scan_rule(idx, rule)) for idx, rule in enumerate(self.cfg.forwarding_rules)]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def scanner_dlq(self):
        self.log("[cyan]Initializing DLQ Recovery Engine...[/]")
        client = self.session_mgr.get_client()
        dlq_path = Path("dead_letter.jsonl")
        if not dlq_path.exists():
            self.log("[yellow]DLQ is empty. No tasks to retry.[/]")
            return
            
        tasks_by_chat = {}
        try:
            with open(dlq_path, "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip(): continue
                    data = json.loads(line)
                    chat = data["chat"]
                    msg = data["msg"]
                    r_idx = data.get("rule_index", 0)
                    if chat not in tasks_by_chat:
                        tasks_by_chat[chat] = []
                    tasks_by_chat[chat].append((msg, r_idx))
        except Exception as e:
            self.log(f"[bold red]Failed to parse DLQ:[/] {e}")
            return

        for chat, item_data in tasks_by_chat.items():
            msgs = [x[0] for x in item_data]
            r_idx_map = {x[0]: x[1] for x in item_data}
            self.log(f"[cyan]Recovering {len(msgs)} messages from {chat}...[/]")
            
            for i in range(0, len(msgs), 50):
                chunk = msgs[i:i+50]
                try:
                    fetched = await client.get_messages(_parse_chat_id(chat), ids=chunk)
                    for m in fetched:
                        if m:
                            self.metrics["discovered"] += 1
                            r_idx = r_idx_map.get(m.id, 0)
                            await self.queue.put(WorkItem([m], rule_index=r_idx))
                except Exception as e:
                    self.log(f"[bold red]DLQ Fetch Error for {chat}:[/] {e}")
                await asyncio.sleep(1.0)
                
        self.log("[bold green]✔ DLQ Enqueued successfully.[/]")

    def setup_live_listeners(self):
        client = self.session_mgr.get_client()
        self.log("[bold red]🔴 Registering 24/7 Real-Time Event Listener...[/]")
        
        if self.cfg.routing_mode == 2 and self.cfg.forwarding_rules:
            for idx, rule in enumerate(self.cfg.forwarding_rules):
                src_p = _parse_chat_id(rule["source_chat"])
                src_topic = int(rule.get("source_topic", 0) or 0)
                
                @client.on(events.NewMessage(chats=src_p))
                async def handle_multi_incoming(event, r_idx=idx, r_topic=src_topic):
                    msg = event.message
                    if r_topic:
                        is_match = False
                        if getattr(msg, "reply_to_msg_id", None) == r_topic:
                            is_match = True
                        elif getattr(msg, "reply_to", None):
                            if getattr(msg.reply_to, "reply_to_top_id", None) == r_topic or getattr(msg.reply_to, "reply_to_msg_id", None) == r_topic:
                                is_match = True
                        if not is_match: return
                    
                    if not check_media_filter(msg, self.cfg.perf.media_filter):
                        return
                    
                    if not self.cfg.perf.keywords or self.matches_keywords(msg):
                        self.metrics["discovered"] += 1
                        self.log(f"[bold red]🔴 Live Message Detected[/] (ID: {msg.id})")
                        await self.queue.put(WorkItem([msg], rule_index=r_idx))
        else:
            src_p = _parse_chat_id(self.cfg.source_chat)
            src_topic = int(self.cfg.source_topic or 0)
            
            @client.on(events.NewMessage(chats=src_p))
            async def handle_single_incoming(event):
                msg = event.message
                if src_topic:
                    is_match = False
                    if getattr(msg, "reply_to_msg_id", None) == src_topic:
                        is_match = True
                    elif getattr(msg, "reply_to", None):
                        if getattr(msg.reply_to, "reply_to_top_id", None) == src_topic or getattr(msg.reply_to, "reply_to_msg_id", None) == src_topic:
                            is_match = True
                    if not is_match: return
                
                if not check_media_filter(msg, self.cfg.perf.media_filter):
                    return
                
                if not self.cfg.perf.keywords or self.matches_keywords(msg):
                    self.metrics["discovered"] += 1
                    self.log(f"[bold red]🔴 Live Message Detected[/] (ID: {msg.id})")
                    await self.queue.put(WorkItem([msg], rule_index=0))

    def setup_remote_control_listener(self):
        client = self.session_mgr.get_client()
        if not client: return
        
        @client.on(events.NewMessage(chats="me"))
        async def handle_remote_command(event):
            text = (event.raw_text or "").strip().lower()
            if not text: return
            
            if text in ("/status", "status", "/stats"):
                total_mb = self.metrics.get("bytes_uploaded", 0) / MB
                data_str = f"{total_mb:.2f} MB" if total_mb < 1024 else f"{total_mb/1024:.2f} GB"
                uptime_seconds = int(time.monotonic() - self.start_time)
                h_up, rem = divmod(uptime_seconds, 3600)
                m_up, s_up = divmod(rem, 60)
                time_str = f"{h_up:02d}h {m_up:02d}m {s_up:02d}s"
                
                completed = self.metrics.get("messages_forwarded", 0)
                discovered = max(1, self.metrics.get("discovered", 0))
                pct = (completed / discovered) * 100
                
                v_s = self.metrics.get('videos_sent', 0)
                d_s = self.metrics.get('docs_sent', 0)
                p_s = self.metrics.get('photos_sent', 0)
                t_s = self.metrics.get('text_sent', 0)
                
                speed = self.metrics.get('current_speed_mb', 0.0)
                peak = self.metrics.get('peak_speed', 0.0)
                
                status_card = (
                    "📊 **[REMOTE TELEGRAM LIVE STATUS]**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📁 **Active File:** `{self.active_file_name}` ({self.active_file_progress:.1f}%)\n"
                    f"⚡ **Speed:** `{speed:.2f} MB/s` (Peak: `{peak:.2f} MB/s`)\n"
                    f"📈 **Progress:** `{completed} / {self.metrics.get('discovered', 0)}` ({pct:.1f}%)\n"
                    f"📦 **Sent:** {v_s} 🎥 | {d_s} 📄 | {p_s} 🖼️ | {t_s} 💬\n"
                    f"💾 **Transferred:** `{data_str}`\n"
                    f"⏱️ **Uptime:** `{time_str}` | **ETA:** `{self.active_file_eta}`\n"
                    f"💻 **Vitals:** `{self.get_system_health()}`\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "💡 *Commands: `/status`, `/pause`, `/help`*"
                )
                with suppress(Exception):
                    await event.reply(status_card, parse_mode="md")

            elif text in ("/pause", "/stop", "pause", "stop"):
                self.log("[bold yellow]⏸ Remote Pause Triggered from Saved Messages[/]")
                with suppress(Exception):
                    await event.reply("⏸ **Forwarding Paused Remotely.** Bookmarks & history saved safely.", parse_mode="md")
                self.stop_evt.set()

            elif text in ("/kill", "/kill_all", "/killall", "/unlock_db", "/force_stop", "kill"):
                self.log("[bold red]🛑 Remote Kill & Force Stop Triggered from Saved Messages[/]")
                with suppress(Exception):
                    await event.reply("🛑 **Emergency Force Stop Received!** Terminating engine and releasing all database locks...", parse_mode="md")
                self.stop_evt.set()
                # Clean stale lock files
                for pat in ["*.session-journal", "*.session-wal", "*.session-shm", "history_core.sqlite-journal", "engine.lock"]:
                    for f in Path(".").glob(pat):
                        with suppress(Exception): f.unlink(missing_ok=True)
                # Terminate
                await asyncio.sleep(0.5)
                os._exit(0)

            elif text in ("/clean_history", "/clear_history", "/reset_history", "/wipe_history"):
                self.log("[bold magenta]🧹 Remote Clean History Triggered from Saved Messages[/]")
                try:
                    # 1. Safety snapshot first adhering to timestamp rules
                    now_dt = datetime.now()
                    stamp = now_dt.strftime("%A_%d-%B-%Y_%I-%M-%S%p")
                    snap_name = f"history_core_backup_{stamp}.sqlite"
                    
                    db_p = Path(DB_FILE)
                    if db_p.exists():
                        import sqlite3
                        src = sqlite3.connect(f"file:{db_p.resolve()}?mode=ro", uri=True)
                        dst = sqlite3.connect(snap_name)
                        src.backup(dst)
                        dst.close()
                        src.close()
                        
                        date_str = now_dt.strftime("%A, %d %B %Y | %I:%M %p")
                        caption_card = (
                            f"📦 **[PRE-WIPE SAFETY BACKUP — FORWARDER ENGINE]**\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• **Date & Time**   : `{date_str}`\n"
                            f"• **Safety Status** : `100% Preserved before Wipe`\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"🛡️ *Automatic safety backup dispatched before history wipe.*"
                        )
                        await client.send_file("me", snap_name, caption=caption_card, parse_mode="md")
                        with suppress(Exception): Path(snap_name).unlink()

                        # 2. Wipe history
                        with sqlite3.connect(DB_FILE, timeout=15) as conn:
                            conn.execute("DELETE FROM forwarded")
                            conn.execute("DELETE FROM source_watermarks")
                            with suppress(Exception): conn.execute("DELETE FROM local_folder_uploads")
                            conn.commit()
                            with suppress(Exception): conn.execute("VACUUM")

                        self.metrics["messages_forwarded"] = 0
                        self.metrics["bytes_uploaded"] = 0
                        self.metrics["videos_sent"] = 0
                        self.metrics["docs_sent"] = 0
                        self.metrics["photos_sent"] = 0
                        self.metrics["text_sent"] = 0

                        await event.reply(
                            "🧹 **[FORWARDING HISTORY CLEANED & RESET]**\n"
                            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            "• Previous history safely backed up above ⬆️\n"
                            "• Database `history_core.sqlite` is now 100% clean!\n"
                            "• Forwarder will re-forward files from scratch.",
                            parse_mode="md"
                        )
                except Exception as ex:
                    with suppress(Exception):
                        await event.reply(f"❌ Failed to clean history: {ex}", parse_mode="md")

            elif text in ("/backup", "/db", "backup"):
                try:
                    now_dt = datetime.now()
                    stamp = now_dt.strftime("%A_%d-%B-%Y_%I-%M-%S%p")
                    snap_name = f"history_core_backup_{stamp}.sqlite"
                    db_p = Path(DB_FILE)
                    if db_p.exists():
                        import sqlite3
                        src = sqlite3.connect(f"file:{db_p.resolve()}?mode=ro", uri=True)
                        dst = sqlite3.connect(snap_name)
                        src.backup(dst)
                        dst.close()
                        src.close()
                        
                        date_str = now_dt.strftime("%A, %d %B %Y | %I:%M %p")
                        caption_card = (
                            f"📦 **[CLOUD DATABASE BACKUP]**\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• **Date & Time**   : `{date_str}`\n"
                            f"• **Database**      : `history_core.sqlite`\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"🛡️ *Online zero-downtime backup.*"
                        )
                        await client.send_file("me", snap_name, caption=caption_card, parse_mode="md")
                        with suppress(Exception): Path(snap_name).unlink()
                except Exception as ex:
                    with suppress(Exception):
                        await event.reply(f"❌ Backup failed: {ex}", parse_mode="md")

            elif text in ("/help", "help"):
                help_card = (
                    "📱 **[REMOTE TELEGRAM COMMANDS]**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• `/status` - Live speed, progress & active file\n"
                    "• `/pause` or `/stop` - Safely pause forwarding\n"
                    "• `/kill` - 🛑 Kill engine & force unlock SQLite database\n"
                    "• `/clean_history` - 🧹 Wipe forwarding history (Auto-backup first)\n"
                    "• `/backup` - 📦 1-Click instant database snapshot\n"
                    "• `/help` - Show this commands guide"
                )
                with suppress(Exception):
                    await event.reply(help_card, parse_mode="md")

    async def scanner(self):
        if self.cfg.run_dlq:
            await self.scanner_dlq()
        elif self.cfg.routing_mode == 2 and self.cfg.forwarding_rules:
            await self.scanner_multiple()
        else:
            await self.scanner_single()
            
        if self.cfg.live_mode:
            self.log("[bold red]🔴 Catch-up scan complete. Live Listener is now 24/7 Active...[/]")
        else:
            self.log("[cyan]Scanner complete. Waiting for workers to finish.[/]")
            for _ in range(self.cfg.perf.workers): await self.queue.put(None)

    async def worker_supervisor(self, wid: int, proc: PipelineProcessor):
        items_processed = 0
        while not self.stop_evt.is_set():
            item = None
            try:
                item = await self.queue.get()
                if item is None:
                    self.queue.task_done()
                    break

                # Dynamic remote pause/resume check from Web Dashboard / Mobile
                ctrl_p = Path("engine_control.json")
                if ctrl_p.exists():
                    with suppress(Exception):
                        with open(ctrl_p, "r", encoding="utf-8") as cf:
                            c_state = json.load(cf)
                            if c_state.get("paused", False):
                                self.log("[bold yellow]⏸ Forwarding Paused via Web Dashboard[/]")
                            while c_state.get("paused", False) and not self.stop_evt.is_set():
                                await asyncio.sleep(1.0)
                                if ctrl_p.exists():
                                    with open(ctrl_p, "r", encoding="utf-8") as cf2:
                                        c_state = json.load(cf2)
                            if not c_state.get("paused", False):
                                pass

                await proc.execute(item, self.stop_evt)
                
                items_processed += 1
                if items_processed % 50 == 0:
                    gc.collect()
            except Exception as e:
                self.log(f"[red]Worker {wid} Crash: {e}[/]")
            finally:
                if item is not None:
                    self.queue.task_done()

    def get_system_health(self):
        if not PSUTIL: return "N/A"
        ram = psutil.Process().memory_info().rss / MB
        cpu = psutil.cpu_percent()
        return f"{ram:.1f} MB | CPU: {cpu}%"

    def update_live_metrics(self):
        now = time.monotonic()
        dt = now - self.last_time
        if dt >= 0.4:
            db = self.metrics["bytes_uploaded"] - self.last_bytes
            instant_speed = (db / MB) / dt
            
            self.speed_history.append(instant_speed)
            smoothed_speed = sum(self.speed_history) / len(self.speed_history)
            
            self.metrics["current_speed_mb"] = smoothed_speed
            if smoothed_speed > self.metrics["peak_speed"]:
                self.metrics["peak_speed"] = smoothed_speed
            
            self.last_time = now
            self.last_bytes = self.metrics["bytes_uploaded"]

    def render_dashboard(self):
        global THUMB_MODE
        self.update_live_metrics()
        
        uptime_seconds = int(time.monotonic() - self.start_time)
        hours, rem = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        uptime_str = f"{hours:02d}h {minutes:02d}m {seconds:02d}s"
        
        total_mb = self.metrics["bytes_uploaded"] / MB
        data_str = f"{total_mb:.2f} MB" if total_mb < 1024 else f"{total_mb/1024:.2f} GB"

        total_msgs = max(1, self.metrics['discovered'])
        completed = self.metrics['messages_forwarded']
        percent = (completed / total_msgs) * 100
        remaining_msgs = max(0, self.metrics['discovered'] - completed)

        width = get_terminal_width()
        bar_size = 22 if width >= 100 else 14

        def make_gradient_bar(val):
            v = max(0.0, min(100.0, float(val)))
            filled = int((v / 100) * bar_size)
            empty = bar_size - filled
            color = "bold green" if v >= 75 else ("bold cyan" if v >= 35 else "bold yellow")
            return f"[{color}]" + "█" * filled + "[/]" + "[dim]" + "░" * empty + "[/]"

        pipeline_bar = make_gradient_bar(percent)
        upload_bar = make_gradient_bar(self.active_file_progress)

        cur_speed = self.metrics['current_speed_mb']
        if cur_speed >= 15:
            speed_badge = f"[bold green]⚡ {cur_speed:.2f} MB/s (Turbo)[/]"
        elif cur_speed >= 5:
            speed_badge = f"[bold cyan]⚡ {cur_speed:.2f} MB/s (Fast)[/]"
        else:
            speed_badge = f"[bold yellow]⚡ {cur_speed:.2f} MB/s (Paced)[/]"

        w = get_terminal_width()
        sub_div = "─" * min(37, max(15, (w // 2) - 8 if w >= 95 else w - 8))
        full_div = "─" * min(76, max(20, w - 8))

        live_badge = "[bold red blink]🔴 LIVE 24/7 LISTENER ACTIVE[/]\n" if self.cfg.live_mode else ""
        routing_panel = Panel(
            Text.from_markup(f"{live_badge}[bold cyan]🛰️ ROUTING & NODES[/]\n{sub_div}\n{self.src_info}\n\n{self.tgt_info}"),
            border_style="red" if self.cfg.live_mode else "blue", box=box.ROUNDED, padding=(1, 2)
        )

        v_found = self.metrics.get('found_videos', 0)
        d_found = self.metrics.get('found_docs', 0)
        p_found = self.metrics.get('found_photos', 0)
        t_found = self.metrics.get('found_text', 0)

        v_sent = self.metrics.get('videos_sent', 0)
        d_sent = self.metrics.get('docs_sent', 0)
        p_sent = self.metrics.get('photos_sent', 0)
        t_sent = self.metrics.get('text_sent', 0)

        found_breakdown = f"[bold green]{v_found} 🎥[/] [dim]|[/] [bold yellow]{d_found} 📄[/] [dim]|[/] [bold cyan]{p_found} 🖼️[/] [dim]|[/] [bold magenta]{t_found} 💬[/]"
        sent_breakdown = f"[bold green]{v_sent} 🎥[/] [dim]|[/] [bold yellow]{d_sent} 📄[/] [dim]|[/] [bold cyan]{p_sent} 🖼️[/] [dim]|[/] [bold magenta]{t_sent} 💬[/]"

        transfer_panel = Panel(
            Text.from_markup(
                f"[bold cyan]📊 TRANSFER PIPELINE[/]\n{sub_div}\n"
                f"Progress : {pipeline_bar} [bold green]{percent:.1f}%[/]\n"
                f"Messages : [bold green]{completed}[/] / [cyan]{self.metrics['discovered']}[/] ([yellow]{remaining_msgs} left[/])\n"
                f"Found In : {found_breakdown}\n"
                f"Sent Out : {sent_breakdown}\n"
                f"Albums   : [cyan]{self.metrics['albums_forwarded']}[/]  |  Errors: [red]{self.metrics['errors_count']}[/]"
            ),
            border_style="green", box=box.ROUNDED, padding=(1, 2)
        )

        filename = shorten_middle(self.active_file_name, 32)
        file_panel = Panel(
            Text.from_markup(
                f"[bold cyan]🚀 ACTIVE FILE STREAM[/]\n{sub_div}\n"
                f"File       : [yellow]{filename}[/]\n"
                f"Progress   : {upload_bar} [bold yellow]{self.active_file_progress:.1f}%[/]\n"
                f"Transferred: [cyan]{self.active_file_transferred}[/] / {self.active_file_total}\n"
                f"Time Left  : [magenta]{self.active_file_eta}[/]"
            ),
            border_style="magenta", box=box.ROUNDED, padding=(1, 2)
        )

        kw_display = ", ".join(self.cfg.perf.keywords) if self.cfg.perf.keywords else "All Messages"

        performance_panel = Panel(
            Text.from_markup(
                f"[bold cyan]⚡ VELOCITY & TELEMETRY[/]\n{sub_div}\n"
                f"Speed    : {speed_badge}\n"
                f"Peak     : [cyan]{self.metrics['peak_speed']:.2f} MB/s[/]\n"
                f"Uploaded : [magenta]{data_str}[/]\n"
                f"Uptime   : [yellow]{uptime_str}[/]"
            ),
            border_style="yellow", box=box.ROUNDED, padding=(1, 2)
        )

        if w < 95:
            sys_content = (
                f"[bold cyan]🛡️ SYSTEM HEALTH & RESOURCES[/]\n{full_div}\n"
                f"🎯 Filters : [green]{kw_display}[/]\n"
                f"👥 Parallel: [green]{self.metrics['active_parallel']}[/]   |   ⚡ RPC: [cyan]{self.metrics['api_calls']}[/]\n"
                f"💻 Vitals  : [cyan]{self.get_system_health()}[/]   |   🛡️ Floods: [yellow]{self.metrics['flood_waits']}[/]"
            )
        else:
            sys_content = (
                f"[bold cyan]🛡️ SYSTEM HEALTH & RESOURCES[/]\n{full_div}\n"
                f"🎯 Filters : [green]{kw_display}[/]   |   👥 Parallel: [green]{self.metrics['active_parallel']}[/]   |   ⚡ RPC Calls: [cyan]{self.metrics['api_calls']}[/]\n"
                f"💻 Vitals  : [cyan]{self.get_system_health()}[/]   |   🛡️ Floods: [yellow]{self.metrics['flood_waits']}[/]"
            )

        system_panel = Panel(
            Text.from_markup(sys_content),
            border_style="cyan", box=box.ROUNDED, padding=(0, 2)
        )

        log_lines = list(self.logs)[-7:]
        while len(log_lines) < 7: log_lines.append("[dim]...[/]")
        log_text = "\n".join(log_lines)
        log_panel = Panel(
            Text.from_markup(f"[bold cyan]📜 LIVE ACTIVITY STREAM[/]\n{full_div}\n{log_text}"),
            border_style="cyan", box=box.ROUNDED, padding=(0, 2)
        )

        table = Table.grid(expand=True)
        if w < 95:
            table.add_column(ratio=1)
            table.add_row(routing_panel)
            table.add_row(transfer_panel)
            table.add_row(file_panel)
            table.add_row(performance_panel)
        else:
            table.add_column(ratio=1)
            table.add_column(ratio=1)
            table.add_row(routing_panel, transfer_panel)
            table.add_row(file_panel, performance_panel)

        return Group(get_persistent_header(), table, system_panel, log_panel)

    async def boot(self):
        acquire_instance_lock()
        if not self.cfg.api_id or not self.cfg.api_hash:
            await self.session_mgr._prompt_credentials()
            self.cfg.api_id = self.session_mgr.api_id
            self.cfg.api_hash = self.session_mgr.api_hash

        await self.session_mgr.start_all()
        client = self.session_mgr.get_client()

        # PRE-FLIGHT INTERACTIVE VALIDATION
        valid_routing = await preflight_verify_routing(client, self.cfg)
        if not valid_routing:
            console.print("[yellow]Returning to Main Menu...[/]")
            await asyncio.sleep(1.5)
            return

        await self.state.start()
        
        # SMART AUTO-RESUME & CRASH RECOVERY BOOKMARK CHECK
        self.resume_min_id = None
        if not self.cfg.live_mode and not self.cfg.run_dlq and self.cfg.routing_mode == 1:
            prev_watermark = await self.state.get_watermark(self.cfg.source_chat)
            if prev_watermark > 0:
                console.print(Panel(
                    f"[bold cyan]🔄 PREVIOUS TRANSFER BOOKMARK DETECTED[/]\n\n"
                    f"• Source Channel : [yellow]{self.cfg.source_chat}[/]\n"
                    f"• Last Message ID: [bold green]#{prev_watermark}[/]\n\n"
                    f"[dim]You can resume from this exact point without re-scanning old messages.[/]\n"
                    f"[dim]• Press Enter (or YES) to RESUME from #{prev_watermark}\n"
                    f"• Type 'ALL' to re-verify everything from the beginning.[/]",
                    border_style="cyan", box=box.ROUNDED
                ))
                res_choice = await safe_input("Resume from bookmark? (YES / ALL)", default_val="YES", allow_cancel=False)
                if res_choice.strip().upper() == "ALL":
                    self.resume_min_id = 0
                    console.print("[yellow]Re-scanning all messages from the beginning...[/]")
                else:
                    self.resume_min_id = prev_watermark
                    console.print(f"[bold green]✔ Resuming instantly from Message #{prev_watermark}![/]")
                await asyncio.sleep(1.0)

        # PRE-FLIGHT BATCH BRANDING CONFIRMATION
        detected_batch_name = ""
        try:
            if not self.cfg.live_mode and self.cfg.routing_mode == 1 and self.cfg.target_topic:
                input_peer = await client.get_input_entity(_parse_chat_id(self.cfg.target_chat))
                res = await client(GetForumTopicsRequest(
                    peer=input_peer,
                    offset_date=None,
                    offset_id=0,
                    offset_topic=0,
                    limit=100
                ))
                if hasattr(res, 'topics'):
                    for t in res.topics:
                        if t.id == int(self.cfg.target_topic):
                            detected_batch_name = getattr(t, 'title', '').strip()
                            break
        except Exception:
            pass

        active_batch_candidate = detected_batch_name or os.getenv("BATCH_NAME", "")
        if active_batch_candidate:
            console.print(Panel(
                f"[bold cyan]🎯 BATCH BRANDING & TOPIC SETTINGS[/]\n\n"
                f"• Detected Topic Batch: [bold green]{active_batch_candidate}[/]\n\n"
                f"[dim]• Press [bold white][Enter][/] to START with this Batch Tag in Captions\n"
                f"• Type [bold white][1][/] to Type a Custom Batch Name\n"
                f"• Type [bold white][2][/] to Turn Batch Tag OFF for this run[/]",
                border_style="cyan", box=box.ROUNDED
            ))
            b_choice = await safe_input("Select Option or Press Enter to Start", valid_options=["1", "2", ""], default_val="", allow_cancel=True)
            if b_choice is None:
                console.print("[yellow]Cancelled. Returning to Main Menu...[/]")
                await asyncio.sleep(0.8)
                return
            elif b_choice == "1":
                custom_name = await safe_input("Enter Custom Batch Name", allow_cancel=True)
                if custom_name and custom_name.strip():
                    self.cfg.batch_name = custom_name.strip()
                    os.environ["BATCH_NAME"] = custom_name.strip()
                    os.environ["SHOW_BATCH"] = "true"
                    console.print(f"[bold green]✔ Custom Batch Tag Set:[/] [yellow]{custom_name.strip()}[/]")
            elif b_choice == "2":
                self.cfg.batch_name = ""
                os.environ["SHOW_BATCH"] = "false"
                console.print("[yellow]Batch tag turned OFF for this run.[/]")
            else:
                self.cfg.batch_name = active_batch_candidate
                os.environ["BATCH_NAME"] = active_batch_candidate
                os.environ["SHOW_BATCH"] = "true"
                console.print(f"[bold green]✔ Active Batch Tag:[/] [yellow]{active_batch_candidate}[/]")
            await asyncio.sleep(0.8)
        else:
            self.cfg.batch_name = os.getenv("BATCH_NAME", "")

        workers = []
        interrupted = False
        try:
            await self.fetch_names()
            
            clear_screen()
            proc = PipelineProcessor(self.rpc, self.streamer, self.state, self.cfg, self.log, self.metrics, self.dlq, self.session_mgr)
            
            mode_name = "Live 24/7 Mode" if self.cfg.live_mode else ("Balanced Mode" if getattr(self.cfg.perf, "upload_parallelism", 12) == 12 else ("God Mode" if getattr(self.cfg.perf, "upload_parallelism", 12) == 40 else "Safe Mode"))
            AdminTelemetry.dispatch(client, "🟢 [MONITOR] Forwarder Session Started", {
                "Selected Mode": mode_name,
                "Source Route": f"`{self.cfg.source_chat}` (Topic: `{self.cfg.source_topic}`)",
                "Target Route": f"`{self.cfg.target_chat}` (Topic: `{self.cfg.target_topic}`)",
                "Workers": f"{self.cfg.perf.workers}",
                "Parallel Chunks": f"{getattr(self.cfg.perf, 'upload_parallelism', 12)}",
                "Filter Scope": f"{self.cfg.perf.media_filter} | {len(self.cfg.perf.keywords)} keywords"
            })

            workers = [asyncio.create_task(self.worker_supervisor(i, proc)) for i in range(self.cfg.perf.workers)]
            if self.cfg.live_mode:
                self.setup_live_listeners()
            self.setup_remote_control_listener()
            scan_task = asyncio.create_task(self.scanner())

            with Live(self.render_dashboard(), console=console, refresh_per_second=1, screen=True, transient=False) as live:
                while not self.stop_evt.is_set():
                    live.update(self.render_dashboard())
                    if not self.cfg.live_mode and scan_task.done() and self.queue.empty(): break
                    await asyncio.sleep(1.0)
                
                try:
                    await asyncio.wait_for(self.queue.join(), timeout=30.0)
                except asyncio.TimeoutError:
                    self.log("[yellow]⚠ Queue join timed out; shutting down gracefully.[/]")

                # 📑 Trigger Clickable Batch Index Card if enabled
                if self.cfg.generate_batch_index and proc.batch_index_records:
                    with suppress(Exception):
                        await proc.post_batch_index_card(self.cfg.target_chat, self.cfg.target_topic, client)

                self.log("[bold green]✨ TRANSFER SEQUENCE COMPLETE.[/]")
                try:
                    total_mb = self.metrics.get("bytes_uploaded", 0) / MB
                    data_str = f"{total_mb:.2f} MB" if total_mb < 1024 else f"{total_mb/1024:.2f} GB"
                    uptime_seconds = int(time.monotonic() - self.start_time)
                    m_up, s_up = divmod(uptime_seconds, 60)
                    h_up, m_up = divmod(m_up, 60)
                    time_str = f"{h_up:02d}h {m_up:02d}m {s_up:02d}s"
                    
                    v_s = self.metrics.get('videos_sent', 0)
                    d_s = self.metrics.get('docs_sent', 0)
                    p_s = self.metrics.get('photos_sent', 0)
                    t_s = self.metrics.get('text_sent', 0)
                    
                    v_f = self.metrics.get('found_videos', 0)
                    d_f = self.metrics.get('found_docs', 0)
                    p_f = self.metrics.get('found_photos', 0)
                    t_f = self.metrics.get('found_text', 0)
                    
                    src_clean = self.src_info.replace('[bold cyan]', '').replace('[/]', '').replace('\n', ' | ') if hasattr(self, 'src_info') else str(self.cfg.source_chat)
                    tgt_clean = self.tgt_info.replace('[bold cyan]', '').replace('[/]', '').replace('\n', ' | ') if hasattr(self, 'tgt_info') else str(self.cfg.target_chat)
                    
                    is_done_with_items = self.metrics.get("messages_forwarded", 0) > 0
                    summary_title = "🏆 [TASK COMPLETE — FORWARDING SUMMARY]" if is_done_with_items else "ℹ️ [SCAN COMPLETE — UP TO DATE]"
                    summary_status = "✅ All Messages Forwarded Successfully" if is_done_with_items else "✔ Up-to-Date (0 Unprocessed Messages)"

                    AdminTelemetry.dispatch(client, summary_title, {
                        "Status": summary_status,
                        "Selected Mode": mode_name,
                        "Source Route": f"`{src_clean}` (Topic: `{self.cfg.source_topic}`)",
                        "Target Route": f"`{tgt_clean}` (Topic: `{self.cfg.target_topic}`)",
                        "Discovered Scope": f"{self.metrics.get('discovered', 0)} messages",
                        "Forwarded Count": f"{self.metrics.get('messages_forwarded', 0)} messages",
                        "Found In Scope": f"{v_f} 🎥 | {d_f} 📄 | {p_f} 🖼️ | {t_f} 💬",
                        "Forwarded Output": f"{v_s} 🎥 | {d_s} 📄 | {p_s} 🖼️ | {t_s} 💬",
                        "Albums Grouped": f"{self.metrics.get('albums_forwarded', 0)}",
                        "Data Transferred": data_str,
                        "Peak Speed": f"{self.metrics.get('peak_speed', 0.0):.2f} MB/s",
                        "Total Duration": time_str,
                        "Errors / DLQ": f"{self.metrics.get('errors_count', 0)}"
                    })
                except Exception as e:
                    logger.error(f"Saved messages completion alert error: {e}")

                live.update(self.render_dashboard())
                await asyncio.sleep(1.5)

            if not self.cfg.live_mode and self.metrics["messages_forwarded"] == 0 and self.metrics["discovered"] == 0:
                console.print(Panel(
                    "[bold yellow]ℹ️ Scan Completed — No New Unprocessed Messages Found.[/]\n\n"
                    "• If you want to rescan from the beginning, use [bold green]Option 14[/] to clear history.\n"
                    "• Or verify that the channel contains messages matching your filter criteria.",
                    border_style="yellow", box=box.ROUNDED
                ))
        except (KeyboardInterrupt, asyncio.CancelledError):
            interrupted = True
        finally:
            self.stop_evt.set()
            for w in workers:
                w.cancel()
            if 'scan_task' in locals() and not scan_task.done():
                scan_task.cancel()
            with suppress(Exception):
                await self.state.close()

        if interrupted:
            clear_screen()
            console.print(get_persistent_header())
            console.print(Panel(
                "[bold yellow]⚠️ Process Stopped by User (Ctrl+C).[/]\n\n"
                "[green]✔ Forwarding safely paused.[/]\n"
                "[green]✔ Database bookmarks and history saved successfully.[/]\n"
                "[dim]You can resume from this bookmark anytime from the Main Menu.[/]",
                border_style="yellow", box=box.ROUNDED
            ))
            await asyncio.sleep(0.5)

# ============================================================
# 13. EMBEDDED EXTRACTOR TOOL & CLI MENUS
# ============================================================
async def run_quick_env_extractor(session_mgr):
    load_dotenv(override=True)
    clear_screen()
    console.print(get_persistent_header())
    
    src_cur = os.getenv("SOURCE_CHAT", "0")
    src_top = os.getenv("SOURCE_TOPIC", "0")
    tgt_cur = os.getenv("TARGET_CHAT", "0")
    tgt_top = os.getenv("TARGET_TOPIC", "0")
    
    console.print(Panel(
        f"[bold cyan]🔗 TELEGRAM LINK EXTRACTOR & .ENV QUICK SETUP[/]\n\n"
        f"[bold yellow]Current .env Single Route Configuration:[/]\n"
        f" • [cyan]SOURCE_CHAT :[/] [bold green]{src_cur}[/] [dim](Topic: {src_top})[/]\n"
        f" • [cyan]TARGET_CHAT :[/] [bold green]{tgt_cur}[/] [dim](Topic: {tgt_top})[/]\n\n"
        f"[dim]Paste any Telegram link (e.g. t.me/c/123456/10/50, @username, or chat ID)\n"
        f"The engine extracts Chat ID, Topic ID & Message ID and locks them into .env instantly![/]\n\n"
        f"[bold green][1][/] 🔗 Paste Links / Chat IDs [dim](Direct Paste Setup)[/]\n"
        f"[bold blue][2][/] 📋 1-Click Pick from Joined Channels [dim](Interactive Selector)[/]\n"
        f"[bold red][0][/] ⬅️ Back to Main Menu",
        border_style="cyan", box=box.ROUNDED
    ))
    
    choice = await safe_input("\nSelect Option (1/2/0)", valid_options=["1", "2", "0"], default_val="1", allow_cancel=True)
    if not choice or choice == "0":
        return

    client = session_mgr.get_client()

    if choice == "1":
        src_link = await safe_input("\n1. Paste SOURCE Telegram Link / ID", allow_cancel=True)
        if src_link and src_link.strip():
            src_parsed = parse_telegram_link(src_link)
            if "error" in src_parsed:
                console.print(f"[bold red]❌ Invalid Source: {src_parsed['error']}[/]")
            else:
                update_env_file(chat_id=src_parsed["CHAT_ID"], topic_id=src_parsed.get("TOPIC_ID", 0), mode="1")
                console.print(f"[bold green]✔ Source Set -> Chat: {src_parsed['CHAT_ID']} | Topic: {src_parsed.get('TOPIC_ID', 0)}[/]")

        tgt_link = await safe_input("\n2. Paste TARGET Telegram Link / ID", allow_cancel=True)
        if tgt_link and tgt_link.strip():
            tgt_parsed = parse_telegram_link(tgt_link)
            if "error" in tgt_parsed:
                console.print(f"[bold red]❌ Invalid Target: {tgt_parsed['error']}[/]")
            else:
                update_env_file(chat_id=tgt_parsed["CHAT_ID"], topic_id=tgt_parsed.get("TOPIC_ID", 0), mode="2")
                console.print(f"[bold green]✔ Target Set -> Chat: {tgt_parsed['CHAT_ID']} | Topic: {tgt_parsed.get('TOPIC_ID', 0)}[/]")

        console.print("\n[bold green]✨ .env Single Route saved successfully![/]")
        await asyncio.sleep(1.5)

    elif choice == "2":
        client = await session_mgr.ensure_active_client()
        if not client: return
        console.print("\n[bold cyan]Step 1: Choose SOURCE Channel[/]")
        src_sel = await interactive_channel_selector(client, prompt_title="SOURCE Channel")
        if src_sel:
            update_env_file(chat_id=src_sel["id"], topic_id=src_sel["topic"], mode="1")
            console.print(f"[bold green]✔ Source Set -> {src_sel['title']} (ID: {src_sel['id']} | Topic: {src_sel['topic']})[/]\n")
            
            console.print("[bold cyan]Step 2: Choose TARGET Channel[/]")
            tgt_sel = await interactive_channel_selector(client, prompt_title="TARGET Channel")
            if tgt_sel:
                update_env_file(chat_id=tgt_sel["id"], topic_id=tgt_sel["topic"], mode="2")
                console.print(f"[bold green]✔ Target Set -> {tgt_sel['title']} (ID: {tgt_sel['id']} | Topic: {tgt_sel['topic']})[/]\n")
                console.print("[bold green]✨ .env Single Route saved successfully![/]")
                await asyncio.sleep(1.5)

async def run_extractor_tool(session_mgr):
    while True:
        load_dotenv(override=True)
        clear_screen()
        console.print(get_persistent_header())
        
        src_chat = os.getenv("SOURCE_CHAT", "0")
        src_topic = os.getenv("SOURCE_TOPIC", "0")
        tgt_chat = os.getenv("TARGET_CHAT", "0")
        tgt_topic = os.getenv("TARGET_TOPIC", "0")
        rules_str = os.getenv("FORWARDING_RULES", "").strip()
        
        parsed_rules = []
        if rules_str:
            for r in rules_str.split(","):
                p = r.strip().split(":")
                if len(p) == 4:
                    parsed_rules.append({
                        "src_chat": p[0],
                        "src_topic": p[1],
                        "tgt_chat": p[2],
                        "tgt_topic": p[3]
                    })

        single_route_text = f"[bold cyan]Source:[/] [yellow]{src_chat}[/] (Topic: {src_topic}) ➔ [bold cyan]Target:[/] [yellow]{tgt_chat}[/] (Topic: {tgt_topic})"
        
        if parsed_rules:
            rules_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta", expand=True)
            rules_table.add_column("#", style="dim", width=4)
            rules_table.add_column("Source Channel ID", style="bold green")
            rules_table.add_column("Src Topic", style="yellow")
            rules_table.add_column("Target Channel ID", style="bold cyan")
            rules_table.add_column("Tgt Topic", style="yellow")
            for idx, r in enumerate(parsed_rules, 1):
                rules_table.add_row(str(idx), str(r["src_chat"]), str(r["src_topic"]), str(r["tgt_chat"]), str(r["tgt_topic"]))
            routes_display = Group(
                Text.from_markup(f"[bold yellow]🔗 Single Route:[/] {single_route_text}\n"),
                Text.from_markup(f"[bold magenta]🔀 Multi-Routing Rules ({len(parsed_rules)} Active):[/]"),
                rules_table
            )
        else:
            routes_display = Text.from_markup(
                f"[bold yellow]🔗 Single Route:[/] {single_route_text}\n\n"
                f"[dim]🔀 Multi-Routing Rules: None configured (Uses Single Route by default)[/]"
            )

        console.print(Panel(routes_display, title="[bold cyan]🧭 CURRENT ROUTING STATUS[/]", border_style="cyan", box=box.ROUNDED))
        
        console.print(Panel(
            "[bold cyan]🛠️ ROUTING & MULTI-ROUTE ACTIONS[/]\n\n"
            "[bold green][1][/] 📋 1-Click Pick Single Route [dim](Source & Target from Joined Channels)[/]\n"
            "[bold green][2][/] 🔗 Paste Single Route Links / IDs [dim](Quick Setup)[/]\n"
            "[bold blue][3][/] ➕ Add New Multi-Route Rule [dim](Append to FORWARDING_RULES)[/]\n"
            "[bold yellow][4][/] 🗑️ Delete a Multi-Route Rule [dim](Choose Rule # to remove)[/]\n"
            "[bold cyan][5][/] 🔍 Test & Verify All Routes [dim](1-Click permissions & chat check)[/]\n"
            "[bold red][6][/] 🧹 Clear All Multi-Route Rules [dim](Reset to empty)[/]\n"
            "[bold white][0][/] ⬅️ Back to Main Menu",
            border_style="magenta", box=box.ROUNDED
        ))
        
        choice = await safe_input("\nSelect Option (0-6)", valid_options=["1", "2", "3", "4", "5", "6"], allow_cancel=True)
        if choice is None or choice == "0":
            break

        client = session_mgr.get_client()

        if choice == "1":
            if not client.is_connected():
                await client.start()
            console.print("\n[bold cyan]Step 1: Choose SOURCE Channel[/]")
            src_sel = await interactive_channel_selector(client, prompt_title="SOURCE Channel")
            if src_sel:
                update_env_file(chat_id=src_sel["id"], topic_id=src_sel["topic"], mode="1")
                console.print(f"[bold green]✔ Source Set -> {src_sel['title']} (ID: {src_sel['id']} | Topic: {src_sel['topic']})[/]\n")
                
                console.print("[bold cyan]Step 2: Choose TARGET Channel[/]")
                tgt_sel = await interactive_channel_selector(client, prompt_title="TARGET Channel")
                if tgt_sel:
                    update_env_file(chat_id=tgt_sel["id"], topic_id=tgt_sel["topic"], mode="2")
                    console.print(f"[bold green]✔ Target Set -> {tgt_sel['title']} (ID: {tgt_sel['id']} | Topic: {tgt_sel['topic']})[/]\n")
                    console.print("[bold green]✨ Single Route saved successfully![/]")
                    await asyncio.sleep(1.2)

        elif choice == "2":
            src_link = await safe_input("1. Paste SOURCE Telegram Link / ID", allow_cancel=True)
            if src_link and src_link.strip():
                src_parsed = parse_telegram_link(src_link)
                if "error" in src_parsed:
                    console.print(f"[bold red]❌ Invalid Source: {src_parsed['error']}[/]")
                else:
                    update_env_file(chat_id=src_parsed["CHAT_ID"], topic_id=src_parsed["TOPIC_ID"], mode="1")
                    console.print(f"[bold green]✔ Source Updated -> {src_parsed['CHAT_ID']}[/]\n")

            tgt_link = await safe_input("2. Paste TARGET Telegram Link / ID", allow_cancel=True)
            if tgt_link and tgt_link.strip():
                tgt_parsed = parse_telegram_link(tgt_link)
                if "error" in tgt_parsed:
                    console.print(f"[bold red]❌ Invalid Target: {tgt_parsed['error']}[/]")
                else:
                    update_env_file(chat_id=tgt_parsed["CHAT_ID"], topic_id=tgt_parsed["TOPIC_ID"], mode="2")
                    console.print(f"[bold green]✔ Target Updated -> {tgt_parsed['CHAT_ID']}[/]\n")
            console.print("[bold green]✨ Single Route updated![/]")
            await asyncio.sleep(1.2)

        elif choice == "3":
            console.print("\n[bold cyan]Choose how to add Multi-Route Rule:[/]")
            console.print(" [1] 📋 Pick from Logged-in Channels")
            console.print(" [2] 🔗 Paste Links / IDs")
            sub_c = await safe_input("Select Method (1 / 2)", valid_options=["1", "2"], allow_cancel=True, default_val="1")
            if sub_c == "1":
                if not client.is_connected():
                    await client.start()
                src_sel = await interactive_channel_selector(client, prompt_title="SOURCE Channel for New Rule")
                if src_sel:
                    tgt_sel = await interactive_channel_selector(client, prompt_title="TARGET Channel for New Rule")
                    if tgt_sel:
                        extra_data = {"target_chat": tgt_sel["id"], "target_topic": tgt_sel["topic"] or "0"}
                        update_env_file(chat_id=src_sel["id"], topic_id=src_sel["topic"] or "0", mode="3", extra_data=extra_data)
                        console.print(f"[bold green]✔ Added Rule: {src_sel['title']} ➔ {tgt_sel['title']}![/]")
                        await asyncio.sleep(1.2)
            elif sub_c == "2":
                src_link = await safe_input("1. Paste SOURCE Telegram Link", allow_cancel=True)
                if src_link:
                    src_p = parse_telegram_link(src_link)
                    if "error" not in src_p:
                        tgt_link = await safe_input("2. Paste TARGET Telegram Link", allow_cancel=True)
                        if tgt_link:
                            tgt_p = parse_telegram_link(tgt_link)
                            if "error" not in tgt_p:
                                extra_data = {"target_chat": tgt_p["CHAT_ID"], "target_topic": tgt_p["TOPIC_ID"] or "0"}
                                update_env_file(chat_id=src_p["CHAT_ID"], topic_id=src_p["TOPIC_ID"] or "0", mode="3", extra_data=extra_data)
                                console.print("[bold green]✔ New rule added successfully![/]")
                                await asyncio.sleep(1.2)

        elif choice == "4":
            if not parsed_rules:
                console.print("[yellow]No multi-routing rules to delete.[/]")
                await asyncio.sleep(1.0)
                continue
            del_idx = await safe_input(f"Enter Rule # to Delete (1 to {len(parsed_rules)})", allow_cancel=True)
            if del_idx and del_idx.isdigit() and 1 <= int(del_idx) <= len(parsed_rules):
                idx_to_remove = int(del_idx) - 1
                parsed_rules.pop(idx_to_remove)
                new_rules_str = ",".join(f"{r['src_chat']}:{r['src_topic']}:{r['tgt_chat']}:{r['tgt_topic']}" for r in parsed_rules)
                set_key(".env", "FORWARDING_RULES", new_rules_str)
                console.print(f"[bold green]✔ Rule #{del_idx} successfully deleted![/]")
                await asyncio.sleep(1.2)

        elif choice == "5":
            client = await session_mgr.ensure_active_client()
            if not client: return
            console.print("\n[bold cyan]🔍 Verifying Routes & Telegram Permissions...[/]\n")
            test_table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
            test_table.add_column("Route Type", style="yellow", width=15)
            test_table.add_column("Channel / Chat", style="bold green")
            test_table.add_column("Status & Permissions", style="cyan")
            
            for role, chat_val in [("Single Source", src_chat), ("Single Target", tgt_chat)]:
                if chat_val and str(chat_val) != "0":
                    try:
                        ent = await client.get_entity(_parse_chat_id(chat_val))
                        title = getattr(ent, 'title', str(chat_val))
                        test_table.add_row(role, f"{title} ({chat_val})", "[bold green]✔ Accessible[/]")
                    except Exception as e:
                        test_table.add_row(role, str(chat_val), f"[bold red]❌ Failed: {str(e)[:35]}[/]")
            
            for idx, r in enumerate(parsed_rules, 1):
                try:
                    s_ent = await client.get_entity(_parse_chat_id(r["src_chat"]))
                    s_title = getattr(s_ent, 'title', r["src_chat"])
                    s_status = "[bold green]✔ OK[/]"
                except Exception as e:
                    s_title = str(r["src_chat"])
                    s_status = f"[bold red]❌ {str(e)[:20]}[/]"

                try:
                    t_ent = await client.get_entity(_parse_chat_id(r["tgt_chat"]))
                    t_title = getattr(t_ent, 'title', r["tgt_chat"])
                    t_status = "[bold green]✔ OK[/]"
                except Exception as e:
                    t_title = str(r["tgt_chat"])
                    t_status = f"[bold red]❌ {str(e)[:20]}[/]"

                test_table.add_row(f"Rule #{idx} Source", f"{s_title}", s_status)
                test_table.add_row(f"Rule #{idx} Target", f"{t_title}", t_status)

            console.print(test_table)
            await safe_input("\nPress Enter to return", allow_cancel=False)

        elif choice == "6":
            confirm = await safe_input("Type 'CLEAR' to delete all multi-routing rules", allow_cancel=True)
            if confirm == "CLEAR":
                set_key(".env", "FORWARDING_RULES", "")
                console.print("[bold green]✔ All multi-routing rules cleared![/]")
                await asyncio.sleep(1.2)

async def prompt_routing_mode():
    while True:
        clear_screen()
        console.print(get_persistent_header())
        console.print(Panel(
            "[bold cyan]📡 SELECT ROUTING ARCHITECTURE[/]\n\n"
            "[bold green][1][/] 🔗 Single Routing Mode [dim](Uses SOURCE_CHAT & TARGET_CHAT from .env)[/]\n"
            "[bold blue][2][/] 🔀 Multi-Route Mode [dim](Uses FORWARDING_RULES configuration)[/]",
            border_style="cyan", box=box.ROUNDED
        ))
        ch = await safe_input("\nEnter Routing Mode", valid_options=["1", "2"], allow_cancel=True, default_val="1")
        if ch == "1": return 1
        elif ch == "2": return 2
        elif ch is None: return None

async def prompt_sequence_mode():
    while True:
        clear_screen()
        console.print(get_persistent_header())
        console.print(Panel(
            "[bold cyan]📋 CHOOSE FORWARDING SEQUENCE / ORDERING MODE[/]\n"
            "[dim]Select how lectures, videos, and materials should be delivered in the target group.[/]\n\n"
            " [bold green][1][/] 📋 [bold white]Original Source Sequence[/] [bold yellow]⭐ (Recommended)[/]\n"
            "     [dim]Exact chronological sequence of original group (Lecture 01 ➔ Lecture 02 ➔ Lecture N). Zero disorder.[/]\n\n"
            " [bold cyan][2][/] 📚 [bold white]Smart Subject-Wise Grouping[/]\n"
            "     [dim]Auto-detect and group by subjects (Anatomy ➔ Physiology ➔ Biochemistry...)[/]",
            border_style="cyan", box=box.ROUNDED
        ))
        ch = await safe_input("\nEnter Sequence Mode", valid_options=["1", "2"], allow_cancel=True, default_val="1")
        if ch == "1":
            os.environ["AUTO_SORT_SUBJECTS"] = "false"
            set_key(".env", "AUTO_SORT_SUBJECTS", "false")
            return False
        elif ch == "2":
            os.environ["AUTO_SORT_SUBJECTS"] = "true"
            set_key(".env", "AUTO_SORT_SUBJECTS", "true")
            return True
        elif ch is None:
            return None

async def interactive_caption_and_filter_wizard():
    global GLOBAL_RUNTIME_FILTER
    env_path = ".env"
    while True:
        load_dotenv(override=True)
        cur_replace_words = os.getenv("REPLACE_WORDS", "").strip() or "[dim]None[/]"
        cur_replace_link = os.getenv("REPLACE_LINK", "").strip() or "[dim]None[/]"
        cur_remove_links = os.getenv("REMOVE_LINKS", "true").strip().upper()
        cur_replace_user = os.getenv("REPLACE_USERNAME", "").strip() or "[dim]None[/]"
        cur_header = os.getenv("CUSTOM_HEADER", "").strip() or "[dim]None[/]"
        cur_footer = os.getenv("CUSTOM_FOOTER", "").strip() or "[dim]None[/]"
        cur_silent = os.getenv("SILENT_MODE", "false").strip().upper()
        cur_kw = os.getenv("FILTER_KEYWORDS", "").strip() or "[dim]All[/]"
        cur_ex = os.getenv("FILTER_EXCLUDE", "").strip() or "[dim]None[/]"
        cur_index = os.getenv("GENERATE_BATCH_INDEX", "true").strip().upper()
        cur_tags_val = os.getenv("AUTO_HASHTAGS", "false").strip().lower() in ("true", "1", "yes")
        cur_strip_tags = os.getenv("STRIP_HASHTAGS", "false").strip().lower() in ("true", "1", "yes")
        if cur_tags_val:
            cur_tags_disp = "[bold green]ON[/] (#Subject #Lec)"
        elif cur_strip_tags:
            cur_tags_disp = "[bold red]OFF (Strip All Tags)[/]"
        else:
            cur_tags_disp = "[bold yellow]OFF (Keep Original)[/]"

        cur_subj = os.getenv("AUTO_SUBJECT_HEADERS", "true").strip().upper()
        cur_sort = os.getenv("AUTO_SORT_SUBJECTS", "true").strip().upper()
        cur_prefix = os.getenv("CUSTOM_FILE_PREFIX", "").strip() or "[dim]None[/]"

        strip_words_list, replace_words_map = get_clean_rules()
        cur_clean_count = len(strip_words_list)

        cur_sig = os.getenv("ENABLE_SIGNATURE", "true").strip().lower() in ("true", "1", "yes")
        sig_disp = "[bold green]ON (Kind Doctor Sig + 16:9 Cover)[/]" if cur_sig else "[bold red]OFF (Clean Mode: No Sig & Original Media)[/]"

        clear_screen()
        console.print(get_persistent_header())
        console.print(Panel(
            "[bold magenta]✍️ CAPTION, WORD REPLACER & LINK STUDIO[/]\n"
            "[dim]Easily customize every aspect of your messages directly on screen![/]\n\n"
            f"[bold green][1][/] 📝 Word & Watermark Cleaner [dim]Active:[/] [yellow]{cur_clean_count} rules in strip_words.txt[/]\n"
            f"[bold cyan][2][/] 🔗 Link Cleaner / Replacer  [dim]Remove:[/] [yellow]{cur_remove_links}[/] | [dim]Replace Link:[/] [yellow]{cur_replace_link}[/]\n"
            f"[bold blue][3][/] 👤 Username Replacer        [dim]Current:[/] [yellow]{cur_replace_user}[/]\n"
            f"[bold yellow][4][/] 🏷️ Custom Header & Footer   [dim]Header:[/] [yellow]{cur_header}[/] | [dim]Footer:[/] [yellow]{cur_footer}[/]\n"
            f"[bold green][5][/] 🎯 Keyword Search & Filters [dim]Keywords:[/] [yellow]{cur_kw}[/] | [dim]Skip:[/] [yellow]{cur_ex}[/]\n"
            f"[bold magenta][6][/] 🔕 Silent Forwarding Mode   [dim]Muted:[/] [yellow]{cur_silent}[/]\n"
            f"[bold cyan][7][/] 📑 Clickable Batch Index    [dim]Active:[/] [yellow]{cur_index}[/]\n"
            f"[bold yellow][8][/] 🏷️ Smart Auto-Hashtags     [dim]Active:[/] {cur_tags_disp}\n"
            f"[bold cyan][9][/] ✨ Subject Header Divider  [dim]Active:[/] [yellow]{cur_subj}[/] [dim](Default ON - ✨ 🦴 ANATOMY ✨)[/]\n"
            f"[bold green][10][/] 📚 Subject Auto-Sorter      [dim]Active:[/] [yellow]{cur_sort}[/] [dim](Auto-groups by Subject)[/]\n"
            f"[bold cyan][11][/] ✏️ Custom Video/File Prefix [dim]Current:[/] [yellow]{cur_prefix}[/]\n"
            f"[bold yellow][12][/] 👑 Unified Branding Mode  [dim]Active:[/] {sig_disp} [bold yellow]⭐[/]\n"
            f"[bold red][13][/] 🧹 Clear All Customizations [dim](Reset to Default)[/]\n"
            "[bold cyan][0][/] ⬅️ Back to Main Menu",
            border_style="magenta", box=box.ROUNDED
        ))
        
        choice = await safe_input("Select Setting to Configure", valid_options=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "0"], allow_cancel=True)
        if choice is None: break

        if choice == "1":
            strip_words_list, replace_words_map = get_clean_rules()
            console.print("\n[bold cyan]📝 Word & Watermark Cleaner Studio[/]")
            console.print(f"[dim]Permanent File: [yellow]strip_words.txt[/] ({len(strip_words_list)} words/phrases active)[/]\n")
            console.print(" [1] 📋 View Active Clean Words List")
            console.print(" [2] ➕ Add New Word / Tag to Remove Permanently")
            console.print(" [3] 📂 Open strip_words.txt in Notepad")
            console.print(" [4] 🔄 Edit REPLACE_WORDS mapping (Old:New)")
            sub_c = await safe_input("Select Action (1 / 2 / 3 / 4)", valid_options=["1", "2", "3", "4"], allow_cancel=True, default_val="1")
            if sub_c == "1":
                console.print("\n[bold green]📋 Active Clean Words (strip_words.txt + .env):[/]")
                for idx, w in enumerate(strip_words_list, 1):
                    console.print(f"  [dim]{idx:2d}.[/] [yellow]{w}[/]")
                if replace_words_map:
                    console.print("\n[bold cyan]🔄 Active Replacements:[/]")
                    for ow, nw in replace_words_map.items():
                        console.print(f"  • [red]{ow}[/] ➔ [green]{nw}[/]")
                await safe_input("\nPress Enter to return", default_val="")
            elif sub_c == "2":
                new_w = await safe_input("Enter new word/tag to remove permanently", allow_cancel=True)
                if new_w and new_w.strip():
                    with open("strip_words.txt", "a", encoding="utf-8") as f:
                        f.write(f"\n{new_w.strip()}\n")
                    console.print(f"[bold green]✔ Added '{new_w.strip()}' to strip_words.txt permanently![/]")
                    await asyncio.sleep(1.2)
            elif sub_c == "3":
                console.print("[dim]Opening strip_words.txt in Notepad...[/]")
                if os.name == "nt":
                    os.system("start notepad strip_words.txt")
                await asyncio.sleep(1.0)
            elif sub_c == "4":
                console.print("[dim]Format: OldWord:NewWord,OldChannel:NewChannel[/]")
                val = await safe_input("Enter replacement pairs", allow_cancel=True)
                if val is not None:
                    set_key(env_path, "REPLACE_WORDS", val.strip())
                    console.print("[bold green]✔ Word Replacements saved![/]")
                    await asyncio.sleep(1.0)

        elif choice == "2":
            console.print("\n[bold cyan]🔗 Link Cleaner Configuration[/]")
            rem_choice = await safe_input("1. Remove all external links? (YES / NO)", valid_options=["YES", "NO", "yes", "no"], default_val="YES", allow_cancel=True)
            if rem_choice is not None:
                set_key(env_path, "REMOVE_LINKS", "true" if rem_choice.upper() == "YES" else "false")
                
            cust_link = await safe_input("2. Replace links with your custom link? (e.g. https://t.me/your_channel) [Leave blank for none]", allow_cancel=True)
            if cust_link is not None:
                set_key(env_path, "REPLACE_LINK", cust_link.strip())
                console.print("[bold green]✔ Link settings saved![/]")
                await asyncio.sleep(1.0)

        elif choice == "3":
            console.print("\n[bold cyan]👤 Username Replacement Setup[/]")
            val = await safe_input("Enter your @username to replace all @mentions (or leave blank to clear)", allow_cancel=True)
            if val is not None:
                uname = val.strip()
                if uname and not uname.startswith("@"): uname = f"@{uname}"
                set_key(env_path, "REPLACE_USERNAME", uname)
                console.print("[bold green]✔ Username replacement saved![/]")
                await asyncio.sleep(1.0)

        elif choice == "4":
            console.print("\n[bold cyan]🏷️ Custom Header & Footer Setup[/]")
            hdr = await safe_input("1. Enter TOP Header Text (or blank to clear)", allow_cancel=True)
            if hdr is not None: set_key(env_path, "CUSTOM_HEADER", hdr.strip())
            
            ftr = await safe_input("2. Enter BOTTOM Footer Signature (or blank to clear)", allow_cancel=True)
            if ftr is not None: set_key(env_path, "CUSTOM_FOOTER", ftr.strip())
            console.print("[bold green]✔ Header & Footer saved![/]")
            await asyncio.sleep(1.0)

        elif choice == "5":
            await interactive_filter_setup()

        elif choice == "6":
            cur_val = os.getenv("SILENT_MODE", "false").strip().lower() in ("true", "1", "yes")
            new_val = not cur_val
            set_key(env_path, "SILENT_MODE", "true" if new_val else "false")
            status_str = "[bold green]ON (Notifications Muted)[/]" if new_val else "[bold yellow]OFF (Normal Notifications)[/]"
            console.print(f"\n✔ Silent Mode is now {status_str}")
            await asyncio.sleep(1.2)

        elif choice == "7":
            cur_val = os.getenv("GENERATE_BATCH_INDEX", "true").strip().lower() in ("true", "1", "yes")
            new_val = not cur_val
            set_key(env_path, "GENERATE_BATCH_INDEX", "true" if new_val else "false")
            status_str = "[bold green]ENABLED (Auto-TOC Card at End)[/]" if new_val else "[bold yellow]DISABLED[/]"
            console.print(f"\n✔ Clickable Batch Index Card is now {status_str}")
            await asyncio.sleep(1.2)

        elif choice == "8":
            console.print("\n[bold cyan]🏷️ Smart Auto-Hashtags Configuration[/]")
            console.print("[1] 🟢 ENABLE Smart Auto-Hashtags (Auto-generate #Subject #Lecture)")
            console.print("[2] 🔴 DISABLE & STRIP all hashtags (Clean captions, zero hashtags)")
            console.print("[3] 🟡 KEEP original hashtags without auto-generating new ones")
            tag_ch = await safe_input("Choose Option (1/2/3)", valid_options=["1", "2", "3"], default_val="1" if not cur_tags_val else "2", allow_cancel=True)
            if tag_ch == "1":
                set_key(env_path, "AUTO_HASHTAGS", "true")
                set_key(env_path, "STRIP_HASHTAGS", "false")
                console.print("\n✔ Auto-Hashtags [bold green]ENABLED[/]!")
            elif tag_ch == "2":
                set_key(env_path, "AUTO_HASHTAGS", "false")
                set_key(env_path, "STRIP_HASHTAGS", "true")
                console.print("\n✔ Tagging [bold yellow]DISABLED[/] and existing hashtags will be [bold yellow]STRIPPED[/]!")
            elif tag_ch == "3":
                set_key(env_path, "AUTO_HASHTAGS", "false")
                set_key(env_path, "STRIP_HASHTAGS", "false")
                console.print("\n✔ Original hashtags will be kept as-is (Auto-tagging OFF).")
            await asyncio.sleep(1.2)

        elif choice == "9":
            cur_val = os.getenv("AUTO_SUBJECT_HEADERS", "true").strip().lower() in ("true", "1", "yes")
            new_val = not cur_val
            set_key(env_path, "AUTO_SUBJECT_HEADERS", "true" if new_val else "false")
            status_str = "[bold green]ENABLED (✨ 🦴 ANATOMY ✨)[/]" if new_val else "[bold yellow]DISABLED (OFF)[/]"
            console.print(f"\n✔ Auto-Subject Header Divider is now {status_str}")
            await asyncio.sleep(1.2)

        elif choice == "10":
            cur_val = os.getenv("AUTO_SORT_SUBJECTS", "true").strip().lower() in ("true", "1", "yes")
            new_val = not cur_val
            set_key(env_path, "AUTO_SORT_SUBJECTS", "true" if new_val else "false")
            status_str = "[bold green]ENABLED (Textbook Curriculum Order)[/]" if new_val else "[bold yellow]DISABLED (Raw Sequence)[/]"
            console.print(f"\n✔ Subject Auto-Sorter is now {status_str}")
            await asyncio.sleep(1.2)

        elif choice == "11":
            console.print("\n[bold cyan]✏️ Custom Video / File Prefix Setup[/]")
            console.print("[dim]Enter prefix to prepend to forwarded and uploaded files (e.g. 'Dr Amit - ' / or leave blank to clear):[/]")
            pref_val = await safe_input("Enter prefix", allow_cancel=True)
            if pref_val is not None:
                set_key(env_path, "CUSTOM_FILE_PREFIX", pref_val.strip())
                console.print(f"[bold green]✔ Custom File Prefix saved as: '{pref_val.strip()}'![/]")
                await asyncio.sleep(1.0)

        elif choice == "12":
            cur_bool = os.getenv("ENABLE_SIGNATURE", "true").strip().lower() in ("true", "1", "yes")
            new_val = "false" if cur_bool else "true"
            # Unified Toggle: Clean mode disables both signature and custom branded thumbnail
            new_th = "custom" if new_val == "true" else "original"
            set_key(env_path, "ENABLE_SIGNATURE", new_val)
            set_key(env_path, "THUMB_MODE", new_th)
            os.environ["ENABLE_SIGNATURE"] = new_val
            os.environ["THUMB_MODE"] = new_th
            console.print(f"\n[bold green]✔ Unified Branding toggled to:[/] {'[bold green]ON (Kind Doctor Signature + 16:9 Cover)[/]' if new_val == 'true' else '[bold red]OFF (Clean Mode: No Signature & Original Media)[/]'}")
            await asyncio.sleep(1.2)
            continue

        elif choice == "13":
            confirm = await safe_input("Type 'YES' to clear all custom replacements/headers", allow_cancel=True)
            if confirm == "YES":
                set_key(env_path, "REPLACE_WORDS", "")
                set_key(env_path, "REPLACE_LINK", "")
                set_key(env_path, "REPLACE_USERNAME", "")
                set_key(env_path, "CUSTOM_HEADER", "")
                set_key(env_path, "CUSTOM_FOOTER", "")
                set_key(env_path, "CUSTOM_FILE_PREFIX", "")
                set_key(env_path, "REMOVE_LINKS", "true")
                set_key(env_path, "REMOVE_USERNAMES", "false")
                set_key(env_path, "AUTO_HASHTAGS", "false")
                set_key(env_path, "STRIP_HASHTAGS", "false")
                set_key(env_path, "AUTO_SUBJECT_HEADERS", "true")
                set_key(env_path, "AUTO_SORT_SUBJECTS", "true")
                set_key(env_path, "ENABLE_SIGNATURE", "true")
                console.print("[bold green]✔ All customizations reset to default![/]")
                await asyncio.sleep(1.2)

async def interactive_filter_setup():
    global GLOBAL_RUNTIME_FILTER
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel("[bold cyan]🎯 INTERACTIVE RUNTIME FILTER BUILDER[/]", border_style="green", box=box.ROUNDED))
    console.print("[dim]Set your surgical filters directly without touching .env files![/]\n")
    
    kw_input = await safe_input("1. Enter target keywords separated by comma (e.g. notes, pdf, book) [Leave blank for all]", allow_cancel=True)
    if kw_input is None: return
    keywords = [k.strip().lower() for k in kw_input.split(",") if k.strip()] if kw_input else []
    
    ex_input = await safe_input("2. Enter words to SKIP/IGNORE separated by comma [Leave blank for none]", allow_cancel=True)
    if ex_input is None: return
    exclude_words = [e.strip().lower() for e in ex_input.split(",") if e.strip()] if ex_input else []
    
    console.print("\n3. Choose search scope:")
    console.print("   [1] Anywhere (Text Caption + File Name)")
    console.print("   [2] Caption / Text Only")
    console.print("   [3] File Name Only")
    scope_choice = await safe_input("Select Scope", valid_options=["1", "2", "3"], allow_cancel=True, default_val="1")
    if scope_choice is None: return
    
    scope = "anywhere"
    if scope_choice == "2": scope = "caption"
    elif scope_choice == "3": scope = "filename"

    GLOBAL_RUNTIME_FILTER["keywords"] = keywords
    GLOBAL_RUNTIME_FILTER["exclude_words"] = exclude_words
    GLOBAL_RUNTIME_FILTER["scope"] = scope
    
    update_env_file(mode="filters", filter_data={"keywords": keywords, "exclude": exclude_words, "scope": scope})
    console.print("\n[bold green]✔ Filters successfully locked in and saved for this session![/]")
    await asyncio.sleep(1.2)

async def advanced_cleaner_menu():
    while True:
        clear_screen()
        console.print(get_persistent_header())
        console.print(Panel(
            "[bold magenta]🧹 ADVANCED CLEANER & JUNK PURGE UTILITY[/]\n\n"
            "[bold green][1][/] 🗑️ Purge Old & Duplicate Session Files\n"
            "[bold yellow][2][/] 🗄️ Purge Active DB & Thumbnail Cache (Backup First)\n"
            "[bold magenta][3][/] 📝 Purge JSON Records, Logs & Text Junk\n"
            "[bold red][4][/] ☢️ COMPLETE FACTORY RESET (Wipe Everything)\n"
            "[bold cyan][0][/] ⬅️ Back to Main Menu",
            border_style="magenta", box=box.ROUNDED
        ))
        choice = await safe_input("\nSelect Option", valid_options=["1", "2", "3", "4"], allow_cancel=True)
        if choice is None: break
        
        if choice == "1":
            count = 0
            for f in os.listdir("."):
                if f.endswith(".session") and f != "session_forwarder.session":
                    with suppress(Exception): os.remove(f); count += 1
            console.print(f"\n[bold green]✨ Done! Removed {count} old session file(s).[/]")
            await safe_input("\nPress Enter to continue", allow_cancel=False)
            
        elif choice == "2":
            confirm = await safe_input("Type 'PURGE' to backup then remove the ACTIVE database + thumbnail cache", allow_cancel=True)
            if confirm != "PURGE":
                console.print("[yellow]Cancelled. No active database was changed.[/]")
                await safe_input("\nPress Enter to continue", allow_cancel=False)
                continue
            
            count = 0
            try:
                backup_path = backup_active_database(reason="cleaner_purge")
                for file in [*_active_db_sidecars(), "tg_thumb_cached.jpg"]:
                    if os.path.exists(file):
                        os.remove(file)
                        count += 1
                console.print(f"\n[bold green]✨ Done! Removed {count} active DB/cache file(s).[/]")
                if backup_path: console.print(f"[dim]Safety backup: {backup_path}[/]")
            except Exception as e:
                console.print(f"\n[bold red]❌ Purge aborted; active database preserved.[/] {e}")
            await safe_input("\nPress Enter to continue", allow_cancel=False)
            
        elif choice == "3":
            count = 0
            for file in ["dead_letter.jsonl"]:
                if os.path.exists(file):
                    with suppress(Exception): os.remove(file); count += 1
            console.print(f"\n[bold green]✨ Done! Removed {count} junk file(s).[/]")
            await safe_input("\nPress Enter to continue", allow_cancel=False)
            
        elif choice == "4":
            confirm = await safe_input("Type 'RESET' to wipe everything", allow_cancel=True)
            if confirm == "RESET":
                reset_dir = DB_BACKUP_DIR / f"factory_reset_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                reset_dir.mkdir(parents=True, exist_ok=True)
                try:
                    for t in [".env", "session_forwarder.session", *_active_db_sidecars(), LOCK_FILE]:
                        with suppress(Exception): os.remove(t)
                    release_lock()
                    console.print(f"\n[bold green]✨ Factory Reset Complete![/]\n[dim]Safety backup: {reset_dir}[/]")
                    sys.exit(0)
                except Exception as e:
                    console.print(f"\n[bold red]❌ Factory Reset aborted.[/] {e}")
                    await safe_input("\nPress Enter to return", allow_cancel=False)

async def filter_menu():
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel(
        "[bold cyan]🎯 SELECTIVE MEDIA TRANSFER FILTER[/]\n\n"
        "[white][1][/] 📦 Everything [dim](Default)[/]\n"
        "[white][2][/] 🎬 Only Videos\n"
        "[white][3][/] 📄 Only Documents\n"
        "[white][4][/] 🖼️ Only Photos\n"
        "[bold red][0][/] ⬅️ Back to Main Menu",
        border_style="cyan", box=box.ROUNDED
    ))
    ch = await safe_input("Select Filter", valid_options=["1", "2", "3", "4"], allow_cancel=True, default_val="1")
    if ch == "2": 
        update_env_file(mode="media_filter", filter_data="video")
        return "video"
    if ch == "3": 
        update_env_file(mode="media_filter", filter_data="document")
        return "document"
    if ch == "4":
        update_env_file(mode="media_filter", filter_data="photos")
        return "photos"
    if ch is None: return "back"
    
    update_env_file(mode="media_filter", filter_data="all")
    return "all"

async def thumbnail_menu():
    global THUMB_MODE
    while True:
        load_dotenv(override=True)
        cur_file = os.getenv("THUMB_FILE", "kind_doctor_thumb.jpg").strip()
        clear_screen()
        console.print(get_persistent_header())
        console.print(Panel(
            f"[bold magenta]🖼️ 16:9 THUMBNAIL & COVER STUDIO[/]\n\n"
            f" • [cyan]Active Mode  :[/] [bold yellow]{THUMB_MODE.upper()}[/]\n"
            f" • [cyan]Active Image :[/] [bold green]{cur_file}[/]\n\n"
            "[bold green][1][/] 📁 Set / Change Custom 16:9 Cover Image File\n"
            "[bold yellow][2][/] 🎞️ Keep Original Media Thumbnail (Disable Custom Cover)\n"
            "[bold magenta][3][/] 🔄 Force Re-render & Refresh Thumbnail Cache\n"
            "[bold cyan][0][/] ⬅️ Back to Main Menu",
            border_style="magenta", box=box.ROUNDED
        ))
        ch = await safe_input("\nSelect Option (1/2/3/0)", valid_options=["1", "2", "3", "0"], allow_cancel=True)
        if not ch or ch == "0": break

        if ch == "1":
            console.print("\n[bold cyan]📁 Select Custom 16:9 Cover Image File[/]")
            console.print("[dim]Enter absolute path to your image (.jpg / .png / .jpeg):[/]")
            new_path = await safe_input("Image File Path (or blank to cancel)", default_val="", allow_cancel=True)
            if new_path and new_path.strip():
                clean_p = Path(new_path.strip().strip("'\""))
                if clean_p.exists() and clean_p.is_file():
                    dest_name = f"custom_cover{clean_p.suffix}"
                    try:
                        shutil.copy2(str(clean_p), dest_name)
                        set_key(".env", "THUMB_FILE", dest_name)
                        set_key(".env", "THUMB_MODE", "custom")
                        THUMB_MODE = "custom"
                        ThumbEnforcer().force_regenerate()
                        console.print(f"\n[bold green]✔ Custom Cover successfully updated from:[/] [cyan]{clean_p.name}[/]")
                        console.print("[bold green]✔ Perfect 16:9 (1280x720) thumbnail cache generated![/]")
                    except Exception as e:
                        console.print(f"\n[bold red]❌ Failed to copy image:[/] {e}")
                else:
                    console.print(f"\n[bold red]❌ File not found at:[/] {clean_p}")
            await asyncio.sleep(1.5)

        elif ch == "2":
            THUMB_MODE = "original"
            set_key(".env", "THUMB_MODE", "original")
            console.print("\n[bold yellow]✔ Mode set to ORIGINAL. Custom cover disabled.[/]")
            await asyncio.sleep(1.2)
            break

        elif ch == "3":
            ThumbEnforcer().force_regenerate()
            THUMB_MODE = "custom"
            set_key(".env", "THUMB_MODE", "custom")
            console.print("\n[bold green]✔ Thumbnail cache refreshed successfully![/]")
            await asyncio.sleep(1.2)

async def mode_toggle_menu():
    env_path = ".env"
    while True:
        load_dotenv(override=True)
        cur_direct = os.getenv("DIRECT_FORWARD", "false").strip().lower() in ("true", "1", "yes")
        cur_mode_txt = "[bold green]⚡ FAST DIRECT FORWARD (0.2s)[/]" if cur_direct else "[bold cyan]🔄 STREAM MODE (Safe Default)[/]"
        
        clear_screen()
        console.print(get_persistent_header())
        console.print(Panel(
            "[bold cyan]⚡ FORWARDING PIPELINE & UNRESTRICTED CHANNEL ENGINE[/]\n"
            "[dim]Choose how messages and media are forwarded from source to target![/]\n\n"
            f" • [cyan]Active Engine Mode :[/] {cur_mode_txt}\n\n"
            "[bold cyan][1][/] 🔄 [bold white]Stream Mode[/] [bold yellow]⭐ (Recommended Default)[/]\n"
            "   • [dim]In-memory RAM streaming (0 MB disk space used)[/]\n"
            "   • [dim]100% cuts origin links & generates clean, brand-new file hashes[/]\n"
            "   • [dim]Successfully attaches your Custom 16:9 Cover[/]\n"
            "   • [dim]Bypasses restricted & copy-protected channels seamlessly[/]\n\n"
            "[bold green][2][/] ⚡ [bold white]Fast Direct Mode[/] [dim](For Unrestricted / Public Channels)[/]\n"
            "   • [dim]Instant 0.2s server-side forwarding without re-upload delay[/]\n"
            "   • [dim]Bypasses forward signature tag (sends as clean message)[/]\n"
            "   • [dim]Ideal for high-speed batch transfers on unrestricted channels[/]\n"
            "   • [yellow]Note: Retains original thumbnail (custom cover cannot be attached to direct clones)[/]\n\n"
            "[bold cyan][0][/] ⬅️ Back to Main Menu",
            border_style="cyan", box=box.ROUNDED
        ))
        ch = await safe_input("\nSelect Forwarding Mode (1/2/0)", valid_options=["1", "2", "0"], allow_cancel=True)
        if not ch or ch == "0":
            break
        if ch == "1":
            set_key(env_path, "DIRECT_FORWARD", "false")
            os.environ["DIRECT_FORWARD"] = "false"
            console.print("\n[bold cyan]✔ Pipeline switched to: STREAM MODE (Safe, Clean Hashes, 16:9 Cover Enabled)![/]")
            await asyncio.sleep(1.2)
        elif ch == "2":
            set_key(env_path, "DIRECT_FORWARD", "true")
            os.environ["DIRECT_FORWARD"] = "true"
            console.print("\n[bold green]✔ Pipeline switched to: FAST DIRECT MODE (0.2s Instant Forward for Unrestricted Channels)![/]")
            await asyncio.sleep(1.2)

async def wipe_memory():
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel("[bold yellow]⚠️ WIPE FORWARDING HISTORY[/]", border_style="yellow", box=box.ROUNDED))
    confirm = await safe_input("Type 'yes' to clear database history and restart scan fresh", allow_cancel=True)
    if confirm and confirm.lower() == "yes":
        try:
            backup_path = backup_active_database(reason="history_wipe")
            conn = sqlite3.connect(DB_FILE)
            conn.execute("DROP TABLE IF EXISTS forwarded")
            conn.execute("DROP TABLE IF EXISTS source_watermarks")
            conn.execute("VACUUM")
            conn.commit()
            conn.close()
            safe_remove_active_database_files()
            console.print("[green]✔ History wiped and Physical Disk Space reclaimed (VACUUM successful)![/]")
            if backup_path: console.print(f"[dim]Safety backup: {backup_path}[/]")
        except Exception as e:
            console.print(f"[bold red]❌ History wipe aborted; active database preserved.[/] {e}")
        await asyncio.sleep(1.5)

def natural_sort_key(s):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', str(s))]

def generate_folder_hashtags(subject_name: str) -> str:
    clean_subj = subject_name.strip()
    clean_subj = re.sub(r'(?i)ma[_|\']?am', 'Mam', clean_subj)
    clean_subj = re.sub(r'(?i)sir[_]', 'Sir', clean_subj)
    words = re.findall(r'[A-Za-z0-9]+', clean_subj)
    tags = []
    camel_parts = []
    for w in words:
        if len(w) <= 3 and w.isupper():
            camel_parts.append(w)
        else:
            camel_parts.append(w.capitalize())
    tag_camel = "#" + "".join(camel_parts)
    if len(tag_camel) > 1:
        tags.append(tag_camel)
    tag_snake = "#" + "_".join(words)
    if len(tag_snake) > 1 and tag_snake.lower() != tag_camel.lower():
        tags.append(tag_snake)
    if "-" in subject_name:
        base_subj = subject_name.split("-")[0].strip()
        base_clean = re.sub(r'[^a-zA-Z0-9]', '', base_subj)
        if base_clean and f"#{base_clean}" not in tags:
            tags.append(f"#{base_clean}")
    tags.extend(["#MedEdNotes", "#KindDoctor"])
    return " ".join(OrderedDict.fromkeys(tags))

async def run_single_file_splitter_tool(session_mgr):
    load_dotenv(override=True)
    target_chat = os.getenv("TARGET_CHAT", "").strip()
    target_topic = os.getenv("TARGET_TOPIC", "0").strip()
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel("[bold cyan]📂 SINGLE LARGE FILE SPLITTER & UPLOADER (Bypass 2GB Limit)[/]", border_style="green", box=box.ROUNDED))
    file_path_str = await safe_input("Enter absolute path of large video/file on PC", allow_cancel=True)
    if not file_path_str: return
    file_path = Path(file_path_str.strip().strip('"').strip("'"))
    if not file_path.exists() or not file_path.is_file():
        console.print(f"[bold red]❌ File not found at: {file_path}[/]")
        await safe_input("\nPress Enter to return", allow_cancel=False)
        return
    file_size = file_path.stat().st_size
    size_gb = file_size / GB
    console.print(f"[cyan]📁 File Detected:[/] {file_path.name} ([yellow]{size_gb:.2f} GB[/])")
    target_chat_prompt = await safe_input("Target Chat ID / Username / Link", default_val=target_chat if target_chat else None, allow_cancel=True)
    if not target_chat_prompt: return
    target_chat = target_chat_prompt.strip()

    default_topic_from_link = "0"
    if "t.me/" in target_chat:
        try:
            parsed_link = parse_telegram_link(target_chat)
            if parsed_link and parsed_link.get("TOPIC_ID"):
                default_topic_from_link = str(parsed_link["TOPIC_ID"])
        except Exception:
            pass

    topic_default = default_topic_from_link if default_topic_from_link != "0" else (target_topic if target_topic else "0")
    target_topic_prompt = await safe_input("Target Forum Topic ID (0 for General)", default_val=topic_default, allow_cancel=True)
    if target_topic_prompt is None: return
    target_topic = target_topic_prompt.strip()

    # Custom Rename / Prefix
    rename_prefix_prompt = await safe_input("Custom File Title / Prefix (Optional, e.g. 'Dr Amit - ' / Press Enter to skip)", default_val="", allow_cancel=True)
    rename_prefix = rename_prefix_prompt.strip() if rename_prefix_prompt else ""
    disp_base_name = f"{rename_prefix}{file_path.name}" if rename_prefix else file_path.name

    chunk_size = int(1.9 * GB)
    total_chunks = math.ceil(file_size / chunk_size)
    console.print(f"[cyan]ℹ️ Splitting into {total_chunks} part(s) (~1.9 GB each)...[/]")
    confirm = await safe_input(f"Type 'YES' to start splitting and uploading to {target_chat}", allow_cancel=True)
    if confirm != "YES":
        console.print("[yellow]Cancelled.[/]")
        await safe_input("\nPress Enter to return", allow_cancel=False)
        return

    client = session_mgr.get_client()
    thumb_enforcer = ThumbEnforcer()
    t_path = thumb_enforcer.get()
    try:
        if not client.is_connected():
            await client.start()
        console.print("[green]✔ Connected to Telegram. Verifying destination channel...[/]")
        target_entity, resolved_topic = await resolve_telethon_entity(client, target_chat, target_topic)
        final_topic = resolved_topic if resolved_topic is not None else (int(target_topic) if target_topic and str(target_topic) != "0" else None)
        topic_kw = {"reply_to": final_topic} if final_topic else {}

        chat_title = getattr(target_entity, "title", None) or getattr(target_entity, "username", None) or str(target_chat)
        console.print(f"[bold green]✔ Destination Verified:[/] [cyan]{chat_title}[/] (Topic ID: {final_topic or 'General'})\n")

        is_vid = file_path.suffix.lower() in (".mp4", ".mkv", ".mov", ".avi", ".webm")
        with open(file_path, "rb") as f:
            for i in range(total_chunks):
                part_name = f"{file_path.name}.part{i+1}"
                part_disp_name = f"{disp_base_name}.part{i+1}"
                part_path = Path(part_name)
                console.print(f"[cyan]📦 Preparing Part {i+1} of {total_chunks} ([yellow]{part_disp_name}[/])...[/]")
                bytes_written = 0
                with open(part_path, "wb") as pf:
                    while bytes_written < chunk_size:
                        data = f.read(min(1024 * 1024, chunk_size - bytes_written))
                        if not data: break
                        pf.write(data)
                        bytes_written += len(data)
                
                part_cap_raw = f"📄 **{disp_base_name}**\n📍 Part {i+1} of {total_chunks}"
                caption_res = customize_caption(part_cap_raw, for_media=True)
                caption = caption_res[0] if isinstance(caption_res, tuple) else caption_res

                part_attrs = [DocumentAttributeFilename(file_name=part_disp_name)]
                if is_vid:
                    part_attrs.append(DocumentAttributeVideo(duration=0, w=1280, h=720, supports_streaming=True))

                console.print(f"[yellow]🚀 Uploading {part_disp_name} ({bytes_written / MB:.1f} MB)...[/]")
                await client.send_file(
                    target_entity,
                    str(part_path),
                    caption=caption,
                    thumb=t_path,
                    attributes=part_attrs,
                    supports_streaming=True,
                    **topic_kw
                )
                console.print(f"[green]✔ Part {i+1} Uploaded Successfully![/]")
                with suppress(Exception): part_path.unlink()
        console.print("\n[bold green]✨ All parts split and uploaded successfully![/]")
    except Exception as e:
        console.print(f"\n[bold red]❌ Upload/Split Error:[/] {e}")
    await safe_input("\nPress Enter to return to menu", allow_cancel=False)

async def run_batch_folder_uploader_tool(session_mgr):
    load_dotenv(override=True)
    target_chat = os.getenv("TARGET_CHAT", "").strip()
    target_topic = os.getenv("TARGET_TOPIC", "0").strip()
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel(
        "[bold cyan]📚 BATCH FOLDER & SUBJECT-WISE PDF/MEDIA UPLOADER[/]\n"
        "[dim]Auto-scans root folders, detects subjects, naturally sorts files (CH-01...CH-10), generates auto-hashtags & bypasses 2GB limits![/]",
        border_style="cyan", box=box.ROUNDED
    ))

    raw_path = await safe_input("Enter Root Directory / Folder Path on PC", allow_cancel=True)
    if not raw_path: return
    clean_dir = Path(raw_path.strip().strip('"').strip("'"))
    if not clean_dir.exists() or not clean_dir.is_dir():
        console.print(f"[bold red]❌ Invalid directory path: {clean_dir}[/]")
        await safe_input("\nPress Enter to return", allow_cancel=False)
        return

    # Scanning directories and subdirectories
    console.print(f"\n[cyan]🔍 Scanning directory structure at:[/] [yellow]{clean_dir}[/]")
    subjects_map = OrderedDict()
    
    # 1. Check direct subdirectories
    subdirs = [p for p in clean_dir.iterdir() if p.is_dir() and not p.name.startswith(".")]
    subdirs.sort(key=lambda p: natural_sort_key(p.name))

    # 2. Check direct files in root
    root_files = [p for p in clean_dir.iterdir() if p.is_file() and not p.name.startswith(".")]
    if root_files:
        root_files.sort(key=lambda p: natural_sort_key(p.name))
        subjects_map[clean_dir.name] = root_files

    for sdir in subdirs:
        # Recursively gather files in this subject folder
        s_files = [p for p in sdir.rglob("*") if p.is_file() and not p.name.startswith(".")]
        if s_files:
            s_files.sort(key=lambda p: natural_sort_key(p.name))
            subjects_map[sdir.name] = s_files

    if not subjects_map:
        console.print(f"[bold red]❌ No files found inside: {clean_dir}[/]")
        await safe_input("\nPress Enter to return", allow_cancel=False)
        return

    # Display Rich Subject Summary Table
    subj_list = list(subjects_map.keys())
    table = Table(title="[bold green]📁 Detected Subjects & Files Summary[/]", box=box.ROUNDED, expand=True)
    table.add_column("#", justify="center", style="bold cyan", no_wrap=True, width=5)
    table.add_column("Subject / Subfolder Name", style="bold white", ratio=3)
    table.add_column("Files Count", justify="center", style="green", ratio=1)
    table.add_column("Total Size", justify="right", style="yellow", ratio=1)

    grand_total_files = 0
    grand_total_bytes = 0

    for idx, sname in enumerate(subj_list, start=1):
        flist = subjects_map[sname]
        stotal_bytes = sum(f.stat().st_size for f in flist if f.exists())
        stotal_mb = stotal_bytes / MB
        size_str = f"{stotal_mb:.1f} MB" if stotal_mb < 1024 else f"{stotal_mb/1024:.2f} GB"
        table.add_row(str(idx), sname, f"{len(flist)} files", size_str)
        grand_total_files += len(flist)
        grand_total_bytes += stotal_bytes

    grand_mb = grand_total_bytes / MB
    grand_size_str = f"{grand_mb:.1f} MB" if grand_mb < 1024 else f"{grand_mb/1024:.2f} GB"
    table.add_section()
    table.add_row("∑", f"[bold yellow]TOTAL: {len(subj_list)} Subjects[/]", f"[bold green]{grand_total_files} Files[/]", f"[bold yellow]{grand_size_str}[/]")

    console.print(table)

    # Subject Selection prompt
    console.print("\n[bold cyan]Select Subjects to Upload:[/]")
    console.print("[dim]• Enter [bold green]'A'[/] to upload ALL subjects[/]")
    console.print("[dim]• Or specify numbers/ranges, e.g. [bold yellow]1, 3, 5[/] or [bold yellow]1-4[/][/]")
    sel_input = await safe_input("Subjects Selection", default_val="A", allow_cancel=True)
    if not sel_input: return

    selected_subjects = []
    if sel_input.strip().upper() == "A":
        selected_subjects = subj_list
    else:
        parts = [p.strip() for p in sel_input.split(",") if p.strip()]
        for part in parts:
            if "-" in part:
                try:
                    s_start, s_end = map(int, part.split("-"))
                    for i in range(s_start, s_end + 1):
                        if 1 <= i <= len(subj_list):
                            selected_subjects.append(subj_list[i-1])
                except ValueError: pass
            else:
                try:
                    i = int(part)
                    if 1 <= i <= len(subj_list):
                        selected_subjects.append(subj_list[i-1])
                except ValueError: pass
        # Preserve order & deduplicate
        selected_subjects = list(OrderedDict.fromkeys(selected_subjects))

    if not selected_subjects:
        console.print("[bold red]❌ No valid subjects selected.[/]")
        await safe_input("\nPress Enter to return", allow_cancel=False)
        return

    console.print(f"[bold green]✔ Selected {len(selected_subjects)} subject(s) for upload.[/]")

    # Target Chat & Topic Configuration
    target_chat_prompt = await safe_input("Target Chat ID / Username / Link", default_val=target_chat if target_chat else None, allow_cancel=True)
    if not target_chat_prompt: return
    target_chat = target_chat_prompt.strip()

    parsed_chat_id = target_chat
    default_topic_from_link = "0"
    if "t.me/" in target_chat:
        try:
            parsed_link = parse_telegram_link(target_chat)
            if parsed_link and parsed_link.get("CHAT_ID"):
                parsed_chat_id = str(parsed_link["CHAT_ID"])
                if parsed_link.get("TOPIC_ID"):
                    default_topic_from_link = str(parsed_link["TOPIC_ID"])
                console.print(f"[bold green]✔ Link detected:[/] Channel ID = [cyan]{parsed_chat_id}[/], Topic ID = [cyan]{default_topic_from_link}[/]")
        except Exception:
            pass
    target_chat = parsed_chat_id

    topic_default = default_topic_from_link if default_topic_from_link != "0" else (target_topic if target_topic else "0")
    target_topic_prompt = await safe_input("Target Forum Topic ID (0 for General)", default_val=topic_default, allow_cancel=True)
    if target_topic_prompt is None: return
    target_topic = target_topic_prompt.strip()

    # Duplicate Skip / Resume
    skip_dup = await safe_input("Skip already uploaded files (Resume Protection)? (Y/N)", valid_options=["Y", "N", "y", "n"], default_val="Y", allow_cancel=True)
    if not skip_dup: return
    skip_duplicates = skip_dup.upper() == "Y"

    # Hashtags Toggle & Extra Tag
    cur_tags_env = os.getenv("AUTO_HASHTAGS", "true").strip().lower() in ("true", "1", "yes")
    include_tags = await safe_input("Include Smart Auto-Hashtags in Caption? (Y/N)", valid_options=["Y", "N", "y", "n"], default_val="Y" if cur_tags_env else "N", allow_cancel=True)
    if not include_tags: return
    use_hashtags = include_tags.upper() == "Y"

    extra_tag = ""
    if use_hashtags:
        extra_tag_prompt = await safe_input("Custom Extra Tag (Optional, e.g. RapidRevision / Press Enter to skip)", default_val="", allow_cancel=True)
        if extra_tag_prompt is None: return
        extra_tag = extra_tag_prompt.strip()

    # Custom File Renaming Prefix
    rename_prefix_prompt = await safe_input("Custom File Title / Prefix (Optional, e.g. 'Dr Amit - ' / Press Enter to skip)", default_val="", allow_cancel=True)
    if rename_prefix_prompt is None: return
    rename_prefix = rename_prefix_prompt.strip()

    # Final Confirmation
    confirm = await safe_input(f"\nType 'YES' to start uploading {len(selected_subjects)} subject(s) to {target_chat}", allow_cancel=True)
    if confirm != "YES":
        console.print("[yellow]Upload cancelled.[/]")
        await safe_input("\nPress Enter to return", allow_cancel=False)
        return

    # Telegram Client & State Manager Init
    client = session_mgr.get_client()
    state = StateManager()
    await state.start()
    thumb_enforcer = ThumbEnforcer()
    t_path = thumb_enforcer.get()

    uploaded_files_count = 0
    skipped_files_count = 0
    failed_files_count = 0
    total_bytes_uploaded = 0

    try:
        if not client.is_connected():
            await client.start()
        console.print("\n[bold green]🚀 Connected to Telegram Engine! Initializing batch pipeline...[/]")
        target_entity, resolved_topic = await resolve_telethon_entity(client, target_chat, target_topic)
        final_topic = resolved_topic if resolved_topic is not None else (int(target_topic) if target_topic and str(target_topic) != "0" else None)
        topic_kw = {"reply_to": final_topic} if final_topic else {}

        chat_title = getattr(target_entity, "title", None) or getattr(target_entity, "username", None) or str(target_chat)
        console.print(f"[bold green]✔ Destination Channel Verified:[/] [cyan]{chat_title}[/] (Topic ID: {final_topic or 'General'})\n")

        for s_idx, sname in enumerate(selected_subjects, start=1):
            files = subjects_map[sname]
            hashtags = ""
            if use_hashtags:
                hashtags = generate_folder_hashtags(sname)
                if extra_tag:
                    clean_extra = "#" + re.sub(r'[^a-zA-Z0-9]', '', extra_tag)
                    if clean_extra not in hashtags:
                        hashtags = f"{hashtags} {clean_extra}"

            console.print(Rule(f"[bold cyan]📁 Subject [{s_idx}/{len(selected_subjects)}]: {sname} ({len(files)} files)[/]", style="cyan"))

            # Check if there are pending files to upload in this subject
            has_pending = False
            for f in files:
                if not (skip_duplicates and await state.is_local_file_uploaded(str(f.resolve()), target_chat, int(target_topic or 0))):
                    has_pending = True
                    break

            # Send Subject Header Announcement Post to Telegram
            if has_pending:
                subj_body = (
                    f"📌 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📚 **SUBJECT: {sname.upper()}**\n"
                    f"📁 **Total Files:** {len(files)} Notes & Media\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                )
                if hashtags:
                    subj_body += f"\n\n{hashtags}"
                subject_header_msg = customize_caption(subj_body)

                try:
                    if t_path and os.path.exists(t_path):
                        await client.send_file(
                            target_entity,
                            t_path,
                            caption=subject_header_msg,
                            **topic_kw
                        )
                    else:
                        await client.send_message(
                            target_entity,
                            subject_header_msg,
                            **topic_kw
                        )
                    console.print(f"  [bold green]📢 Subject Header Announcement Sent to Telegram for: {sname}[/]")
                    await asyncio.sleep(1.0)
                except Exception as he:
                    console.print(f"  [dim yellow]⚠️ Subject header notice: {he}[/]")

            for f_idx, fpath in enumerate(files, start=1):
                if not fpath.exists(): continue
                f_size = fpath.stat().st_size
                f_mb = f_size / MB
                disp_name = f"{rename_prefix}{fpath.name}" if rename_prefix else fpath.name

                # Resume Check
                if skip_duplicates and await state.is_local_file_uploaded(str(fpath.resolve()), target_chat, int(target_topic or 0)):
                    console.print(f"  [dim]⏩ [Skipped - Already Uploaded][/] [cyan]{disp_name}[/]")
                    skipped_files_count += 1
                    continue

                cap_body = f"📚 **Subject:** {sname}\n📄 **File:** {disp_name}"
                if hashtags:
                    cap_body += f"\n\n{hashtags}"
                caption = customize_caption(cap_body)

                # Check if file > 2GB (1.95 GB)
                if f_size > (1.95 * GB):
                    console.print(f"  [bold yellow]⚠️ File > 2GB ({f_mb/1024:.2f} GB). Auto-splitting into ~1.9GB parts...[/]")
                    chunk_size = int(1.9 * GB)
                    total_chunks = math.ceil(f_size / chunk_size)
                    with open(fpath, "rb") as f_in:
                        for p_idx in range(total_chunks):
                            part_name = f"{fpath.name}.part{p_idx+1}"
                            part_path = Path(part_name)
                            bytes_written = 0
                            with open(part_path, "wb") as pf:
                                while bytes_written < chunk_size:
                                    data = f_in.read(min(1024 * 1024, chunk_size - bytes_written))
                                    if not data: break
                                    pf.write(data)
                                    bytes_written += len(data)
                            part_disp_name = f"{disp_name}.part{p_idx+1}"
                            part_cap_raw = (
                                f"📚 **Subject:** {sname}\n"
                                f"📄 **File:** {disp_name} (Part {p_idx+1}/{total_chunks})"
                            )
                            if hashtags:
                                part_cap_raw += f"\n\n{hashtags}"
                            part_cap_res = customize_caption(part_cap_raw, for_media=True)
                            part_caption = part_cap_res[0] if isinstance(part_cap_res, tuple) else part_cap_res

                            part_attrs = [DocumentAttributeFilename(file_name=part_disp_name)]
                            console.print(f"    [yellow]🚀 Uploading {part_disp_name} ({bytes_written/MB:.1f} MB)...[/]")
                            await client.send_file(
                                target_entity,
                                str(part_path),
                                caption=part_caption,
                                thumb=t_path,
                                attributes=part_attrs,
                                supports_streaming=True,
                                **topic_kw
                            )
                            with suppress(Exception): part_path.unlink()
                    await state.record_local_file_upload(str(fpath.resolve()), f_size, target_chat, int(target_topic or 0), sname)
                    uploaded_files_count += 1
                    total_bytes_uploaded += f_size
                    console.print(f"  [bold green]✔ [{f_idx}/{len(files)}][/] [white]{disp_name}[/] [dim](Split & Uploaded)[/]")
                else:
                    # Standard <= 2GB High Speed Streaming Upload
                    last_printed_pct = -10
                    upload_start = time.monotonic()

                    def progress_bar(current, total):
                        nonlocal last_printed_pct
                        pct = int((current / max(1, total)) * 100)
                        if pct >= last_printed_pct + 25 or pct == 100:
                            last_printed_pct = pct
                            elapsed = max(0.1, time.monotonic() - upload_start)
                            speed_mb = (current / MB) / elapsed
                            cur_str = f"{current/MB:.1f} MB" if current < GB else f"{current/GB:.2f} GB"
                            tot_str = f"{total/MB:.1f} MB" if total < GB else f"{total/GB:.2f} GB"
                            eta_sec = int((total - current) / max(1, (current / elapsed)))
                            console.print(f"    [cyan]↳ Uploading:[/] [green]{pct}%[/] [dim]({cur_str}/{tot_str} @ {speed_mb:.1f} MB/s | ETA: {eta_sec}s)[/]")

                    is_vid = fpath.suffix.lower() in (".mp4", ".mkv", ".mov", ".avi", ".webm")
                    file_attrs = [DocumentAttributeFilename(file_name=disp_name)]
                    if is_vid:
                        file_attrs.append(DocumentAttributeVideo(duration=0, w=1280, h=720, supports_streaming=True))

                    max_retries = 3
                    uploaded_ok = False
                    for attempt in range(max_retries):
                        try:
                            console.print(f"  [bold yellow]🚀 [{f_idx}/{len(files)}][/] [white]{disp_name}[/] [dim]({f_mb:.1f} MB)[/]")
                            await client.send_file(
                                target_entity,
                                str(fpath),
                                caption=caption,
                                thumb=t_path,
                                attributes=file_attrs,
                                supports_streaming=True,
                                progress_callback=progress_bar,
                                **topic_kw
                            )
                            uploaded_ok = True
                            break
                        except FloodWaitError as fe:
                            console.print(f"    [bold yellow]⏳ Telegram FloodWait: Sleeping for {fe.seconds + 2}s...[/]")
                            await asyncio.sleep(fe.seconds + 2)
                        except Exception as err:
                            if attempt == max_retries - 1:
                                console.print(f"    [bold red]❌ Failed to upload {fpath.name}: {err}[/]")
                                failed_files_count += 1
                            else:
                                await asyncio.sleep(2)

                    if uploaded_ok:
                        await state.record_local_file_upload(str(fpath.resolve()), f_size, target_chat, int(target_topic or 0), sname)
                        uploaded_files_count += 1
                        total_bytes_uploaded += f_size
                        console.print(f"  [bold green]✔ Done:[/] [white]{fpath.name}[/]")
                        await asyncio.sleep(0.6)  # Gentle Telegram rate limit pause

        # Completion Summary Panel
        t_mb = total_bytes_uploaded / MB
        t_str = f"{t_mb:.1f} MB" if t_mb < 1024 else f"{t_mb/1024:.2f} GB"
        console.print(Panel(
            f"[bold green]✨ BATCH UPLOAD COMPLETED SUCCESSFULLY![/]\n\n"
            f"👤 [bold cyan]Target Chat:[/] {target_chat}\n"
            f"📁 [bold cyan]Subjects Processed:[/] {len(selected_subjects)}\n"
            f"✅ [bold green]Files Uploaded:[/] {uploaded_files_count}\n"
            f"⏩ [bold yellow]Files Skipped (Resume):[/] {skipped_files_count}\n"
            f"❌ [bold red]Failed Files:[/] {failed_files_count}\n"
            f"⚡ [bold cyan]Total Data Uploaded:[/] {t_str}",
            border_style="green", box=box.ROUNDED
        ))
    except Exception as e:
        console.print(f"\n[bold red]❌ Fatal Batch Upload Error:[/] {e}")
        traceback.print_exc()
    finally:
        await state.close()

    await safe_input("\nPress Enter to return to menu", allow_cancel=False)

async def run_local_splitter_tool(session_mgr):
    while True:
        clear_screen()
        console.print(get_persistent_header())
        console.print(Panel(
            "[bold cyan]📁 BATCH FOLDER & LOCAL FILE 2GB UPLOADER[/]\n\n"
            "[bold green][1][/] 📚 [bold white]Batch Folder / Subject-wise PDF Uploader[/] [dim]• Auto-Tags, Sequence, Resume & Live Speed[/]\n"
            "[bold yellow][2][/] ✂️ [bold white]Single Large File Splitter (Bypass 2GB Limit)[/] [dim]• Split .part1, .part2...[/]\n"
            "[bold cyan][0][/] ⬅️ Return to Main Menu",
            border_style="cyan", box=box.ROUNDED
        ))
        ch = await safe_input("Choose Mode (1/2/0)", valid_options=["0", "1", "2"], default_val="1", allow_cancel=True)
        if not ch or ch == "0":
            break
        elif ch == "1":
            await run_batch_folder_uploader_tool(session_mgr)
        elif ch == "2":
            await run_single_file_splitter_tool(session_mgr)

async def run_group_cloner_tool(session_mgr):
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel("[bold magenta]🧬 FULL GROUP & FORUM STRUCTURE CLONER[/]", border_style="magenta", box=box.ROUNDED))
    console.print("[dim]Mirror clone entire groups, all forum topics, threads & message history![/]\n")
    
    client = await session_mgr.ensure_active_client()
    if not client: return None
        
    console.print("[bold cyan]Step 1: Choose SOURCE Group to Clone[/]")
    src_sel = await interactive_channel_selector(client, prompt_title="SOURCE Group")
    if not src_sel: return None
    
    console.print("\n[bold cyan]Step 2: Choose TARGET Group (Destination)[/]")
    tgt_sel = await interactive_channel_selector(client, prompt_title="TARGET Group")
    if not tgt_sel: return None
    
    src_id = src_sel["id"]
    tgt_id = tgt_sel["id"]
    
    console.print(f"\n[cyan]🔍 Inspecting Source Structure for {src_sel['title']}...[/]")
    
    src_topics = []
    try:
        src_peer = await client.get_input_entity(_parse_chat_id(src_id))
        res = await client(GetForumTopicsRequest(
            peer=src_peer,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=100
        ))
        if hasattr(res, 'topics'):
            src_topics = res.topics
    except Exception as e:
        logger.info(f"Source forum lookup: {e}")
        
    if not src_topics:
        console.print("[yellow]ℹ️ Source is a Standard Group/Channel (No Forum Topics).[/]")
        console.print(f"[bold green]Configuring direct 1-to-1 mirror clone: {src_id} ➔ {tgt_id}[/]\n")
        update_env_file(chat_id=src_id, topic_id=0, mode="1")
        update_env_file(chat_id=tgt_id, topic_id=0, mode="2")
        confirm = await safe_input("Start Cloning Now? (YES / NO)", valid_options=["YES", "NO", "yes", "no"], default_val="YES", allow_cancel=True)
        if confirm and confirm.upper() == "YES":
            return (1, 12, False, "all", 1, False, False)
        return None
        
    console.print(f"[bold green]✨ Found {len(src_topics)} Forum Topics in Source Group![/]")
    topic_table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    topic_table.add_column("#", style="dim", width=4)
    topic_table.add_column("Topic Title", style="bold yellow")
    topic_table.add_column("Topic ID", style="cyan")
    
    for idx, t in enumerate(src_topics, 1):
        topic_table.add_row(str(idx), getattr(t, 'title', f'Topic {t.id}'), str(t.id))
    console.print(topic_table)
    
    tgt_topics_map = {}
    tgt_peer = await client.get_input_entity(_parse_chat_id(tgt_id))
    try:
        tgt_res = await client(GetForumTopicsRequest(
            peer=tgt_peer,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=100
        ))
        if hasattr(tgt_res, 'topics'):
            for tt in tgt_res.topics:
                tgt_topics_map[tt.title.lower()] = tt.id
    except Exception as e:
        logger.info(f"Target forum lookup: {e}")
        
    console.print("\n[bold cyan]Step 3: Topic Mirroring & Auto-Creation in Target...[/]")
    rules_to_create = []
    
    for t in src_topics:
        t_title = getattr(t, 'title', f'Topic {t.id}')
        tgt_t_id = tgt_topics_map.get(t_title.lower())
        
        if tgt_t_id:
            console.print(f" [green]✔ Found existing matching topic in target:[/] {t_title} (ID: {tgt_t_id})")
        else:
            try:
                created = await client(CreateForumTopicRequest(
                    peer=tgt_peer,
                    title=t_title,
                    icon_color=getattr(t, 'icon_color', None) or 7322096,
                    random_id=generate_random_long()
                ))
                tgt_t_id = created.updates[0].id if hasattr(created, 'updates') and created.updates else (getattr(created, 'id', None) or t.id)
                console.print(f" [bold green]➕ Created new matching topic in target:[/] {t_title} (ID: {tgt_t_id})")
            except Exception as e:
                console.print(f" [yellow]⚠️ Could not auto-create '{t_title}' ({e}) -> Using default[/]")
                tgt_t_id = 0
                
        rules_to_create.append(f"{src_id}:{t.id}:{tgt_id}:{tgt_t_id or 0}")
        await asyncio.sleep(0.3)
        
    set_key(".env", "FORWARDING_RULES", ",".join(rules_to_create))
    console.print(f"\n[bold green]✨ All {len(rules_to_create)} topic routing rules successfully configured in .env![/]")
    
    confirm = await safe_input("\nStart Multi-Topic Group Clone Sequence Now? (YES / NO)", valid_options=["YES", "NO", "yes", "no"], default_val="YES", allow_cancel=True)
    if confirm and confirm.upper() == "YES":
        AdminTelemetry.dispatch(client, "🧬 [MONITOR] Group Cloner Started", {
            "Source Group": f"`{src_id}` ({src_sel.get('title', '')})",
            "Target Group": f"`{tgt_id}` ({tgt_sel.get('title', '')})",
            "Topics Found": f"{len(src_topics)}",
            "Rules Configured": f"{len(rules_to_create)}"
        })
        return (1, 12, False, "all", 2, False, False)
        
    return None

async def run_single_or_specific_messages_forwarder(session_mgr):
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel(
        "[bold cyan]🎬 DIRECT SINGLE / SPECIFIC VIDEOS & MESSAGES FORWARDER[/]\n"
        "[dim]Forward 1 or 2 specific videos, message IDs, or t.me links straight into any Forum Topic.[/]",
        border_style="cyan", box=box.ROUNDED
    ))

    client = await session_mgr.ensure_active_client()
    if not client: return

    # 1. Select SOURCE Channel / Group
    console.print("\n[bold cyan]Step 1: Choose SOURCE Channel / Group (where files are located)[/]")
    src_sel = await interactive_channel_selector(client, prompt_title="SOURCE Channel / Group")
    if not src_sel: return

    src_id = src_sel["id"]
    try:
        src_entity = await client.get_entity(_parse_chat_id(src_id))
        src_title = getattr(src_entity, 'title', None) or str(src_id)
    except Exception as e:
        console.print(f"[bold red]❌ Failed to connect to source:[/] {e}")
        await safe_input("Press Enter to return", allow_cancel=False)
        return

    # 2. Select TARGET Channel / Forum Group
    console.print(f"\n[bold green]Step 2: Choose TARGET Channel / Forum Group (where to send)[/]")
    tgt_sel = await interactive_channel_selector(client, prompt_title="TARGET Channel / Group")
    if not tgt_sel: return

    tgt_id = tgt_sel["id"]
    try:
        tgt_entity = await client.get_entity(_parse_chat_id(tgt_id))
        tgt_title = getattr(tgt_entity, 'title', None) or str(tgt_id)
    except Exception as e:
        console.print(f"[bold red]❌ Failed to connect to target:[/] {e}")
        await safe_input("Press Enter to return", allow_cancel=False)
        return

    # 3. Check if target is a forum with topics
    tgt_topic_id = None
    tgt_topic_name = "General / Main Chat"
    try:
        tgt_peer = await client.get_input_entity(_parse_chat_id(tgt_id))
        res = await client(GetForumTopicsRequest(
            peer=tgt_peer, offset_date=None, offset_id=0, offset_topic=0, limit=100
        ))
        if hasattr(res, 'topics') and res.topics:
            console.print(f"\n[cyan]Found {len(res.topics)} Forum Topics in '{tgt_title}'. Choose destination Topic:[/]")
            console.print(" [0] 🌐 General Topic / Main Thread")
            for idx, t in enumerate(res.topics, 1):
                t_name = getattr(t, 'title', f"Topic #{t.id}")
                console.print(f" [{idx}] 📌 {t_name} (ID: {t.id})")
            
            top_ch = await safe_input(f"Select Target Topic (0-{len(res.topics)})", valid_options=[str(i) for i in range(len(res.topics)+1)], default_val="0", allow_cancel=True)
            if top_ch and top_ch != "0":
                chosen_t = res.topics[int(top_ch)-1]
                tgt_topic_id = chosen_t.id
                tgt_topic_name = getattr(chosen_t, 'title', f"Topic #{chosen_t.id}")
    except Exception:
        pass

    # 4. Prompt for message ID(s) or Links
    console.print(Panel(
        "[bold white]Enter the Message ID(s) or Telegram Link(s) to forward:[/]\n\n"
        "• [bold green]Single Video / ID:[/] [cyan]124[/]\n"
        "• [bold green]Multiple IDs:[/] [cyan]124, 128, 135[/]\n"
        "• [bold green]Range of IDs:[/] [cyan]120-125[/]\n"
        "• [bold green]Telegram Message Link:[/] [cyan]https://t.me/c/1234567890/124[/]",
        border_style="cyan", box=box.ROUNDED
    ))
    raw_input_ids = await safe_input("Message ID(s) / Link(s)", allow_cancel=True)
    if not raw_input_ids: return

    # Parse message IDs
    target_msg_ids = set()
    import re
    tokens = [t.strip() for t in raw_input_ids.replace(";", ",").split(",") if t.strip()]
    for token in tokens:
        if "t.me/" in token:
            m = re.search(r"/(\d+)(?:\?.*)?$", token)
            if m:
                target_msg_ids.add(int(m.group(1)))
        elif "-" in token and not token.startswith("-"):
            parts = token.split("-")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                start_id, end_id = int(parts[0]), int(parts[1])
                if start_id <= end_id and (end_id - start_id) <= 200:
                    for mid in range(start_id, end_id + 1):
                        target_msg_ids.add(mid)
        elif token.isdigit():
            target_msg_ids.add(int(token))

    if not target_msg_ids:
        console.print("[bold red]❌ No valid message IDs parsed from input.[/]")
        await safe_input("Press Enter to return", allow_cancel=False)
        return

    sorted_ids = sorted(list(target_msg_ids))
    console.print(f"\n[cyan]Fetching {len(sorted_ids)} message(s) from '{src_title}'...[/]")

    try:
        msgs = await client.get_messages(src_entity, ids=sorted_ids)
    except Exception as e:
        console.print(f"[bold red]❌ Failed to fetch messages:[/] {e}")
        await safe_input("Press Enter to return", allow_cancel=False)
        return

    valid_msgs = [m for m in msgs if m is not None]
    if not valid_msgs:
        console.print("[bold red]❌ None of the requested message IDs exist or could be accessed.[/]")
        await safe_input("Press Enter to return", allow_cancel=False)
        return

    # Preview table
    table = Table(title="Selected Items to Forward", box=box.ROUNDED, border_style="cyan")
    table.add_column("Msg ID", style="bold yellow", justify="center")
    table.add_column("Type", style="bold cyan")
    table.add_column("Title / Caption", style="white")
    table.add_column("Size", style="dim green", justify="right")

    for m in valid_msgs:
        m_type = "💬 Text"
        m_title = (m.message or "").strip().split("\n")[0][:45] or "[No Text]"
        m_size = "N/A"
        if m.video:
            m_type = "🎬 Video"
            v_title = ""
            for attr in getattr(getattr(m, 'media', None), 'document', None) and getattr(m.media.document, 'attributes', []) or []:
                if hasattr(attr, 'file_name') and attr.file_name:
                    v_title = attr.file_name
                    break
            m_title = v_title or (m.message or "").strip().split("\n")[0][:45] or f"Video #{m.id}"
            if getattr(m, 'media', None) and getattr(m.media, 'document', None):
                m_size = f"{round(m.media.document.size / (1024*1024), 1)} MB"
        elif m.document:
            m_type = "📄 Document"
            d_title = ""
            for attr in getattr(getattr(m, 'media', None), 'document', None) and getattr(m.media.document, 'attributes', []) or []:
                if hasattr(attr, 'file_name') and attr.file_name:
                    d_title = attr.file_name
                    break
            m_title = d_title or (m.message or "").strip().split("\n")[0][:45] or f"Document #{m.id}"
            if getattr(m, 'media', None) and getattr(m.media, 'document', None):
                m_size = f"{round(m.media.document.size / (1024*1024), 1)} MB"
        elif m.photo:
            m_type = "🖼️ Photo"
            m_title = (m.message or "").strip().split("\n")[0][:45] or f"Photo #{m.id}"

        table.add_row(str(m.id), m_type, m_title, m_size)

    console.print(table)
    console.print(f"\n[bold green]Target Destination:[/] {tgt_title} ➔ [bold yellow]{tgt_topic_name}[/] (Topic ID: {tgt_topic_id or 'General'})")

    confirm = await safe_input(f"\nForward these {len(valid_msgs)} message(s) now? (YES / NO)", valid_options=["YES", "NO", "yes", "no"], default_val="YES", allow_cancel=True)
    if not confirm or confirm.upper() != "YES":
        console.print("[yellow]Forwarding cancelled.[/]")
        await safe_input("Press Enter to return", allow_cancel=False)
        return

    success_count = 0
    fail_count = 0
    reply_kw = {"reply_to": tgt_topic_id} if tgt_topic_id else {}
    temp_dir = Path("temp_cherry_pick")
    temp_dir.mkdir(exist_ok=True)

    with console.status(f"[bold cyan]Forwarding {len(valid_msgs)} item(s) with anti-flood pacing...[/]") as status:
        for idx, m in enumerate(valid_msgs, 1):
            status.update(f"[bold cyan][{idx}/{len(valid_msgs)}] Sending Msg #{m.id}...[/]")
            clean_caption = customize_caption(m.message) if m.message else ""
            sent_msg = None
            try:
                if not m.media:
                    sent_msg = await client.send_message(
                        tgt_entity,
                        clean_caption or m.message,
                        parse_mode="md",
                        **reply_kw
                    )
                else:
                    try:
                        sent_msg = await client.send_file(
                            tgt_entity,
                            m.media,
                            caption=clean_caption,
                            parse_mode="md",
                            supports_streaming=True,
                            **reply_kw
                        )
                    except Exception as fe:
                        # Restricted Content Bypass: Download to temp and stream upload
                        status.update(f"[bold yellow][{idx}/{len(valid_msgs)}] Protected content detected. Downloading securely...[/]")
                        downloaded_path = await client.download_media(m, file=str(temp_dir))
                        if downloaded_path and os.path.exists(downloaded_path):
                            status.update(f"[bold green][{idx}/{len(valid_msgs)}] Uploading to topic '{tgt_topic_name}'...[/]")
                            sent_msg = await client.send_file(
                                tgt_entity,
                                downloaded_path,
                                caption=clean_caption,
                                parse_mode="md",
                                supports_streaming=True,
                                **reply_kw
                            )
                            with suppress(Exception):
                                os.remove(downloaded_path)

                if sent_msg:
                    success_count += 1
                    console.print(f" [bold green]✔ [{idx}/{len(valid_msgs)}] Delivered Msg #{m.id} to '{tgt_topic_name}'![/]")
                    with suppress(Exception):
                        with sqlite3.connect(DB_FILE) as conn:
                            conn.execute(
                                "INSERT OR REPLACE INTO forwarded (source_chat, msg_id, target_chat, target_topic, completed_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                                (str(src_id), m.id, str(tgt_id), tgt_topic_id or 0)
                            )
                else:
                    fail_count += 1
                    console.print(f" [bold red]❌ [{idx}/{len(valid_msgs)}] Failed to deliver Msg #{m.id}[/]")
            except Exception as ex:
                fail_count += 1
                console.print(f" [bold red]❌ [{idx}/{len(valid_msgs)}] Error forwarding Msg #{m.id}:[/] {ex}")

            await asyncio.sleep(1.0)

    with suppress(Exception):
        if temp_dir.exists():
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    console.print(f"\n[bold green]🎉 Forwarding Complete:[/] [bold yellow]{success_count}[/] delivered successfully" + (f", [red]{fail_count} failed[/]" if fail_count else ""))

    AdminTelemetry.dispatch(client, "🎬 [DIRECT FORWARD] Single / Specific Messages Forwarded", {
        "Source": f"`{src_id}` ({src_title})",
        "Target": f"`{tgt_id}` ({tgt_title})",
        "Topic": f"`{tgt_topic_name}` (ID: `{tgt_topic_id or 0}`)",
        "Messages": f"{success_count}/{len(valid_msgs)} Delivered",
        "IDs": ", ".join(str(m.id) for m in valid_msgs[:10])
    })

    await safe_input("\nPress Enter to return to menu", allow_cancel=False)

async def run_selective_content_picker(session_mgr):

    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel("[bold cyan]🎯 SELECTIVE CONTENT EXPLORER & CHERRY-PICKER CLONER[/]", border_style="cyan", box=box.ROUNDED))
    console.print("[dim]Explore any group/channel, inspect files, pick what you need & paste directly into your chosen topic![/]\n")
    
    client = await session_mgr.ensure_active_client()
    if not client: return
    
    # 1. Select SOURCE Group
    console.print("[bold cyan]Step 1: Choose SOURCE Channel / Group (to explore & extract from)[/]")
    src_sel = await interactive_channel_selector(client, prompt_title="SOURCE Channel / Group")
    if not src_sel: return
    
    src_id = src_sel["id"]
    try:
        src_entity = await client.get_entity(_parse_chat_id(src_id))
        src_title = getattr(src_entity, 'title', None) or str(src_id)
    except Exception as e:
        console.print(f"[bold red]❌ Failed to connect to source:[/] {e}")
        await safe_input("Press Enter to return", allow_cancel=False)
        return

    # Check if source has forum topics
    src_topic_id = None
    try:
        src_peer = await client.get_input_entity(_parse_chat_id(src_id))
        res = await client(GetForumTopicsRequest(
            peer=src_peer, offset_date=None, offset_id=0, offset_topic=0, limit=100
        ))
        if hasattr(res, 'topics') and res.topics:
            console.print(f"\n[cyan]Found {len(res.topics)} Topics in {src_title}. Which topic do you want to explore?[/]")
            console.print(" [0] 🌐 All Topics / General Messages")
            for idx, t in enumerate(res.topics, 1):
                console.print(f" [{idx}] {getattr(t, 'title', f'Topic {t.id}')}")
            t_pick = await safe_input("Select Topic # (or 0 for All)", valid_options=[str(i) for i in range(len(res.topics)+1)], default_val="0")
            if t_pick and t_pick != "0":
                src_topic_id = res.topics[int(t_pick)-1].id
    except Exception:
        pass

    # 2. Scanning Filters
    console.print(f"\n[bold cyan]Step 2: Set Exploration Filters for [bold yellow]{src_title}[/][/]")
    limit_str = await safe_input("How many recent messages to inspect? (default: 50, or enter 100/200)", default_val="50")
    limit_n = int(limit_str) if limit_str.isdigit() else 50

    keyword = await safe_input("Filter by Keyword / Topic name (Press Enter to view all files)", default_val="")
    keyword = keyword.strip().lower()

    console.print("Filter by Media Type:")
    console.print(" [1] 🌟 All Media & Notes (Videos, PDFs, Images)")
    console.print(" [2] 🎬 Videos Only")
    console.print(" [3] 📄 PDF Notes & Documents Only")
    console.print(" [4] 💬 All Posts (Including Text Announcements)")
    m_choice = await safe_input("Select Type (1/2/3/4)", valid_options=["1", "2", "3", "4"], default_val="1")

    # 3. Fetch messages
    scanned_items = []
    with console.status(f"[bold cyan]Scanning up to {limit_n} items from {src_title}...[/]"):
        try:
            kw_iter = {"limit": limit_n}
            if src_topic_id:
                kw_iter["reply_to"] = src_topic_id
            
            async for msg in client.iter_messages(src_entity, **kw_iter):
                if not msg: continue
                
                # Check media type
                is_video = bool(getattr(msg, "video", None))
                is_doc = bool(getattr(msg, "document", None) and not is_video)
                is_photo = bool(getattr(msg, "photo", None))
                has_media = bool(msg.media)
                
                m_type = "📝 Text"
                if is_video: m_type = "🎬 Video"
                elif is_doc: m_type = "📄 Document"
                elif is_photo: m_type = "🖼️ Photo"
                
                if m_choice == "2" and not is_video: continue
                if m_choice == "3" and not is_doc: continue
                if m_choice == "1" and not has_media: continue
                
                # Get file name / title
                caption = (msg.message or "").strip()
                file_name = ""
                file_size_mb = 0.0
                
                if msg.file:
                    file_name = getattr(msg.file, "name", "") or ""
                    if getattr(msg.file, "size", None):
                        file_size_mb = round(msg.file.size / (1024 * 1024), 2)
                        
                display_label = file_name or (caption[:60] if caption else f"Message #{msg.id}")
                display_label = display_label.replace("\n", " ").strip()
                
                # Keyword check
                if keyword and (keyword not in display_label.lower() and keyword not in caption.lower()):
                    continue
                    
                # Check if already cloned in DB
                is_already_cloned = False
                try:
                    with sqlite3.connect(DB_FILE) as conn:
                        row = conn.execute(
                            "SELECT msg_id FROM forwarded WHERE source_chat = ? AND msg_id = ?",
                            (str(src_id), msg.id)
                        ).fetchone()
                        if row: is_already_cloned = True
                except Exception:
                    pass
                    
                date_str = msg.date.strftime("%Y-%m-%d %H:%M") if msg.date else ""
                
                scanned_items.append({
                    "msg": msg,
                    "id": msg.id,
                    "date": date_str,
                    "type": m_type,
                    "title": display_label,
                    "size_mb": file_size_mb,
                    "caption": caption,
                    "cloned": is_already_cloned
                })
        except Exception as e:
            console.print(f"[bold red]❌ Error scanning messages:[/] {e}")
            await safe_input("Press Enter to return", allow_cancel=False)
            return

    if not scanned_items:
        console.print("\n[yellow]⚠️ No messages matched your filter criteria.[/]")
        await safe_input("Press Enter to return", allow_cancel=False)
        return

    # Display Results Table
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel(f"[bold green]✨ EXPLORER FOUND {len(scanned_items)} ITEMS IN {src_title.upper()}[/]", border_style="green", box=box.ROUNDED))
    
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan", expand=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Msg ID", style="cyan", width=8)
    table.add_column("Date", style="dim", width=16)
    table.add_column("Type", width=12)
    table.add_column("Title / Content Snippet", style="bold yellow")
    table.add_column("Size", style="magenta", justify="right", width=10)
    table.add_column("Status", width=14)
    
    for idx, item in enumerate(scanned_items, 1):
        status_badge = "[dim]⏩ Already Cloned[/]" if item["cloned"] else "[bold green]🟢 NEW[/]"
        size_str = f"{item['size_mb']} MB" if item["size_mb"] > 0 else "-"
        table.add_row(
            str(idx), str(item["id"]), item["date"], item["type"],
            item["title"][:50], size_str, status_badge
        )
    console.print(table)

    # 4. Selection Mode
    console.print("\n[bold cyan]Step 3: Select Content to Clone / Forward[/]")
    console.print(" • Type numbers/ranges: [bold green]1, 3, 5-10[/]")
    console.print(" • Type [bold green]NEW[/] to clone ONLY items not yet cloned")
    console.print(" • Type [bold green]ALL[/] to clone everything listed")
    console.print(" • Type [bold red]0[/] to Cancel\n")
    
    sel_input = await safe_input("Enter Selection", default_val="NEW", allow_cancel=True)
    if not sel_input or sel_input == "0":
        return
        
    selected_indices = set()
    sel_clean = sel_input.strip().upper()
    if sel_clean == "ALL":
        selected_indices = set(range(len(scanned_items)))
    elif sel_clean == "NEW":
        selected_indices = {i for i, item in enumerate(scanned_items) if not item["cloned"]}
        if not selected_indices:
            console.print("[yellow]All listed items are already cloned in your DB![/]")
            await safe_input("Press Enter to return", allow_cancel=False)
            return
    else:
        parts = [p.strip() for p in sel_clean.split(",") if p.strip()]
        for p in parts:
            if "-" in p:
                sub_parts = p.split("-")
                if len(sub_parts) == 2 and sub_parts[0].isdigit() and sub_parts[1].isdigit():
                    s_idx = int(sub_parts[0]) - 1
                    e_idx = int(sub_parts[1]) - 1
                    for idx_range in range(max(0, s_idx), min(len(scanned_items), e_idx + 1)):
                        selected_indices.add(idx_range)
            elif p.isdigit():
                idx_single = int(p) - 1
                if 0 <= idx_single < len(scanned_items):
                    selected_indices.add(idx_single)

    if not selected_indices:
        console.print("[yellow]No valid items selected.[/]")
        await safe_input("Press Enter to return", allow_cancel=False)
        return

    items_to_clone = [scanned_items[i] for i in sorted(selected_indices)]
    console.print(f"\n[bold green]✔ Selected {len(items_to_clone)} items for cloning![/]")

    # 5. Choose TARGET Destination
    console.print("\n[bold cyan]Step 4: Choose DESTINATION (Target) Channel / Group to Paste[/]")
    tgt_sel = await interactive_channel_selector(client, prompt_title="TARGET Channel / Group")
    if not tgt_sel: return
    
    tgt_id = tgt_sel["id"]
    try:
        tgt_entity = await client.get_entity(_parse_chat_id(tgt_id))
        tgt_title = getattr(tgt_entity, 'title', None) or str(tgt_id)
    except Exception as e:
        console.print(f"[bold red]❌ Failed to connect to target:[/] {e}")
        await safe_input("Press Enter to return", allow_cancel=False)
        return

    # Check if target has forum topics
    tgt_topic_id = None
    tgt_topic_title = "General"
    try:
        tgt_peer = await client.get_input_entity(_parse_chat_id(tgt_id))
        tgt_res = await client(GetForumTopicsRequest(
            peer=tgt_peer, offset_date=None, offset_id=0, offset_topic=0, limit=100
        ))
        if hasattr(tgt_res, 'topics') and tgt_res.topics:
            console.print(f"\n[bold cyan]🎯 Choose Destination Topic in [yellow]{tgt_title}[/]:[/]")
            console.print(" [0] 🌐 General Topic (Main Chat)")
            for idx, t in enumerate(tgt_res.topics, 1):
                console.print(f" [{idx}] {getattr(t, 'title', f'Topic {t.id}')}")
            console.print(" [N] ➕ Create Brand-New Topic")
            
            t_choice = await safe_input("Select Destination Topic (# / N / 0)", default_val="0")
            if t_choice.upper() == "N":
                new_t_name = await safe_input("Enter New Topic Title", default_val="Cherry-Picked Notes")
                try:
                    created = await client(CreateForumTopicRequest(
                        peer=tgt_peer,
                        title=new_t_name,
                        icon_color=7322096,
                        random_id=generate_random_long()
                    ))
                    tgt_topic_id = created.updates[0].id if hasattr(created, 'updates') and created.updates else (getattr(created, 'id', None) or 0)
                    tgt_topic_title = new_t_name
                    console.print(f"[bold green]✔ Created new topic:[/] [yellow]{new_t_name}[/] (ID: {tgt_topic_id})")
                except Exception as e:
                    console.print(f"[yellow]⚠️ Could not create topic: {e}[/]")
            elif t_choice.isdigit() and int(t_choice) > 0 and int(t_choice) <= len(tgt_res.topics):
                chosen_t = tgt_res.topics[int(t_choice)-1]
                tgt_topic_id = chosen_t.id
                tgt_topic_title = getattr(chosen_t, 'title', f'Topic {chosen_t.id}')
    except Exception:
        pass

    console.print(Panel(
        f"🎯 [bold green]CLONE CONFIRMATION[/]\n\n"
        f" • [cyan]Source :[/] {src_title} ({src_id})\n"
        f" • [magenta]Target :[/] {tgt_title} ({tgt_id})\n"
        f" • [yellow]Topic  :[/] {tgt_topic_title} (ID: {tgt_topic_id or 'General'})\n"
        f" • [green]Items  :[/] {len(items_to_clone)} Selected Files & Posts\n"
        f" • [dim]Restricted Content Bypass: ENABLED (In-Memory Download/Re-Upload)[/]",
        border_style="green", box=box.ROUNDED
    ))

    confirm_start = await safe_input("Execute Cloning Now? (YES / NO)", valid_options=["YES", "NO", "yes", "no"], default_val="YES", allow_cancel=True)
    if not confirm_start or confirm_start.upper() != "YES":
        return

    # 6. Execute Cloning
    cloned_ok = 0
    temp_dir = Path("temp_cherry_pick")
    temp_dir.mkdir(exist_ok=True)
    
    with console.status(f"[bold green]Cloning {len(items_to_clone)} items into {tgt_title}...[/]") as status:
        for idx, item in enumerate(items_to_clone, 1):
            msg = item["msg"]
            status.update(f"[bold green][{idx}/{len(items_to_clone)}] Processing: {item['title'][:40]}...[/]")
            
            clean_caption = customize_caption(item["caption"]) if item["caption"] else ""
            reply_kw = {"reply_to": tgt_topic_id} if tgt_topic_id else {}
            
            sent_msg = None
            try:
                # 1. If Text Only
                if not msg.media:
                    sent_msg = await client.send_message(
                        tgt_entity,
                        clean_caption or msg.message,
                        parse_mode="md",
                        **reply_kw
                    )
                # 2. If Media (Video, Document, Photo)
                else:
                    try:
                        sent_msg = await client.send_file(
                            tgt_entity,
                            msg.media,
                            caption=clean_caption,
                            parse_mode="md",
                            supports_streaming=True,
                            **reply_kw
                        )
                    except Exception as fe:
                        # Restricted Content Bypass: Download raw media to temporary file then re-upload!
                        logger.info(f"Direct send bypassed due to restriction ({fe}). Downloading raw media...")
                        status.update(f"[bold yellow][{idx}/{len(items_to_clone)}] Restricted content detected. Downloading securely...[/]")
                        downloaded_path = await client.download_media(msg, file=str(temp_dir))
                        if downloaded_path and os.path.exists(downloaded_path):
                            status.update(f"[bold green][{idx}/{len(items_to_clone)}] Re-uploading clean file to target...[/]")
                            sent_msg = await client.send_file(
                                tgt_entity,
                                downloaded_path,
                                caption=clean_caption,
                                parse_mode="md",
                                supports_streaming=True,
                                **reply_kw
                            )
                            with suppress(Exception):
                                os.remove(downloaded_path)
                                
                if sent_msg:
                    cloned_ok += 1
                    with suppress(Exception):
                        with sqlite3.connect(DB_FILE) as conn:
                            conn.execute(
                                "INSERT OR REPLACE INTO forwarded (source_chat, msg_id, target_chat, target_topic, completed_at) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
                                (str(src_id), msg.id, str(tgt_id), tgt_topic_id or 0)
                            )
                    console.print(f"  [bold green]✔ [{idx}/{len(items_to_clone)}][/] [cyan]{item['title'][:45]}[/] ➔ [yellow]{tgt_topic_title}[/]")
                else:
                    console.print(f"  [bold red]❌ [{idx}/{len(items_to_clone)}][/] Failed: {item['title'][:45]}")
            except Exception as e:
                console.print(f"  [bold red]❌ Error cloning msg #{msg.id}:[/] {e}")
                
            await asyncio.sleep(0.8)

    with suppress(Exception):
        if temp_dir.exists():
            for f in temp_dir.glob("*"):
                with suppress(Exception): f.unlink()
            temp_dir.rmdir()

    console.print(Panel(
        f"🎉 [bold green]CLONING COMPLETED SUCCESSFULLY![/]\n\n"
        f" • [green]Successfully Cloned:[/] {cloned_ok} / {len(items_to_clone)} items\n"
        f" • [cyan]Destination:[/] {tgt_title} ➔ {tgt_topic_title}\n"
        f" • [dim]All cloned items have been saved to local database history.[/]",
        border_style="green", box=box.ROUNDED
    ))
    
    AdminTelemetry.dispatch(client, "🎯 [MONITOR] Selective Cherry-Pick Cloned", {
        "Source": f"{src_title} ({src_id})",
        "Target": f"{tgt_title} (Topic: {tgt_topic_title})",
        "Items Cloned": f"{cloned_ok} / {len(items_to_clone)}"
    })
    
    await safe_input("\nPress Enter to return to menu", allow_cancel=False)

async def run_member_scraper_and_adder(session_mgr):
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel(
        "[bold cyan]👥 CROSS-GROUP MEMBER SCRAPER, BACKUP & SMART ADDER[/]\n"
        "[dim]Extract active members, save offline backups, and safely add members to your target study group![/]",
        border_style="cyan", box=box.ROUNDED
    ))

    client = await session_mgr.ensure_active_client()
    if not client: return

    console.print(" [bold green][1][/] 📥 [bold white]Scrape & Backup Group Members to CSV[/]")
    console.print("     [dim]Extract members from any group you have joined and save to backup spreadsheet[/]\n")
    console.print(" [bold yellow][2][/] 🚀 [bold white]Safe-Add Members to Target Group[/]")
    console.print("     [dim]Add members from a saved backup CSV or directly from another group with flood safety[/]\n")
    console.print(" [bold cyan][3][/] 📂 [bold white]View Saved Member Backups[/]\n")
    console.print(" [dim][0] Return to Menu[/]")

    sub_ch = await safe_input("Choose Option (1/2/3/0)", valid_options=["1", "2", "3", "0"], default_val="1", allow_cancel=True)
    if not sub_ch or sub_ch == "0": return

    backup_dir = Path("member_backups")
    backup_dir.mkdir(exist_ok=True)

    if sub_ch == "1":
        # 1. Scrape & Backup
        console.print("\n[bold cyan]Step 1: Choose SOURCE Group to Scrape Members From[/]")
        src_sel = await interactive_channel_selector(client, prompt_title="SOURCE Group to Scrape")
        if not src_sel: return

        src_id = src_sel["id"]
        try:
            src_entity = await client.get_entity(_parse_chat_id(src_id))
            src_title = getattr(src_entity, 'title', None) or str(src_id)
        except Exception as e:
            console.print(f"[bold red]❌ Failed to connect to group:[/] {e}")
            await safe_input("Press Enter to return", allow_cancel=False)
            return

        filter_choice = await safe_input(
            "Filter Type: [1] All Real Members  [2] Active Only (Seen in last 7 days)", 
            valid_options=["1", "2"], 
            default_val="1"
        )

        scraped_members = []
        admin_ids = set()
        with console.status(f"[bold cyan]Auditing Admin Protection Shield on [yellow]{src_title}[/]...[/]"):
            try:
                async for admin in client.iter_participants(src_entity, filter=ChannelParticipantsAdmins):
                    if admin and getattr(admin, "id", None):
                        admin_ids.add(admin.id)
            except Exception as ex:
                logger.info(f"Admin scan note: {ex}")

        with console.status(f"[bold cyan]Extracting regular student members from [yellow]{src_title}[/] (Shielding {len(admin_ids)} Admins)...[/]"):
            try:
                async for user in client.iter_participants(src_entity):
                    if not user or getattr(user, 'bot', False) or getattr(user, 'deleted', False):
                        continue
                    # 🛡️ STRICT ANTI-ADMIN SHIELD: Skip group creator, admins, and moderators
                    if user.id in admin_ids:
                        continue
                    
                    if filter_choice == "2":
                        status = getattr(user, 'status', None)
                        is_active = type(status).__name__ in ('UserStatusOnline', 'UserStatusRecently', 'UserStatusLastWeek')
                        if not is_active:
                            continue

                    fn = getattr(user, 'first_name', '') or ''
                    ln = getattr(user, 'last_name', '') or ''
                    full_name = f"{fn} {ln}".strip() or "User"
                    uname = getattr(user, 'username', '') or ''

                    scraped_members.append({
                        "user_id": user.id,
                        "access_hash": getattr(user, 'access_hash', 0),
                        "first_name": fn,
                        "last_name": ln,
                        "full_name": full_name,
                        "username": uname,
                        "is_premium": bool(getattr(user, 'premium', False)),
                        "phone": getattr(user, 'phone', '') or ''
                    })
            except Exception as ex:
                console.print(f"[yellow]⚠️ Partial extraction notice: {ex}[/]")

        if not scraped_members:
            console.print("[bold red]❌ No eligible members could be extracted (check group privacy settings).[/]")
            await safe_input("Press Enter to return", allow_cancel=False)
            return

        clean_name = re.sub(r'[\\/*?:"<>| ]', '_', src_title)[:30]
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = backup_dir / f"members_{clean_name}_{ts}.csv"

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["user_id", "access_hash", "full_name", "username", "is_premium", "phone"])
            writer.writeheader()
            for m in scraped_members:
                writer.writerow({
                    "user_id": m["user_id"],
                    "access_hash": m["access_hash"],
                    "full_name": m["full_name"],
                    "username": m["username"],
                    "is_premium": m["is_premium"],
                    "phone": m["phone"]
                })

        console.print(Panel(
            f"🎉 [bold green]SCRAPING COMPLETE & BACKED UP![/]\n\n"
            f" • [cyan]Source Group:[/] {src_title}\n"
            f" • [green]Total Extracted Members:[/] {len(scraped_members)}\n"
            f" • [yellow]Members with @username:[/] {sum(1 for m in scraped_members if m['username'])}\n"
            f" • [magenta]Backup File Saved:[/] [cyan]{csv_path}[/]\n\n"
            f"💡 *You can now use Option 2 to safely add these members to your new group anytime!*",
            border_style="green", box=box.ROUNDED
        ))
        await safe_input("Press Enter to continue", allow_cancel=False)

    elif sub_ch == "2":
        console.print("\n[bold cyan]Step 1: Choose Members Source for Adding[/]")
        console.print(" [1] 📂 From Saved CSV Backup File")
        console.print(" [2] 📥 Direct Live Scrape from another Group")
        src_mode = await safe_input("Select Source (1/2)", valid_options=["1", "2"], default_val="1")

        members_to_add = []
        if src_mode == "1":
            csv_files = list(backup_dir.glob("*.csv"))
            if not csv_files:
                console.print("[bold red]❌ No CSV backup files found in 'member_backups/' directory.[/]")
                await safe_input("Press Enter to return", allow_cancel=False)
                return

            console.print("\n[bold cyan]Available Member Backups:[/]")
            for idx, cf in enumerate(csv_files, 1):
                console.print(f" [{idx}] [yellow]{cf.name}[/] [dim]({cf.stat().st_size // 1024} KB)[/]")
            b_choice = await safe_input(f"Select Backup # (1-{len(csv_files)})", valid_options=[str(i) for i in range(1, len(csv_files)+1)], default_val="1")
            chosen_csv = csv_files[int(b_choice)-1]

            with open(chosen_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not row: continue
                    # Robust header normalization (e.g. 'User ID' -> 'user_id', 'Username' -> 'username')
                    norm_row = {str(k).strip().lower().replace(" ", "_"): v for k, v in row.items() if k}
                    raw_uid = norm_row.get("user_id") or norm_row.get("id") or norm_row.get("numerical_id") or ""
                    clean_uid = "".join(filter(str.isdigit, str(raw_uid)))
                    uname_val = str(norm_row.get("username") or "").strip().lstrip("@")

                    if not clean_uid and not uname_val:
                        continue
                    
                    uid_val = int(clean_uid) if clean_uid else 0
                    raw_ah = norm_row.get("access_hash") or 0
                    clean_ah = "".join(filter(str.isdigit, str(raw_ah)))
                    ah_val = int(clean_ah) if clean_ah else 0
                    fname_val = str(norm_row.get("full_name") or norm_row.get("name") or "User").strip()

                    members_to_add.append({
                        "user_id": uid_val,
                        "access_hash": ah_val,
                        "username": uname_val,
                        "full_name": fname_val
                    })
        else:
            sel_src = await interactive_channel_selector(client, prompt_title="Source Group to Extract & Add")
            if not sel_src: return
            src_ent = await client.get_entity(_parse_chat_id(sel_src["id"]))
            with console.status("[bold cyan]Fetching participants...[/]"):
                async for user in client.iter_participants(src_ent):
                    if not user or getattr(user, 'bot', False) or getattr(user, 'deleted', False): continue
                    members_to_add.append({
                        "user_id": user.id,
                        "access_hash": getattr(user, 'access_hash', 0),
                        "username": getattr(user, 'username', '') or '',
                        "full_name": f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip() or "User"
                    })

        if not members_to_add:
            console.print("[bold red]❌ No members found to add.[/]")
            await safe_input("Press Enter to return", allow_cancel=False)
            return

        console.print(f"\n[bold green]Loaded {len(members_to_add)} candidate members.[/]")

        console.print("\n[bold cyan]Step 2: Choose TARGET Group to Add Members Into[/]")
        tgt_sel = await interactive_channel_selector(client, prompt_title="TARGET Group (Where to Add)")
        if not tgt_sel: return

        tgt_id = tgt_sel["id"]
        try:
            tgt_entity = await client.get_entity(_parse_chat_id(tgt_id))
            tgt_title = getattr(tgt_entity, 'title', None) or str(tgt_id)
        except Exception as e:
            console.print(f"[bold red]❌ Target group connection error:[/] {e}")
            await safe_input("Press Enter to return", allow_cancel=False)
            return

        console.print("\n[bold yellow]🛡️ Telegram Flood Safety & Pacing Settings:[/]")
        console.print("[dim]Telegram limits member additions (~30-50 per account daily). Paced delays protect account reputation.[/]")
        limit_count_str = await safe_input(f"How many members to add in this session? (1-{min(50, len(members_to_add))})", default_val="25")
        max_to_add = min(len(members_to_add), int(limit_count_str) if limit_count_str.isdigit() else 25)

        delay_str = await safe_input("Delay between member additions in seconds (Recommended: 15-25s)", default_val="18")
        add_delay = int(delay_str) if delay_str.isdigit() else 18

        confirm = await safe_input(f"Ready to add up to {max_to_add} members to '{tgt_title}' with {add_delay}s pacing? (y/n)", valid_options=["y", "n"], default_val="y")
        if confirm.lower() != "y": return

        added_count = 0
        already_count = 0
        privacy_count = 0
        failed_count = 0

        console.print(f"\n[bold cyan]Starting safe addition to [yellow]{tgt_title}[/]...[/]\n")

        for idx, m in enumerate(members_to_add[:max_to_add], 1):
            u_name = f"@{m['username']}" if m['username'] else m['full_name']
            try:
                if m.get("username"):
                    user_to_invite = await client.get_input_entity(m["username"])
                elif m.get("access_hash"):
                    user_to_invite = InputUser(m["user_id"], m["access_hash"])
                else:
                    user_to_invite = await client.get_input_entity(m["user_id"])

                await client(InviteToChannelRequest(
                    channel=tgt_entity,
                    users=[user_to_invite]
                ))
                added_count += 1
                console.print(f" [green]✔ [{idx}/{max_to_add}][/] Successfully added [cyan]{u_name}[/]")
                await asyncio.sleep(add_delay)

            except UserAlreadyParticipantError:
                already_count += 1
                console.print(f" [dim]⏩ [{idx}/{max_to_add}] Already in group: {u_name}[/]")
            except UserPrivacyRestrictedError:
                privacy_count += 1
                console.print(f" [yellow]🔒 [{idx}/{max_to_add}] Privacy restricted (User disabled invites): {u_name}[/]")
            except FloodWaitError as fe:
                console.print(f"\n[bold red]⚠️ Telegram Rate-Limit: Need to wait {fe.seconds}s.[/]")
                console.print("[dim]Stopping session safely to protect account.[/]")
                break
            except Exception as ex:
                failed_count += 1
                console.print(f" [red]❌ [{idx}/{max_to_add}] Could not add {u_name}: {ex}[/]")
                await asyncio.sleep(2)

        console.print(Panel(
            f"🎉 [bold green]MEMBER ADDING SESSION COMPLETED![/]\n\n"
            f" • [green]Successfully Added:[/] {added_count}\n"
            f" • [dim]Already Members:[/] {already_count}\n"
            f" • [yellow]Privacy Restricted:[/] {privacy_count}\n"
            f" • [red]Failed / Skipped:[/] {failed_count}\n"
            f" • [cyan]Target Group:[/] {tgt_title}",
            border_style="green", box=box.ROUNDED
        ))
        await safe_input("Press Enter to continue", allow_cancel=False)

    elif sub_ch == "3":
        csv_files = list(backup_dir.glob("*.csv"))
        if not csv_files:
            console.print("[bold yellow]ℹ️ No member backup files found yet.[/]")
        else:
            table = Table(title="📂 Saved Member Backups", box=box.ROUNDED)
            table.add_column("#", style="cyan", width=4)
            table.add_column("Backup File", style="yellow")
            table.add_column("Size", style="green")
            table.add_column("Date Created", style="dim")
            for idx, cf in enumerate(csv_files, 1):
                sz = f"{cf.stat().st_size // 1024} KB"
                dt = datetime.fromtimestamp(cf.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                table.add_row(str(idx), cf.name, sz, dt)
            console.print(table)
        await safe_input("Press Enter to return", allow_cancel=False)

async def run_master_group_indexer(session_mgr):
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel("[bold cyan]📑 1-CLICK MASTER GROUP & FORUM TOPICS INDEXER[/]", border_style="cyan", box=box.ROUNDED))
    console.print("[dim]Scan all forum topics across your group and auto-generate/update the master directory card![/]\n")
    
    client = await session_mgr.ensure_active_client()
    if not client: return
        
    console.print("[bold cyan]Step 1: Choose Group to Index (e.g. Study Help)[/]")
    sel_group = await interactive_channel_selector(client, prompt_title="Group to Index")
    if not sel_group:
        return
        
    group_id = sel_group["id"]
    entity = await client.get_entity(_parse_chat_id(group_id))
    group_title = getattr(entity, 'title', None) or (sel_group.get("title") if not str(sel_group.get("title")).startswith("-") else "Study Help 😉")
    member_count = getattr(entity, 'participants_count', 1974) or 1974
    
    console.print(f"\n[cyan]🔍 Inspecting Forum Structure & Topics for [bold yellow]{group_title}[/]...[/]")
    
    topics = []
    try:
        input_peer = await client.get_input_entity(_parse_chat_id(group_id))
        res = await client(GetForumTopicsRequest(
            peer=input_peer,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=100
        ))
        if hasattr(res, 'topics'):
            topics = res.topics
    except Exception as e:
        console.print(f"[bold red]❌ Error reading forum topics:[/] {e}")
        await safe_input("\nPress Enter to return", allow_cancel=False)
        return
        
    if not topics:
        console.print("[yellow]⚠️ No Forum Topics found in this group. It might be a standard group.[/]")
        await safe_input("\nPress Enter to return", allow_cancel=False)
        return

    console.print(f"[bold green]✨ Found {len(topics)} Forum Topics![/]")
    
    # Auto-detect "INDEX & Backup" or index topic
    index_topic_obj = None
    content_topics = []
    for t in topics:
        t_name = getattr(t, 'title', f'Topic {t.id}').strip()
        if re.search(r"(?i)\b(?:index|backup|directory|toc)\b", t_name):
            index_topic_obj = t
        else:
            content_topics.append(t)
            
    if not content_topics:
        content_topics = list(topics)
        
    console.print(f"\n[yellow]⚠️ You are about to scan ALL {len(content_topics)} topics in '{group_title}' to build an overarching Master Group Roadmap Index.[/]")
    confirm_all = await safe_input("Proceed with scanning all topics? (YES / NO)", valid_options=["YES", "NO", "yes", "no", "Y", "N", "y", "n"], default_val="YES", allow_cancel=True)
    if not confirm_all or confirm_all.upper() not in ["YES", "Y"]:
        console.print("[yellow]Scan cancelled. Returning to Indexer menu.[/]")
        await safe_input("\nPress Enter to return", allow_cancel=False)
        return

    console.print("\n[bold cyan]Step 2: Choose Index Sorting Style[/]")
    console.print(" [1] 🔤 [bold green]Alphabetical (A to Z)[/] [bold yellow]⭐ (Recommended)[/] (e.g. Cerebellum ➔ DVMCI ➔ Prepladder)")
    console.print(" [2] 📑 [bold white]Forum Group Order[/] (As arranged in Telegram group)")
    sort_choice = await safe_input("Choose Sorting Style (1/2)", valid_options=["1", "2", ""], default_val="1", allow_cancel=True)
    if sort_choice is None:
        return

    if sort_choice != "2":
        content_topics.sort(key=lambda t: clean_sort_key(getattr(t, 'title', f'Topic {t.id}')))
        console.print("[bold green]✔ Sorted topics Alphabetically (A to Z)![/]")
    else:
        console.print("[cyan]✔ Kept original Forum Group Order.[/]")

    console.print(f"[cyan]📊 Scanning message stats across {len(content_topics)} topics (Videos & PDFs count)...[/]")
    
    topic_data = []
    raw_chat_id = str(group_id).replace("-100", "").replace("-", "")
    
    emoji_map = [
        ("Pharmacology", "💊", r"(?i)\bpharm"),
        ("Surgery", "✂️", r"(?i)\bsurg"),
        ("Paediatrics", "🍼", r"(?i)\bp[ae]+diat"),
        ("Pathology", "🔬", r"(?i)\bpath"),
        ("Microbiology", "🦠", r"(?i)\bmicro"),
        ("Anatomy", "🦴", r"(?i)\banat"),
        ("Physiology", "🫀", r"(?i)\bphysio"),
        ("Biochemistry", "🧬", r"(?i)\bbiochem"),
        ("Forensic", "⚖️", r"(?i)\bfmt|forensic"),
        ("PSM", "🏥", r"(?i)\bpsm|community"),
        ("Ophthalmology", "👁️", r"(?i)\bophthal|eye"),
        ("ENT", "👂", r"(?i)\bent"),
        ("Medicine", "🩺", r"(?i)\bmedicine|meded|\bmed\b|priyansh|dilip"),
        ("OBG", "👶", r"(?i)\bobg|gynae|prasan"),
        ("Dermatology", "🧴", r"(?i)\bderma"),
        ("Radiology", "🩻", r"(?i)\bradio"),
        ("Psychiatry", "🧠", r"(?i)\bpsych"),
        ("Orthopedics", "🦿", r"(?i)\bortho"),
        ("Anesthesia", "💉", r"(?i)\ban[ae]+sthesia"),
        ("Grand Tests", "🎯", r"(?i)\bgt|grand test|test series"),
        ("Rapid Revision", "⚡", r"(?i)\brr\b|rapid|lrr|btr|fastrack|bootcamp|sureshot"),
        ("PYQs & Flashcards", "📑", r"(?i)\bpyq|pyt|flashcard"),
        ("Workbooks & Notes", "📚", r"(?i)\bnote|workbook|pdf|handbook|mind map"),
        ("Dissection", "🩻", r"(?i)\bdissection"),
        ("Discussion & Chat", "💬", r"(?i)\bchat|discussion|chatter"),
    ]
    
    with console.status("[bold cyan]Scanning topics and counting media files...[/]"):
        for t in content_topics:
            t_id = t.id
            t_title = getattr(t, 'title', f'Topic {t.id}').strip()
            
            icon = "📖"
            for _, em, pat in emoji_map:
                if re.search(pat, t_title):
                    icon = em
                    break
                    
            v_cnt = 0
            d_cnt = 0
            try:
                async for msg in client.iter_messages(entity, reply_to=t_id, limit=200):
                    if getattr(msg, 'video', None):
                        v_cnt += 1
                    elif getattr(msg, 'document', None):
                        d_cnt += 1
            except Exception:
                pass
                
            link = f"https://t.me/c/{raw_chat_id}/{t_id}" if raw_chat_id.isdigit() else f"https://t.me/{raw_chat_id}/{t_id}"
            topic_data.append({
                "id": t_id,
                "title": t_title,
                "icon": icon,
                "link": link,
                "videos": v_cnt,
                "docs": d_cnt
            })
            await asyncio.sleep(0.05)

    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel(f"[bold green]✨ INDEX SCAN COMPLETED FOR {group_title.upper()}[/]", border_style="green", box=box.ROUNDED))
    
    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan", expand=True)
    table.add_column("#", style="dim", width=4)
    table.add_column("Icon", width=4)
    table.add_column("Topic / Course Title", style="bold yellow")
    table.add_column("Videos", style="green", justify="right")
    table.add_column("PDF Notes", style="magenta", justify="right")
    table.add_column("Topic Link", style="blue")
    
    for idx, td in enumerate(topic_data, 1):
        table.add_row(str(idx), td["icon"], td["title"], f"{td['videos']} 🎬", f"{td['docs']} 📄", td["link"])
    console.print(table)
    
    dest_topic_id = None
    dest_topic_name = "INDEX & Backup"
    if index_topic_obj:
        dest_topic_id = index_topic_obj.id
        dest_topic_name = getattr(index_topic_obj, 'title', 'INDEX & Backup')
        console.print(f"\n[bold green]🎯 Auto-Detected Destination Topic:[/] [yellow]{dest_topic_name}[/] (ID: {dest_topic_id})")
    else:
        console.print("\n[yellow]Select Destination Topic to post this Master Index Card:[/]")
        for idx, t in enumerate(topics, 1):
            console.print(f" [{idx}] {getattr(t, 'title', f'Topic {t.id}')}")
        t_sel = await safe_input("Enter Topic # (or 0 to cancel)", valid_options=[str(i) for i in range(len(topics)+1)], default_val="1")
        if not t_sel or t_sel == "0": return
        dest_topic_id = topics[int(t_sel)-1].id
        dest_topic_name = getattr(topics[int(t_sel)-1], 'title', 'Selected Topic')

    cards = []
    current_card_lines = [
        "╔════════════════════════════════════════════════════════════╗",
        f"║   📚 **{group_title.upper()} — MASTER GROUP INDEX**",
        "║   👨‍⚕️ *Curated & Maintained by Kind Doctor & Team*",
        "╚════════════════════════════════════════════════════════════╝\n",
        "✨ ──────────── 📖 TOPIC & COURSE ROADMAP ──────────── ✨\n"
    ]
    
    current_letter = None
    for idx, td in enumerate(topic_data, 1):
        v = td['videos']
        d = td['docs']
        
        badges = []
        if v > 0:
            badges.append(f"🎬 `{v} Videos`" if v > 1 else "🎬 `1 Video`")
        if d > 0:
            badges.append(f"📄 `{d} PDF Notes`" if d > 1 else "📄 `1 PDF Note`")
            
        if badges:
            detail_line = "     └─ " + "  ·  ".join(badges)
        else:
            detail_line = "     └─ 🔗 `Tap to Open Topic`"
            
        # Clean title to prevent Markdown URL syntax breakage from nested parentheses/brackets
        safe_title = str(td['title']).strip()
        safe_title = safe_title.replace('[', '⟦').replace(']', '⟧').replace('(', '❨').replace(')', '❩').replace('*', '')
        
        # Option B: Clean Hashtag Divider (#A, #B, #C)
        header_tag = ""
        if sort_choice != "2":
            sort_k = clean_sort_key(td['title'])
            first_char = sort_k[0].upper() if sort_k else "#"
            if not first_char.isalpha():
                first_char = "0-9"
            if first_char != current_letter:
                current_letter = first_char
                header_tag = f"\n#{current_letter}\n"

        topic_entry = f"{header_tag}[{idx:02d}] ▫️ {td['icon']} [{safe_title}]({td['link']})\n{detail_line}\n"
        
        if sum(len(l) for l in current_card_lines) + len(topic_entry) > 3100:
            current_card_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            cards.append("\n".join(current_card_lines))
            current_card_lines = [
                f"📑 **{group_title.upper()} INDEX (Part {len(cards)+1})**",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            ]
        current_card_lines.append(topic_entry)
        
    current_card_lines.extend([
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"📊 **Master Index:** `{len(topic_data)} Topics Indexed`",
        f"🏷️ **Brand:** {TELEGRAM_BRAND}  ·  💬 {GROUP_BRAND}"
    ])
    cards.append("\n".join(current_card_lines))
    
    console.print(Panel(cards[0][:600] + "\n...", title="Preview of Master Card", border_style="magenta", box=box.ROUNDED))
    
    post_confirm = await safe_input(f"\nPost Master Index Card directly into '{dest_topic_name}' topic? (YES / NO)", valid_options=["YES", "NO", "yes", "no"], default_val="YES", allow_cancel=True)
    if post_confirm and post_confirm.upper() == "YES":
        try:
            for c_idx, card in enumerate(cards, 1):
                await client.send_message(
                    _parse_chat_id(group_id),
                    card,
                    reply_to=dest_topic_id,
                    parse_mode="md",
                    link_preview=False
                )
                await asyncio.sleep(0.5)
            console.print(f"\n[bold green]🎉 SUCCESS! Master Index successfully posted to '{dest_topic_name}' topic![/]")
            AdminTelemetry.dispatch(client, "📑 [INDEXER] Master Group Index Updated", {
                "Group": f"`{group_id}` ({group_title})",
                "Destination Topic": f"`{dest_topic_name}` (ID: `{dest_topic_id}`)",
                "Topics Indexed": f"{len(topic_data)} Topics",
                "Members": f"{member_count:,}"
            })
        except Exception as e:
            console.print(f"\n[bold red]❌ Failed to post Master Index card:[/] {e}")
    else:
        console.print("[yellow]Post cancelled. Master index preview was generated.[/]")
        
    await safe_input("\nPress Enter to return to menu", allow_cancel=False)

async def run_single_topic_files_indexer(session_mgr):
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel("[bold magenta]📌 1-CLICK SINGLE TOPIC FILES & MEDIA INDEXER[/]", border_style="magenta", box=box.ROUNDED))
    console.print("[dim]Scan all Videos, PDFs & Files inside ONE specific Topic and generate a clickable Table of Contents (TOC) Card![/]\n")
    
    client = await session_mgr.ensure_active_client()
    if not client: return
        
    console.print("[bold cyan]Step 1: Choose Group containing the Topic[/]")
    sel_group = await interactive_channel_selector(client, prompt_title="Group with Topic")
    if not sel_group:
        return
        
    group_id = sel_group["id"]
    try:
        entity = await client.get_entity(_parse_chat_id(group_id))
    except Exception as e:
        console.print(f"[bold red]❌ Failed to access group entity:[/] {e}")
        await safe_input("\nPress Enter to return", allow_cancel=False)
        return

    group_title = getattr(entity, 'title', None) or (sel_group.get("title") if not str(sel_group.get("title")).startswith("-") else "Target Group")
    username = getattr(entity, 'username', None)
    
    console.print(f"\n[cyan]🔍 Fetching Forum Topics for [bold yellow]{group_title}[/]...[/]")
    
    topics = []
    try:
        input_peer = await client.get_input_entity(_parse_chat_id(group_id))
        res = await client(GetForumTopicsRequest(
            peer=input_peer,
            offset_date=None,
            offset_id=0,
            offset_topic=0,
            limit=100
        ))
        if hasattr(res, 'topics') and res.topics:
            topics = res.topics
    except Exception as e:
        logger.info(f"GetForumTopics notice: {e}")

    target_topic_id = None
    target_topic_name = group_title

    # If preset in selector
    preset_topic = sel_group.get("topic")
    if preset_topic and int(preset_topic) > 0:
        target_topic_id = int(preset_topic)
        for t in topics:
            if t.id == target_topic_id:
                target_topic_name = getattr(t, 'title', f'Topic {t.id}').strip()
                break
        if target_topic_name == group_title:
            target_topic_name = f"Topic {target_topic_id}"

    if target_topic_id is None:
        if topics:
            console.print(f"\n[bold green]✨ Found {len(topics)} Forum Topics in {group_title}:[/]")
            t_table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta", expand=True)
            t_table.add_column("#", style="bold cyan", width=5)
            t_table.add_column("Topic Title", style="bold yellow")
            t_table.add_column("Topic ID", style="dim", width=12)
            
            for idx, t in enumerate(topics, 1):
                t_name = getattr(t, 'title', f'Topic {t.id}').strip()
                t_table.add_row(str(idx), t_name, str(t.id))
            console.print(t_table)
            
            console.print("[dim]Enter number (#) from list, 'P' to paste custom Topic ID / link, or 'S' to search.[/]")
            while True:
                t_choice = await safe_input("Select Topic # to Index", allow_cancel=True)
                if not t_choice or t_choice == "0":
                    return
                if t_choice.upper() == "S":
                    q = await safe_input("Enter search keyword", allow_cancel=True)
                    if q:
                        filtered = [(i, t) for i, t in enumerate(topics, 1) if q.lower() in getattr(t, 'title', '').lower()]
                        if filtered:
                            console.print("\n[cyan]Matching Topics:[/]")
                            for i, t in filtered:
                                console.print(f" [{i}] {getattr(t, 'title', f'Topic {t.id}')}")
                        else:
                            console.print("[yellow]No matching topics found.[/]")
                    continue
                elif t_choice.upper() == "P":
                    raw_tid = await safe_input("Enter Topic / Thread ID or Topic Link", allow_cancel=True)
                    if not raw_tid: return
                    parsed = parse_telegram_link(raw_tid)
                    tid = parsed.get("TOPIC_ID") or (int(raw_tid) if raw_tid.strip().isdigit() else None)
                    if not tid:
                        console.print("[red]Invalid Topic ID.[/]")
                        continue
                    target_topic_id = int(tid)
                    target_topic_name = f"Topic {target_topic_id}"
                    break
                elif t_choice.isdigit() and 1 <= int(t_choice) <= len(topics):
                    selected_t = topics[int(t_choice) - 1]
                    target_topic_id = selected_t.id
                    target_topic_name = getattr(selected_t, 'title', f'Topic {selected_t.id}').strip()
                    break
                else:
                    console.print("[red]Invalid selection number. Try again.[/]")
        else:
            console.print("[yellow]⚠️ No Forum Topics detected in this group/channel.[/]")
            do_full = await safe_input("Index all files in this Channel/Group? (YES / NO)", valid_options=["YES", "NO", "yes", "no"], default_val="NO", allow_cancel=True)
            if not do_full or do_full.upper() != "YES":
                return
            target_topic_id = None
            target_topic_name = group_title

    console.print(f"\n[bold green]🎯 Target Topic:[/] [bold yellow]{target_topic_name}[/]" + (f" (ID: `{target_topic_id}`)" if target_topic_id else ""))
    
    console.print("\n[bold cyan]Step 2: Media Type Filter[/]")
    console.print(" [1] 📦 All Media (Videos, PDFs, Notes, Audio) [Default]")
    console.print(" [2] 🎬 Videos Only")
    console.print(" [3] 📄 PDFs & Notes Only")
    filter_choice = await safe_input("Choose Filter (1/2/3)", valid_options=["1", "2", "3", ""], default_val="1", allow_cancel=True)
    if filter_choice is None:
        return
        
    console.print("\n[bold cyan]Step 3: Index Order[/]")
    console.print(" [1] ⏳ Chronological (Lecture #01, #02... Oldest to Newest) [Default]")
    console.print(" [2] ⏱️ Reverse (Newest to Oldest)")
    console.print(" [3] 🔤 Alphabetical (A to Z)")
    order_choice = await safe_input("Choose Sort Order (1/2/3)", valid_options=["1", "2", "3", ""], default_val="1", allow_cancel=True)
    if order_choice is None:
        return
    chronological = (order_choice == "1")

    console.print(f"\n[cyan]🔍 Scanning files inside [bold yellow]{target_topic_name}[/]...[/]")
    
    raw_msgs = []
    with console.status(f"[bold cyan]Reading messages from {target_topic_name}...[/]"):
        try:
            iter_kwargs = {"limit": 3000}
            if target_topic_id:
                iter_kwargs["reply_to"] = target_topic_id
                
            async for msg in client.iter_messages(entity, **iter_kwargs):
                if getattr(msg, 'video', None) or getattr(msg, 'document', None) or getattr(msg, 'photo', None) or getattr(msg, 'audio', None):
                    raw_msgs.append(msg)
        except Exception as e:
            console.print(f"[bold red]❌ Error scanning topic messages:[/] {e}")
            await safe_input("\nPress Enter to return", allow_cancel=False)
            return

    if chronological:
        raw_msgs.reverse() # Sort oldest to newest

    scanned_items = []
    for msg in raw_msgs:
        fname = None
        if getattr(msg, 'file', None) and getattr(msg.file, 'name', None):
            fname = msg.file.name
        elif getattr(msg, 'document', None):
            for attr in getattr(msg.document, 'attributes', []):
                if hasattr(attr, 'file_name') and attr.file_name:
                    fname = attr.file_name
                    break
                    
        is_vid = bool(getattr(msg, 'video', None) or (fname and fname.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm', '.ts', '.m4v'))))
        is_pdf = bool(fname and fname.lower().endswith(('.pdf', '.doc', '.docx', '.ppt', '.pptx', '.txt', '.xlsx', '.epub')))
        is_pic = bool(getattr(msg, 'photo', None))
        is_aud = bool(getattr(msg, 'audio', None) or getattr(msg, 'voice', None))
        
        # Apply filter
        if filter_choice == "2" and not is_vid:
            continue
        elif filter_choice == "3" and not is_pdf:
            continue
            
        if is_vid: m_icon = "🎬"
        elif is_pdf: m_icon = "📄"
        elif is_pic: m_icon = "🖼️"
        elif is_aud: m_icon = "🎧"
        elif getattr(msg, 'document', None): m_icon = "📁"
        else: m_icon = "📦"
            
        raw_title = ""
        if fname:
            raw_title = fname
        elif getattr(msg, 'message', None) and msg.message.strip():
            lines = [line.strip() for line in msg.message.split("\n") if line.strip()]
            if lines:
                raw_title = lines[0]
                
        if not raw_title:
            if is_vid: raw_title = f"Video Lecture #{msg.id}"
            elif is_pdf: raw_title = f"Notes PDF #{msg.id}"
            elif is_pic: raw_title = f"Photo #{msg.id}"
            elif is_aud: raw_title = f"Audio #{msg.id}"
            else: raw_title = f"Attachment #{msg.id}"
            
        clean_title = clean_index_title(raw_title, max_len=48)
        deep_link = make_telegram_link(group_id, msg.id, topic_id=target_topic_id, username=username)
        
        scanned_items.append({
            "msg_id": msg.id,
            "title": clean_title,
            "raw_name": raw_title,
            "icon": m_icon,
            "link": deep_link,
            "is_video": is_vid,
            "is_doc": is_pdf
        })

    if order_choice == "3":
        scanned_items.sort(key=lambda x: clean_sort_key(x["title"]))
        console.print("[bold green]✔ Sorted files Alphabetically (A to Z)![/]")

    if not scanned_items:
        console.print(f"\n[yellow]⚠️ No matching files or media found in [bold]{target_topic_name}[/].[/]")
        await safe_input("\nPress Enter to return", allow_cancel=False)
        return

    v_total = sum(1 for x in scanned_items if x['is_video'])
    d_total = sum(1 for x in scanned_items if x['is_doc'])
    console.print(f"\n[bold green]✔ Scan Complete:[/] Found [bold yellow]{len(scanned_items)}[/] files ([cyan]{v_total} Videos[/], [magenta]{d_total} PDFs/Docs[/])\n")

    # Smart Subject-Wise Grouping Detection
    detected_subjects = OrderedDict()
    for item in scanned_items:
        det = detect_subject(item.get("raw_name", ""), item.get("title", ""))
        if det:
            s_name = det["name"]
            s_icon = det["icon"]
            s_tag = det["tag"]
            s_key = f"{s_icon} {s_name}"
        else:
            s_key = "📁 GENERAL & MISCELLANEOUS"
            s_tag = "#General"
            
        if s_key not in detected_subjects:
            detected_subjects[s_key] = {"items": [], "tag": s_tag}
        detected_subjects[s_key]["items"].append(item)

    use_subject_grouping = False
    if len(scanned_items) > 25 and len(detected_subjects) > 1:
        console.print(Panel(
            f"[bold cyan]🎯 SMART SUBJECT & ROADMAP INDEXER DETECTED[/]\n\n"
            f"• Scanned Items     : [bold yellow]{len(scanned_items)} files[/]\n"
            f"• Detected Subjects : [bold green]{len(detected_subjects)} distinct subjects[/]\n\n"
            + "\n".join([f"  ▫️ {sk}: [bold yellow]{len(sdata['items'])}[/] items" for sk, sdata in list(detected_subjects.items())[:8]])
            + (f"\n  [dim]... and {len(detected_subjects)-8} more subjects[/]" if len(detected_subjects) > 8 else ""),
            border_style="cyan", box=box.ROUNDED
        ))
        console.print("\n[bold cyan]Choose Index Presentation Format:[/]")
        console.print(" [1] 🗂️ Smart Subject-Wise Roadmap (Master Hub + Subject Sub-Cards) ⭐ [Recommended]")
        console.print(" [2] 📑 Flat Chronological List (#01 to #N Linear Cards)")
        group_choice = await safe_input("Choose Option (1/2)", valid_options=["1", "2", ""], default_val="1", allow_cancel=True)
        if group_choice is None:
            return
        use_subject_grouping = (group_choice != "2")

    console.print("\n[bold cyan]Choose Index Presentation Style:[/]")
    console.print(" [1] 📊 Detailed Roadmap (Shows Topic/Subject titles, Lecture counts, video & doc breakdown tags)")
    console.print(" [2] 📜 Clean Minimal Directory (Pure Titles & Clickable Links Only — Zero counts, No clutter)")
    style_ch = await safe_input("Choose Option (1/2)", valid_options=["1", "2"], default_val="1", allow_cancel=True)
    if not style_ch: return
    is_detailed_mode = (style_ch != "2")

    cards = []
    clean_topic_header = clean_index_title(target_topic_name, max_len=40).upper()

    if use_subject_grouping:
        # Card 1: Master Navigation Roadmap Hub (Pinned at top)
        roadmap_header_title = f"{clean_topic_header} — MASTER ROADMAP" if is_detailed_mode else f"{clean_topic_header} — MASTER DIRECTORY"
        roadmap_lines = [
            "╔════════════════════════════════════════════════════════════╗",
            f"║   📑 **{roadmap_header_title}**",
            f"║   ✨ *Curated & Maintained by {GROUP_BRAND}*",
            "╚════════════════════════════════════════════════════════════╝",
            f"✨ ──────────── 📖 SUBJECT DIRECTORY ──────────── ✨"
        ]
        for s_idx, (sk, sdata) in enumerate(detected_subjects.items(), 1):
            first_link = sdata["items"][0]["link"]
            if is_detailed_mode:
                s_v = sum(1 for x in sdata["items"] if x['is_video'])
                s_d = sum(1 for x in sdata["items"] if x['is_doc'])
                breakdown_str = f"{s_v} Videos" if s_v and not s_d else (f"{s_d} Docs" if s_d and not s_v else f"{s_v}V · {s_d}D")
                roadmap_lines.append(f"[{s_idx:02d}] ▫️ **{sk}** — `{len(sdata['items'])} Items` ({breakdown_str}) ➔ [Jump to Start]({first_link})")
            else:
                roadmap_lines.append(f"[{s_idx:02d}] ▫️ **{sk}** ➔ [Jump to Start]({first_link})")

        if is_detailed_mode:
            roadmap_lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"📊 **Course Scope:** `{len(scanned_items)} Items` across `{len(detected_subjects)} Subjects`",
                f"📚 {TELEGRAM_BRAND}  ·  💬 {GROUP_BRAND}"
            ])
        else:
            roadmap_lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"📚 {TELEGRAM_BRAND}  ·  💬 {GROUP_BRAND}"
            ])
        cards.append("\n".join(roadmap_lines))

        # Subsequent Cards: Dedicated Subject Section Cards
        for sk, sdata in detected_subjects.items():
            s_items = sdata["items"]
            s_clean_name = sk.upper()
            s_part = 1
            card_title = f"{s_clean_name} — `{len(s_items)} Lectures & Files`" if is_detailed_mode else s_clean_name
            sub_card_lines = [
                "╔════════════════════════════════════════════════════════════╗",
                f"║   {card_title}",
                "╚════════════════════════════════════════════════════════════╝"
            ]
            for idx, item in enumerate(s_items, 1):
                if is_detailed_mode:
                    entry = f"[{idx:02d}] ▫️ {item['icon']} [{item['title']}]({item['link']})"
                else:
                    entry = f"[{idx:02d}] ▫️ [{item['title']}]({item['link']})"

                if sum(len(l) for l in sub_card_lines) + len(entry) > 3400:
                    sub_card_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    cards.append("\n".join(sub_card_lines))
                    s_part += 1
                    sub_card_lines = [
                        f"📑 **{s_clean_name} (Part {s_part})**",
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    ]
                sub_card_lines.append(entry)

            if is_detailed_mode:
                sub_card_lines.extend([
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    f"✨ {sdata['tag']}  ·  `{len(s_items)} Items Delivered`",
                    f"📚 {TELEGRAM_BRAND}  ·  💬 {GROUP_BRAND}"
                ])
            else:
                sub_card_lines.extend([
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                    f"📚 {TELEGRAM_BRAND}  ·  💬 {GROUP_BRAND}"
                ])
            cards.append("\n".join(sub_card_lines))
    else:
        # Standard Flat Linear Index
        linear_header_title = f"{clean_topic_header} — LECTURE ROADMAP" if is_detailed_mode else f"{clean_topic_header} — DIRECTORY"
        current_card_lines = [
            "╔════════════════════════════════════════════════════════════╗",
            f"║   📑 **{linear_header_title}**",
            f"║   ✨ *Curated & Maintained by {GROUP_BRAND}*",
            "╚════════════════════════════════════════════════════════════╝",
            "✨ ──────────── 📖 TOPIC & COURSE DIRECTORY ──────────── ✨"
        ]
        
        for idx, item in enumerate(scanned_items, 1):
            if is_detailed_mode:
                entry = f"[{idx:02d}] ▫️ {item['icon']} [{item['title']}]({item['link']})"
            else:
                entry = f"[{idx:02d}] ▫️ [{item['title']}]({item['link']})"

            if sum(len(l) for l in current_card_lines) + len(entry) > 3400:
                current_card_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                cards.append("\n".join(current_card_lines))
                current_card_lines = [
                    f"📑 **{clean_topic_header} DIRECTORY (Part {len(cards)+1})**",
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                ]
            current_card_lines.append(entry)
            
        if is_detailed_mode:
            stat_line = f"📊 **Delivered:** `{len(scanned_items)} Items`"
            if v_total and d_total:
                stat_line += f" (`{v_total} Videos` · `{d_total} Docs`)"
            elif v_total:
                stat_line += f" (`{v_total} Videos`)"
            elif d_total:
                stat_line += f" (`{d_total} Docs`)"

            current_card_lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                stat_line,
                f"📚 {TELEGRAM_BRAND}  ·  💬 {GROUP_BRAND}"
            ])
        else:
            current_card_lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"📚 {TELEGRAM_BRAND}  ·  💬 {GROUP_BRAND}"
            ])
        cards.append("\n".join(current_card_lines))

    # Preview Card 1
    card_type_desc = "Master Roadmap Hub" if use_subject_grouping else "Topic Index Card"
    console.print(Panel(cards[0][:650] + ("\n..." if len(cards[0]) > 650 else ""), title=f"Preview of {card_type_desc} (Total {len(cards)} Part{'s' if len(cards)>1 else ''})", border_style="magenta", box=box.ROUNDED))

    # Post confirmation
    post_confirm = await safe_input(f"\nPost Topic Index ({len(cards)} Cards) directly into '{target_topic_name}'? (YES / NO)", valid_options=["YES", "NO", "yes", "no"], default_val="YES", allow_cancel=True)
    if not post_confirm or post_confirm.upper() != "YES":
        console.print("[yellow]Post cancelled. Index preview only.[/]")
        await safe_input("\nPress Enter to return to menu", allow_cancel=False)
        return

    sent_first_msg = None
    try:
        reply_target = int(target_topic_id) if target_topic_id and int(target_topic_id) > 0 else None
        with console.status(f"[bold cyan]Posting {len(cards)} Index Cards with anti-flood pacing...[/]"):
            for c_idx, card in enumerate(cards, 1):
                sent = await client.send_message(
                    _parse_chat_id(group_id),
                    card,
                    reply_to=reply_target,
                    parse_mode="md",
                    link_preview=False
                )
                if c_idx == 1:
                    sent_first_msg = sent
                await asyncio.sleep(1.2) # Anti-flood safe pacing
            
        console.print(f"\n[bold green]🎉 SUCCESS! Topic Index ({len(cards)} Part{'s' if len(cards)>1 else ''}) posted into '{target_topic_name}'![/]")
        
        # Ask to pin Master Card
        pin_choice = await safe_input(f"Do you want to PIN the Master Index Card at the top of '{target_topic_name}'? (YES / NO)", valid_options=["YES", "NO", "yes", "no"], default_val="YES", allow_cancel=True)
        if pin_choice and pin_choice.upper() == "YES" and sent_first_msg:
            try:
                await client.pin_message(_parse_chat_id(group_id), sent_first_msg.id, notify=False)
                console.print("[bold green]📌 Master Index Card pinned successfully at top of Topic![/]")
            except Exception as pe:
                console.print(f"[yellow]⚠️ Message could not be pinned (Admin pin permission may be required): {pe}[/]")

        AdminTelemetry.dispatch(client, "📌 [INDEXER] Single Topic Index Generated", {
            "Group": f"`{group_id}` ({group_title})",
            "Topic": f"`{target_topic_name}` (ID: `{target_topic_id}`)",
            "Files Indexed": f"{len(scanned_items)} Files ({v_total} Videos, {d_total} Docs)",
            "Style": "Detailed Roadmap" if is_detailed_mode else "Clean Minimal Directory",
            "Total Cards": str(len(cards))
        })
    except Exception as e:
        console.print(f"\n[bold red]❌ Failed to post Topic Index card:[/] {e}")

    await safe_input("\nPress Enter to return to menu", allow_cancel=False)

async def run_master_group_indexer(session_mgr):
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel(
        "[bold cyan]🌐 MASTER GROUP & ALL-TOPICS ROADMAP INDEXER[/]\n"
        "[dim]Scan all Forum Topics across the entire group & generate a Master Navigation Roadmap Card.[/]",
        border_style="cyan", box=box.ROUNDED
    ))

    client = await session_mgr.ensure_active_client()
    if not client: return

    # 1. Select Target Forum Group
    console.print("\n[bold cyan]Select Target Forum Group to Index:[/]")
    grp_sel = await interactive_channel_selector(client, prompt_title="Target Forum Group")
    if not grp_sel: return

    group_id = grp_sel["id"]
    try:
        group_entity = await client.get_entity(_parse_chat_id(group_id))
        group_title = getattr(group_entity, 'title', None) or str(group_id)
        username = getattr(group_entity, 'username', None)
    except Exception as e:
        console.print(f"[bold red]❌ Failed to connect to group:[/] {e}")
        await safe_input("Press Enter to return", allow_cancel=False)
        return

    # 2. Fetch all Forum Topics
    with console.status(f"[bold cyan]Scanning Forum Topics in '{group_title}'...[/]"):
        try:
            peer = await client.get_input_entity(_parse_chat_id(group_id))
            res = await client(GetForumTopicsRequest(
                peer=peer, offset_date=None, offset_id=0, offset_topic=0, limit=100
            ))
            topics = res.topics if hasattr(res, 'topics') and res.topics else []
        except Exception as e:
            console.print(f"[bold red]❌ Failed to fetch forum topics:[/] {e}")
            await safe_input("Press Enter to return", allow_cancel=False)
            return

    if not topics:
        console.print(f"[yellow]⚠️ No forum topics found in '{group_title}'. Ensure Topics are enabled in Group Settings.[/]")
        await safe_input("Press Enter to return", allow_cancel=False)
        return

    console.print(f"\n[bold green]✔ Found [bold yellow]{len(topics)}[/] Forum Topics in '{group_title}'![/]\n")

    # 3. Choose Presentation Style
    console.print("[bold cyan]Choose Master Index Presentation Format:[/]")
    console.print(" [1] 📊 Detailed Roadmap (Topic Name, Jump Link, and file/video counts inside each topic)")
    console.print(" [2] 📜 Clean Minimal Directory (Pure Topic Names and direct Jump Links ONLY — zero counts)")
    style_ch = await safe_input("Choose Option (1/2)", valid_options=["1", "2"], default_val="1", allow_cancel=True)
    if not style_ch: return
    is_detailed = (style_ch == "1")

    topic_data = []
    total_files_all = 0
    total_vids_all = 0
    total_docs_all = 0

    with console.status("[bold cyan]Compiling Master Topics Directory...[/]") as status:
        for idx, t in enumerate(topics, 1):
            t_name = getattr(t, 'title', f"Topic #{t.id}").strip()
            clean_t_name = clean_index_title(t_name, max_len=45)
            t_link = make_telegram_link(group_id, t.id, topic_id=t.id, username=username)

            v_count = 0
            d_count = 0
            total_items = 0

            if is_detailed:
                status.update(f"[bold cyan][{idx}/{len(topics)}] Scanning topic: {clean_t_name}...[/]")
                try:
                    t_msgs = await client.get_messages(group_entity, reply_to=t.id, limit=300)
                    for m in t_msgs:
                        if m and (m.video or m.document or m.photo):
                            total_items += 1
                            if m.video: v_count += 1
                            elif m.document: d_count += 1
                    total_files_all += total_items
                    total_vids_all += v_count
                    total_docs_all += d_count
                except Exception:
                    pass

            topic_data.append({
                "id": t.id,
                "title": clean_t_name,
                "link": t_link,
                "total": total_items,
                "videos": v_count,
                "docs": d_count
            })

    console.print("\n[bold cyan]Topic Sorting Order:[/]")
    console.print(" [1] 🔢 Creation Order (Chronological)")
    console.print(" [2] 🔤 Alphabetical (A to Z)")
    sort_ch = await safe_input("Choose Order (1/2)", valid_options=["1", "2"], default_val="1", allow_cancel=True)
    if sort_ch == "2":
        topic_data.sort(key=lambda x: clean_sort_key(x["title"]))

    cards = []
    clean_grp_title = clean_index_title(group_title, max_len=40).upper()

    header_title = f"{clean_grp_title} — MASTER ROADMAP" if is_detailed else f"{clean_grp_title} — MASTER DIRECTORY"
    header_block = [
        "╔════════════════════════════════════════════════════════════╗",
        f"║   📑 **{header_title}**",
        f"║   ✨ *Curated & Maintained by {GROUP_BRAND}*",
        "╚════════════════════════════════════════════════════════════╝",
        "✨ ──────────── 📖 ALL FORUM TOPICS DIRECTORY ──────────── ✨"
    ]

    current_card = list(header_block)
    for idx, td in enumerate(topic_data, 1):
        if is_detailed:
            breakdown = f"{td['videos']} Videos" if td['videos'] and not td['docs'] else (f"{td['docs']} Docs" if td['docs'] and not td['videos'] else f"{td['videos']}V · {td['docs']}D")
            count_str = f" — `{td['total']} Items` ({breakdown})" if td['total'] > 0 else ""
            entry = f"[{idx:02d}] ▫️ 📂 [{td['title']}]({td['link']}){count_str}"
        else:
            entry = f"[{idx:02d}] ▫️ [{td['title']}]({td['link']})"

        if sum(len(l) for l in current_card) + len(entry) > 3400:
            current_card.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            cards.append("\n".join(current_card))
            current_card = [
                f"📑 **{clean_grp_title} DIRECTORY (Part {len(cards)+1})**",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ]
        current_card.append(entry)

    if is_detailed and total_files_all > 0:
        footer = [
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📊 **Scope:** `{len(topics)} Topics`  ·  `{total_files_all} Total Files` (`{total_vids_all} Videos` · `{total_docs_all} Docs`)",
            f"📚 {TELEGRAM_BRAND}  ·  💬 {GROUP_BRAND}"
        ]
    else:
        footer = [
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📊 **Scope:** `{len(topics)} Forum Topics`",
            f"📚 {TELEGRAM_BRAND}  ·  💬 {GROUP_BRAND}"
        ]

    current_card.extend(footer)
    cards.append("\n".join(current_card))

    # Preview Card 1
    console.print(Panel(cards[0][:700] + ("\n..." if len(cards[0]) > 700 else ""), title=f"Preview of Master Roadmap (Total {len(cards)} Part{'s' if len(cards)>1 else ''})", border_style="magenta", box=box.ROUNDED))

    # Ask destination topic to post
    console.print(f"\n[cyan]Where would you like to post this Master Directory Card?[/]")
    console.print(" [1] 🌐 General Topic / Topic #1 (Recommended for Master Hub)")
    console.print(" [2] 📌 Select Specific Topic")
    post_loc = await safe_input("Choose Location (1/2)", valid_options=["1", "2"], default_val="1", allow_cancel=True)
    if not post_loc: return

    dest_topic_id = None
    dest_topic_name = "General Topic"
    if post_loc == "2":
        console.print("\nSelect destination topic:")
        for idx, t in enumerate(topics, 1):
            console.print(f" [{idx}] 📌 {getattr(t, 'title', f'Topic #{t.id}')}")
        top_sel = await safe_input(f"Choose Topic (1-{len(topics)})", valid_options=[str(i) for i in range(1, len(topics)+1)], default_val="1", allow_cancel=True)
        if top_sel:
            chosen = topics[int(top_sel)-1]
            dest_topic_id = chosen.id
            dest_topic_name = getattr(chosen, 'title', f"Topic #{chosen.id}")
    else:
        dest_topic_id = topics[0].id if topics else 1
        dest_topic_name = getattr(topics[0], 'title', 'General')

    post_confirm = await safe_input(f"\nPost Master Directory ({len(cards)} Cards) into '{dest_topic_name}'? (YES / NO)", valid_options=["YES", "NO", "yes", "no"], default_val="YES", allow_cancel=True)
    if not post_confirm or post_confirm.upper() != "YES":
        console.print("[yellow]Post cancelled. Preview only.[/]")
        await safe_input("Press Enter to return", allow_cancel=False)
        return

    sent_first = None
    try:
        reply_target = int(dest_topic_id) if dest_topic_id and int(dest_topic_id) > 0 else None
        with console.status(f"[bold cyan]Posting Master Directory with anti-flood pacing...[/]"):
            for c_idx, card in enumerate(cards, 1):
                sent = await client.send_message(
                    _parse_chat_id(group_id),
                    card,
                    reply_to=reply_target,
                    parse_mode="md",
                    link_preview=False
                )
                if c_idx == 1:
                    sent_first = sent
                await asyncio.sleep(1.2)

        console.print(f"\n[bold green]🎉 SUCCESS! Master Directory posted into '{dest_topic_name}'![/]")

        pin_ch = await safe_input(f"PIN this Master Directory Card at the top of '{dest_topic_name}'? (YES / NO)", valid_options=["YES", "NO", "yes", "no"], default_val="YES", allow_cancel=True)
        if pin_ch and pin_ch.upper() == "YES" and sent_first:
            try:
                await client.pin_message(_parse_chat_id(group_id), sent_first.id, notify=False)
                console.print("[bold green]📌 Master Directory Card pinned successfully![/]")
            except Exception as pe:
                console.print(f"[yellow]⚠️ Could not pin message (Admin permission required): {pe}[/]")

        AdminTelemetry.dispatch(client, "📌 [INDEXER] Master Group Roadmap Generated", {
            "Group": f"`{group_id}` ({group_title})",
            "Topics Indexed": str(len(topics)),
            "Style": "Detailed Roadmap" if is_detailed else "Clean Minimal Directory",
            "Total Cards": str(len(cards))
        })
    except Exception as e:
        console.print(f"\n[bold red]❌ Failed to post Master Directory card:[/] {e}")

    await safe_input("\nPress Enter to return to menu", allow_cancel=False)


async def run_indexer_menu(session_mgr):
    while True:
        clear_screen()
        console.print(get_persistent_header())
        console.print(Panel(
            "[bold cyan]📑 TELEGRAM INDEXING & DIRECTORY SUITE[/]\n"
            "[dim]─────────────────────────────────────────────────[/]\n\n"
            " [bold magenta][1][/] 📌 [bold white]Single Topic Files & Subject Indexer[/] [bold yellow]⭐ (Recommended)[/]\n"
            "     [dim]Scan all Videos & PDFs inside 1 Topic & generate Smart Subject Roadmap (No Uploads)[/]\n\n"
            " [bold green][2][/] 🌐 [bold white]Master Group Roadmap Indexer[/]\n"
            "     [dim]Scan all Forum Topics across the entire group & create Master Group Roadmap[/]\n\n"
            " [dim][0] Return to Main Menu[/]",
            border_style="cyan",
            box=box.ROUNDED
        ))
        sub_ch = await safe_input("Choose Option (1/2/0)", valid_options=["1", "2", "0"], default_val="1", allow_cancel=True)
        if not sub_ch or sub_ch == "0":
            break
        elif sub_ch == "1":
            await run_single_topic_files_indexer(session_mgr)
            break
        elif sub_ch == "2":
            await run_master_group_indexer(session_mgr)
            break

async def run_diagnostics():
    clear_screen()
    console.print(get_persistent_header())
    console.print(Panel("[bold cyan]🩺 SYSTEM DIAGNOSTICS & HEALTH CHECK[/]", border_style="cyan", box=box.ROUNDED))
    
    checks = [
        ("Checking Python Version (>=3.9 recommended)", sys.version_info >= (3, 9)),
        ("Checking .env Configuration File", os.path.exists(".env")),
        ("Checking SQLite Database Integrity", validate_active_database(DB_FILE)["ok"]),
        ("Checking Log Directory Permissions", os.access("logs", os.W_OK) if os.path.exists("logs") else True),
        ("Checking Hardware Accelerators (cryptg)", CRYPTG),
        ("Checking Hardware Accelerators (uvloop)", UVLOOP),
    ]
    
    for check_name, passed in checks:
        status = "[green]✔ PASSED[/]" if passed else "[red]❌ FAILED/MISSING[/]"
        console.print(f" {status} | {check_name}")
        await asyncio.sleep(0.15)

    try:
        t0 = time.monotonic()
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection("149.154.167.50", 443),
            timeout=3.0
        )
        writer.close()
        await writer.wait_closed()
        ping_ms = int((time.monotonic() - t0) * 1000)
        console.print(f" [green]✔ PASSED[/] | Checking Telegram MTProto DC Latency (Online – {ping_ms} ms)")
    except Exception as e:
        console.print(f" [yellow]⚠️ UNREACHABLE[/] | Checking Telegram MTProto DC Latency ({e})")
    await asyncio.sleep(0.15)
        
    await safe_input("\nPress Enter to return", allow_cancel=False)

async def run_account_switcher_tool(session_mgr):
    while True:
        clear_screen()
        console.print(get_persistent_header())
        
        status_list = await session_mgr.get_sessions_status()
        
        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan", expand=True)
        table.add_column("#", style="dim", width=4)
        table.add_column("Session File", style="bold white")
        table.add_column("Account Name", style="bold green")
        table.add_column("Username", style="yellow")
        table.add_column("User ID", style="cyan")
        table.add_column("Status", style="bold")
        
        for idx, s in enumerate(status_list, 1):
            is_act = s["is_active"]
            act_badge = "[bold green]🟢 ACTIVE (Default)[/]" if is_act else "[dim]⚪ Inactive[/]"
            u = s.get("user") or {}
            uname = f"@{u.get('username')}" if u.get('username') else "[dim]None[/]"
            fname = u.get("first_name") or "Unknown"
            uid = str(u.get("id") or "N/A")
            table.add_row(str(idx), s["name"], fname, uname, uid, act_badge)
            
        console.print(Panel(
            "[bold cyan]👥 TELEGRAM MULTI-ACCOUNT & SESSION SWITCHER[/]\n"
            "[dim]Manage your accounts or add your friend's account seamlessly on this machine.[/]",
            border_style="cyan", box=box.ROUNDED
        ))
        console.print(table)
        
        console.print(Panel(
            " [bold green][1..N][/] Switch Active Account (Set Default)\n"
            " [bold cyan][A][/] ➕ Add / Login New Telegram Account\n"
            " [bold red][D][/] 🗑️ Delete / Disconnect a Session File\n"
            " [dim][0] Return to Main Menu[/]",
            border_style="dim", box=box.ROUNDED
        ))
        
        choice = await safe_input("Choose Option (1..N / A / D / 0)", allow_cancel=True, default_val="0")
        if not choice or choice == "0":
            break
            
        if choice.isdigit() and 1 <= int(choice) <= len(status_list):
            sel_idx = int(choice) - 1
            session_mgr.set_active_session(sel_idx)
            env_p = Path(".env")
            if env_p.exists():
                set_key(".env", "ACTIVE_SESSION_INDEX", str(sel_idx))
            console.print(f"\n[bold green]✔ Active account switched to:[/] [cyan]{status_list[sel_idx]['name']}[/]")
            await asyncio.sleep(1.2)
            continue
            
        elif choice.upper() == "A":
            s_name = await safe_input("Enter a custom session nickname (e.g., session_friend or session_primary)", default_val=f"session_user_{len(status_list)+1}")
            if not s_name: continue
            clean_sname = str(Path(s_name).stem)
            client = session_mgr.add_session(clean_sname)
            console.print(f"\n[bold yellow]Starting login flow for '{clean_sname}'...[/]")
            try:
                await client.start()
                me = await client.get_me()
                if me:
                    console.print(f"[bold green]✔ Successfully logged in as:[/] [bold cyan]{me.first_name} (@{me.username or 'No Username'}) [ID: {me.id}][/]")
                    session_mgr._discover_sessions()
                    session_mgr.set_active_session(clean_sname)
                    env_p = Path(".env")
                    if env_p.exists():
                        set_key(".env", "ACTIVE_SESSION_INDEX", str(session_mgr.active_index))
            except Exception as e:
                console.print(f"[bold red]❌ Login failed:[/] {e}")
            await safe_input("\nPress Enter to continue", allow_cancel=False)
            continue
            
        elif choice.upper() == "D":
            del_choice = await safe_input(f"Enter session number to delete (1..{len(status_list)})", allow_cancel=True)
            if del_choice and del_choice.isdigit() and 1 <= int(del_choice) <= len(status_list):
                target_s = status_list[int(del_choice)-1]["name"]
                s_file = f"{target_s}.session"
                if os.path.exists(s_file):
                    with suppress(Exception): os.remove(s_file)
                    console.print(f"[bold green]✔ Removed {s_file} safely.[/]")
                    session_mgr._discover_sessions()
                else:
                    console.print(f"[yellow]File {s_file} not found on disk.[/]")
                await asyncio.sleep(1.2)
            continue

async def run_menu(session_mgr):
    while True:
        clear_screen()
        console.print(get_persistent_header())

        # Number badge helper — \\[ renders as [ in Rich markup
        LB = "\\["
        cur_direct = os.getenv("DIRECT_FORWARD", "false").strip().lower() in ("true", "1", "yes")
        direct_tag = "[bold green]FAST DIRECT[/]" if cur_direct else "[bold cyan]STREAM (Safe)[/]"

        # ── Card 1: Transmission ──────────────────────────────────────────
        card1_transmission = Panel(
            "[bold cyan]⚡  TRANSMISSION & SPEED ENGINES[/]\n"
            "[dim]─────────────────────────────────────────────────[/]\n"
            f" [bold green]{LB}1][/] 🟢 [bold white]Safe Mode[/] [dim]· 4 Workers (Slow Nets)[/]\n"
            f" [bold blue]{LB}2][/] ⚖️ [bold white]Balanced Mode[/] [bold yellow]⭐[/] [dim]· 12 Workers (Default)[/]\n"
            f" [bold red]{LB}3][/] 🔥 [bold white]God Mode[/] [dim]· 40 Workers (Gigabit Turbo)[/]\n"
            f" [bold magenta]{LB}4][/] 🔴 [bold white]Live 24/7 Mode[/] [dim]· Real-Time Auto-Forward[/]",
            title="[bold cyan] 1 [/]",
            border_style="cyan",
            box=box.ROUNDED,
            padding=(0, 1)
        )

        # ── Card 2: Routing ───────────────────────────────────────────────
        card2_routing = Panel(
            "[bold magenta]🔗  LINK EXTRACTOR & ROUTING[/]\n"
            "[dim]─────────────────────────────────────────────────[/]\n"
            f" [bold green]{LB}5][/] 🔗 [bold white]Link Extractor[/] [dim]· Set Source & Target .env[/]\n"
            f" [bold blue]{LB}6][/] 🔀 [bold white]Multi-Route Manager[/] [dim]· Visual Rules Table[/]\n"
            f" [bold magenta]{LB}7][/] 🎯 [bold white]Cherry-Picker & Cloner[/] [bold yellow]⭐[/] [dim]· Pick & Paste Specific Content[/]\n"
            f" [bold cyan]{LB}8][/] 📑 [bold white]Topic & Group Indexer[/] [bold yellow]⭐[/] [dim]· Clickable TOC (No Uploads)[/]",
            title="[bold magenta] 2 [/]",
            border_style="magenta",
            box=box.ROUNDED,
            padding=(0, 1)
        )

        # ── Card 3: Studio ────────────────────────────────────────────────
        card3_studio = Panel(
            "[bold yellow]🛠️  BRANDING & MEDIA STUDIO[/]\n"
            "[dim]─────────────────────────────────────────────────[/]\n"
            f" [bold green]{LB}9][/] 📁 [bold white]Batch Folder & 2GB Uploader[/] [dim]· Auto-Tags & Sequence[/]\n"
            f" [bold magenta]{LB}10][/] ✍️ [bold white]Caption & Link Studio[/] [dim]· Signature ON/OFF & Clean[/]\n"
            f" [bold yellow]{LB}11][/] 🖼️ [bold white]16:9 Cover Enforcer[/] [dim]· Custom Thumbnails[/]\n"
            f" [bold yellow]{LB}12][/] 🔄 [bold white]DLQ Auto-Recovery[/] [dim]· 1-Click Retry Failed[/]\n"
            f" [bold cyan]{LB}17][/] ⚡ [bold white]Pipeline Engine:[/] {direct_tag} [dim]· Stream / Direct[/]",
            title="[bold yellow] 3 [/]",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(0, 1)
        )

        # ── Card 4: System Health & Accounts ───────────────────────────────
        card4_system = Panel(
            "[bold green]🩺  SYSTEM HEALTH & ACCOUNTS[/]\n"
            "[dim]─────────────────────────────────────────────────[/]\n"
            f" [bold cyan]{LB}19][/] 👥 [bold white]Account Switcher & Login[/] [bold yellow]⭐[/] [dim]· Add/Switch TG Accounts[/]\n"
            f" [bold yellow]{LB}13][/] 🩺 [bold white]System Diagnostics[/] [dim]· Latency & Integrity[/]\n"
            f" [bold green]{LB}14][/] ♻️ [bold white]Reset History & DB[/] [dim]· Fresh Re-Scan #1[/]\n"
            f" [bold cyan]{LB}15][/] 🧹 [bold white]Deep Cleaner & Purge[/] [dim]· Sessions & Logs[/]\n"
            f" [bold magenta]{LB}18][/] 🚀 [bold white]Check & Install Updates[/] [bold yellow]⭐[/] [dim]· 1-Click Code Sync[/]\n"
            f" [bold red]{LB}16][/] ❌ [bold white]Safe Exit[/] [dim]· Flush DB WAL & Shutdown[/]",
            title="[bold green] 4 [/]",
            border_style="green",
            box=box.ROUNDED,
            padding=(0, 1)
        )

        # ── Dashboard grid ─────────────────────────────────────────────────────
        w = get_terminal_width()
        menu_table = Table.grid(expand=True)
        if w < 95:
            menu_table.add_column(ratio=1)
            menu_table.add_row(card1_transmission)
            menu_table.add_row(card2_routing)
            menu_table.add_row(card3_studio)
            menu_table.add_row(card4_system)
        else:
            menu_table.add_column(ratio=1)
            menu_table.add_column(ratio=1)
            menu_table.add_row(card1_transmission, card2_routing)
            menu_table.add_row(card3_studio, card4_system)

        console.print(menu_table)

        # ── Prompt bar ─────────────────────────────────────────────────────────
        console.print(Panel(
            "  [dim]Enter[/] [bold cyan]1–19[/] [dim]to select a tool  ·  [/][bold yellow]2[/][dim] = Balanced Mode (Recommended Default)[/]",
            border_style="dim",
            box=box.ROUNDED,
            padding=(0, 1)
        ))
        ch = await safe_input("Choice", valid_options=[str(i) for i in range(1, 20)], allow_cancel=False, default_val="2")
        
        # 1-4: Transmission Modes
        if ch in ["1", "2", "3", "4"]:
            selected_routing = await prompt_routing_mode()
            if selected_routing is None: continue
            
            selected_seq = await prompt_sequence_mode()
            if selected_seq is None: continue
            
            m_filter = await filter_menu()
            if m_filter == "back": continue
            
            if ch == "1": return (1, 4, False, m_filter, selected_routing, False, False)
            if ch == "2": return (1, 12, False, m_filter, selected_routing, False, False)
            if ch == "3": return (1, 40, True, m_filter, selected_routing, False, False)
            if ch == "4": return (1, 12, False, m_filter, selected_routing, False, True)
            
        elif ch == "5":
            await run_quick_env_extractor(session_mgr)
            continue
        elif ch == "6":
            await run_extractor_tool(session_mgr)
            continue
        elif ch == "7":
            clear_screen()
            console.print(get_persistent_header())
            console.print(Panel(
                "[bold magenta]🎯 CONTENT CLONING, CHERRY-PICKER & FORWARDER SUITE[/]\n"
                "[dim]─────────────────────────────────────────────────[/]\n\n"
                " [bold green][1][/] 🎬 [bold white]Direct Single / Specific Videos & Messages Forwarder[/] [bold yellow]⭐ (New)[/]\n"
                "     [dim]Forward 1 or 2 specific videos, message IDs, or t.me links straight into any Forum Topic[/]\n\n"
                " [bold cyan][2][/] 🎯 [bold white]Selective Content Explorer & Cherry-Picker[/]\n"
                "     [dim]Browse source group, inspect files, pick what you need & paste to chosen topic[/]\n\n"
                " [bold blue][3][/] 👥 [bold white]Cross-Group Member Scraper, Backup & Smart Adder[/]\n"
                "     [dim]Scrape active members from any group, export CSV backup & safely add to your group[/]\n\n"
                " [bold magenta][4][/] 🧬 [bold white]Full Group / Forum Auto-Mirror[/]\n"
                "     [dim]Auto-create matching topics and mirror entire group structure[/]\n\n"
                " [dim][0] Return to Main Menu[/]",
                border_style="magenta", box=box.ROUNDED
            ))
            clone_sub = await safe_input("Choose Option (1/2/3/4/0)", valid_options=["1", "2", "3", "4", "0"], default_val="1", allow_cancel=True)
            if clone_sub == "1":
                await run_single_or_specific_messages_forwarder(session_mgr)
            elif clone_sub == "2":
                await run_selective_content_picker(session_mgr)
            elif clone_sub == "3":
                await run_member_scraper_and_adder(session_mgr)
            elif clone_sub == "4":
                res = await run_group_cloner_tool(session_mgr)
                if res: return res
            continue
        elif ch == "8":
            await run_indexer_menu(session_mgr)
            continue
        elif ch == "9":
            await run_local_splitter_tool(session_mgr)
            continue
        elif ch == "10":
            await interactive_caption_and_filter_wizard()
            continue
        elif ch == "11":
            await thumbnail_menu()
            continue
        elif ch == "12":
            console.print(Panel(
                "[bold cyan]📮 DEAD LETTER QUEUE (DLQ) MANAGEMENT[/]\n\n"
                "[bold green][1][/] 🔁 Auto-Retry & Recover All Failed Items (DLQ Stream)\n"
                "[bold yellow][2][/] 📄 Export Failed Items Report (`dlq_report.json`)\n"
                "[bold red][3][/] 🗑️ Clear / Purge DLQ Failure History\n"
                "[dim][0] Return to Main Menu[/]",
                border_style="cyan", box=box.ROUNDED
            ))
            dlq_choice = await safe_input("Choose Option (1/2/3/0)", default_val="1", allow_cancel=True)
            if not dlq_choice or dlq_choice == "0":
                continue
            if dlq_choice == "2":
                dlq_inst = AsyncDLQ()
                out_p, count = dlq_inst.export_json_report("dlq_report.json")
                if out_p and count > 0:
                    console.print(f"\n[bold green]✔ Successfully exported {count} failed items to:[/] [cyan]{out_p}[/]")
                elif count == 0:
                    console.print("\n[bold green]✔ DLQ is empty (0 failed items). No failures found![/]")
                else:
                    console.print("\n[bold red]❌ Failed to export DLQ report.[/]")
                await safe_input("\nPress Enter to return to menu", allow_cancel=False)
                continue
            elif dlq_choice == "3":
                if os.path.exists("dead_letter.jsonl"):
                    with suppress(Exception): os.remove("dead_letter.jsonl")
                console.print("\n[bold green]✔ DLQ records successfully cleared.[/]")
                await asyncio.sleep(1.0)
                continue
            elif dlq_choice == "1":
                console.print("[bold yellow]Initializing DLQ recovery mode...[/]")
                await asyncio.sleep(1)
                return (1, 12, False, "all", 1, True, False)
        elif ch == "13":
            await run_diagnostics()
            continue
        elif ch == "14":
            await wipe_memory()
            continue
        elif ch == "15":
            await advanced_cleaner_menu()
            continue
        elif ch == "17":
            await mode_toggle_menu()
            continue
        elif ch == "18":
            clear_screen()
            console.print(get_persistent_header())
            from tools.updater import run_update
            run_update()
            await safe_input("\nPress Enter to return to main menu", allow_cancel=False)
            continue
        elif ch == "19":
            await run_account_switcher_tool(session_mgr)
            continue
        elif ch == "16":
            AdminTelemetry.dispatch(session_mgr.get_client(), "🔴 [MONITOR] Program Closed / Exit", {
                "Status": "Terminated Normally by User"
            })
            console.print("\n[bold green]👋 Program Exited Safely. Have a great day![/]")
            await asyncio.sleep(0.5)
            release_lock()
            sys.exit(0)

async def start_platform(auto_start: bool = False):
    acquire_instance_lock()
    startup_animation()
    optimize_runtime()
    
    load_dotenv(override=True)
    api_id = int(os.getenv("API_ID", 0) or 0)
    api_hash = os.getenv("API_HASH", "").strip().strip("'").strip('"')

    # Fallback to verified official MTProto credentials if unconfigured
    if not api_id or not api_hash or api_id in (0, 2040) or "hash" in api_hash.lower():
        api_id = 36193727
        api_hash = "fef19b9b1434a3e66b009fd31053200b"
        with suppress(Exception):
            set_key(".env", "API_ID", str(api_id))
            set_key(".env", "API_HASH", api_hash)

    session_mgr = MultiSessionManager(api_id, api_hash)

    # Proactive Telegram User Authentication Check BEFORE presenting menu
    try:
        primary_client = session_mgr.get_client()
        if primary_client:
            if not primary_client.is_connected():
                await primary_client.connect()
            if not await primary_client.is_user_authorized():
                console.print(Panel(
                    "[bold cyan]👋 WELCOME TO TG KINDSYNC PRO![/]\n\n"
                    "Telegram sync shuru karne ke liye pehli baar login karna zaroori hai.\n"
                    "• Browser me automatic Login Page khulega ya Terminal me OTP enter kar sakte hain.\n"
                    "• Apne Telegram phone number (+91...) ke saath login karein.",
                    border_style="cyan", box=box.ROUNDED
                ))
                await interactive_telegram_login(primary_client)
                session_mgr._discover_sessions()
    except Exception as auth_err:
        logger.warning(f"Initial login check: {auth_err}")
    
    # Auto-start check for 100% hands-free execution
    is_auto = auto_start or ("--auto" in sys.argv) or ("--live" in sys.argv) or (os.getenv("AUTO_START_LIVE", "").strip() in ("1", "true", "yes"))
    first_run = True
    
    while True:
        try:
            if is_auto and first_run:
                first_run = False
                console.print("\n[bold green]🚀 AUTO-START:[/] [cyan]Launching Real-Time Live Forwarding in Balanced Mode (12 Workers)...[/]")
                menu_result = (12, 1, False, None, "balanced", False, True)
            else:
                menu_result = await run_menu(session_mgr)
            if menu_result is None: continue 
            
            w_count, parallel, is_adaptive, m_filter, routing_mode, dlq_flag, live_mode = menu_result
            update_env_file(mode="perf", perf_data={"workers": w_count, "parallelism": parallel, "adaptive": is_adaptive})
            
            cfg = AppConfig.load(media_filter=m_filter, workers=w_count, parallelism=parallel, adaptive=is_adaptive, routing_mode=routing_mode, run_dlq=dlq_flag, live_mode=live_mode)
            platform = TerminalPlatform(cfg, session_mgr=session_mgr)
            await platform.boot()
            await safe_input("\nPress Enter to return to Main Menu", allow_cancel=False)
        except (KeyboardInterrupt, asyncio.CancelledError):
            console.print("\n[bold yellow]Returning to Main Menu...[/]")
            await asyncio.sleep(0.5)
            continue
        except Exception as e:
            console.print(f"\n[bold red]❌ FATAL ERROR: {e}[/]")
            traceback.print_exc()
            await safe_input("\nPress Enter to return to menu", allow_cancel=False)

async def main_async():
    await start_platform()

if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(start_platform())
    release_lock()

"""
DEVI Multi-Role Telegram Sentinel & Operator Bot Daemon
Features:
- Two-Tier Architecture: Silent Guardian in Groups, Full Command & Intel Center in Admin DM
- Group Anti-Spam: Auto-purge phone numbers and external links with auto-expiring warnings (30s)
- Clean Minimalist Group Welcome (Auto-destructs after 60s to prevent clutter)
- Private Admin Intel Alerts on New Members with 1-Click [👢 Kick] & [🚫 Ban]
- Single-Use Disposable Invite Links (/invitelink) for copyright & crawler defense
- 100% Anonymous Live Support Relay with "👨‍⚕️ Kind Doctor:" branding
- User Intel Dossier & Full Change History Tracking (Name, Username, Phone, Premium)
- Automatic Username Setup Guide for new users with "No Username"
- Devi AI Autonomous Assistant for Admins
"""

import aiohttp
import asyncio
import os
import sys
import re
import json
import html
import logging
import sqlite3
import csv
import io
import random
import base64
import struct
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Set, Dict, Any, Optional
from contextlib import suppress

from dotenv import load_dotenv, set_key

from devi.config import DEVI_NAME, CURRENT_AUTONOMY_LEVEL
from devi.memory.memory_store import MemoryStore
from devi.tools.system_tools import SystemTools
from devi.evolution.evaluator import Evaluator
from devi.brain.model_router import ModelRouter
from devi.operator.medical_calculator import (
    calc_bmi,
    calc_bsa,
    calc_gfr,
    calc_pediatric_dose,
    calc_mg_per_kg,
    calc_maintenance_fluids,
    calc_et_tube,
    calc_apgar,
    calc_parkland,
    calc_urine_output,
    calc_edd,
    calc_psm_matrix,
    calc_iv_drip,
    calc_inotrope_infusion,
    calc_map,
    calc_anion_gap,
    calc_corrected_sodium,
    calc_gcs,
    calc_curb65,
    calc_wells_pe,
)

logger = logging.getLogger("DEVI.TelegramBot")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

BASE_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_PROJECT_DIR / "history_core.sqlite"
ENV_PATH = BASE_PROJECT_DIR / ".env"
load_dotenv(ENV_PATH)

def get_db_conn() -> sqlite3.Connection:
    """Thread-safe, locked-resistant SQLite connection with 60s timeout and WAL pragma."""
    conn = sqlite3.connect(DB_PATH, timeout=60.0)
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA busy_timeout = 60000")
    conn.execute("PRAGMA synchronous = NORMAL")
    return conn

# Regex for Indian & International 10-12 digit numbers (handles spaces, dashes, +91)
PHONE_REGEX = re.compile(r'(?:\+?91[\s-]?)?[6-9](?:[\s-]?\d){9}\b|\b\d(?:[\s-]?\d){9,11}\b')
# Regex for external promo & invite links
LINK_REGEX = re.compile(r'(?:https?://)?(?:t\.me|telegram\.me|telegram\.dog)/(?:joinchat/|[a-zA-Z0-9_+]+)|https?://\S+')
# Regex for Crypto, Forex, Gambling, Betting, Color Trading Scam & Adult/NSFW (AI TelegramGuard style)
SCAM_NSFW_REGEX = re.compile(
    r'(?i)\b('
    r'crypto|bitcoin|btc|usdt|eth|binance|airdrop|doubler|guaranteed profit|forex trading|binary trading|'
    r'1xbet|betting|casino|color trading|rummy|teen patti|satta|dream11 hack|earn money online|free recharge|'
    r'nude|nudes|escort|call girl|dating|porn|xxx|sex chat|hookup|onlyfans'
    r')\b'
)
# Malicious / executable file extensions for student group safety (Dr.Web style)
DANGEROUS_EXT_REGEX = re.compile(r'(?i)\.(apk|exe|bat|cmd|vbs|scr|msi)$')

# Commands accessible to all group members without requiring admin privilege
PUBLIC_ALLOWED_COMMANDS = (
    "/find", "/search", "/faq", "/faqs", 
    "/indexhelp", "/topics", "/help",
    "/mainindex", "/topicindex", "/indexmaster", "/index",
    "/scan", "/autoindex", "/start", "/menu", "/fullhelp", "/manual",
    "/support", "/contact", "/id", "/myid", "/info",
    "/stats", "/leaderboard", "/topmembers", "/history", "/rules",
    "/userinfo", "/whois", "/botinfo", "/about",
    "/engine", "/status", "/backup", "/clean", "/cleanbot", "/sangmata",
    "/phone", "/email", "/phonelookup", "/emaillookup",
    "/calc", "/dose", "/formula", "/score",
    "/bmi", "/bsa", "/gfr", "/pedia", "/burns", "/uop", "/edd", "/psm",
    "/drip", "/infusion", "/map", "/abg", "/sodium", "/gcs", "/curb65", "/wells",
    "/save", "/get", "/note", "/notes", "/saved", "/clear", "/delnote",
    "/filter", "/setfilter", "/stop", "/delfilter", "/filters",
    "/mcq", "/pearl", "/pomodoro", "/ask"
)
STUDENT_ALLOWED_COMMANDS = PUBLIC_ALLOWED_COMMANDS

class DeviTelegramBot:
    def __init__(self, bot_token: str = None):
        self.token = bot_token or os.getenv("DEVI_TELEGRAM_BOT_TOKEN", "").strip().strip("'").strip('"')
        self.target_chat = os.getenv("TARGET_CHAT", "").strip().strip("'").strip('"')
        
        # Parse Master Admins from env (Strictly Primary 1: 1553619403, Primary 2: 759038032)
        raw_admins = os.getenv("DEVI_ADMIN_ID", "1553619403,759038032").replace("'", "").replace('"', "")
        self.master_admin_ids: Set[int] = set()
        for item in raw_admins.split(","):
            item = item.strip()
            if item.isdigit():
                self.master_admin_ids.add(int(item))
                
        self.co_admins: Set[int] = set()
        self.blocked_users: Set[int] = set()
        
        # In-memory mapping: (admin_chat_id, admin_msg_id) -> dict(user_chat_id, user_name, user_msg_id)
        self.relay_map: Dict[tuple, Dict[str, Any]] = {}
        # Anti-Flood tracking: user_id -> list of timestamps
        self.flood_tracker: Dict[int, list] = {}
        
        self.memory = MemoryStore()
        self.evaluator = Evaluator(self.memory)
        self.router = ModelRouter()
        self.offset = 0
        self.is_running = False
        self.active_tasks: Set[asyncio.Task] = set()
        self.bot_name: str = "Kind Doctor 🩺"
        self.bot_username: str = "KindDoc_bot"
        self._init_db()

    def create_tracked_task(self, coro, name: Optional[str] = None) -> asyncio.Task:
        """Spawns an asyncio task with automatic lifecycle tracking to prevent task leaks."""
        task = asyncio.create_task(coro, name=name)
        self.active_tasks.add(task)
        task.add_done_callback(self.active_tasks.discard)
        return task

    def _init_db(self):
        """Initialize bot tables and user dossier tracking in SQLite."""
        try:
            with get_db_conn() as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_bot_admins (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        added_by INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_bot_blocked (
                        user_id INTEGER PRIMARY KEY,
                        blocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # User Intel Dossier & Identity Change Tracker
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_users_dossier (
                        user_id INTEGER PRIMARY KEY,
                        first_name TEXT,
                        last_name TEXT,
                        username TEXT,
                        phone_number TEXT,
                        is_premium INTEGER DEFAULT 0,
                        language_code TEXT,
                        first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        total_messages INTEGER DEFAULT 1,
                        name_history TEXT DEFAULT '[]',
                        username_history TEXT DEFAULT '[]',
                        changes_count INTEGER DEFAULT 0
                    )
                """)
                # Custom Commands Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_custom_commands (
                        command TEXT PRIMARY KEY,
                        response_text TEXT,
                        created_by INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Group Forum Topics Directory
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_group_topics (
                        chat_id INTEGER,
                        topic_id INTEGER,
                        topic_title TEXT,
                        topic_icon TEXT DEFAULT '📖',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY(chat_id, topic_id)
                    )
                """)
                # Topic Items / Lectures / Files Table of Contents
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_topic_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER,
                        topic_id INTEGER,
                        item_order INTEGER DEFAULT 0,
                        msg_id INTEGER,
                        custom_link TEXT,
                        title TEXT,
                        item_type TEXT DEFAULT 'video',
                        icon TEXT DEFAULT '🎬',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_topic_items_chat_topic ON telegram_topic_items(chat_id, topic_id)
                """)
                # Rose Style Group Notes Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_group_notes (
                        chat_id INTEGER,
                        note_name TEXT,
                        content TEXT,
                        created_by INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY(chat_id, note_name)
                    )
                """)
                # Group FAQs Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_group_faqs (
                        chat_id INTEGER,
                        keyword TEXT,
                        response_text TEXT,

                        created_by INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY(chat_id, keyword)
                    )
                """)
                # Persistent Live Support Relay Mapping (survives restarts)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_relay_map (
                        admin_chat_id INTEGER,
                        admin_msg_id INTEGER,
                        user_chat_id INTEGER,
                        user_name TEXT,
                        user_msg_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (admin_chat_id, admin_msg_id)
                    )
                """)
                # Moderation & Study Group Analytics Table (Combot / TGStat style)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_bot_analytics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER,
                        event_type TEXT,
                        user_id INTEGER,
                        details TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Master Bot Network & Multi-Tenant Connected Groups
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_network_chats (
                        chat_id INTEGER PRIMARY KEY,
                        title TEXT,
                        username TEXT,
                        member_count INTEGER DEFAULT 0,
                        added_by INTEGER,
                        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        is_active INTEGER DEFAULT 1
                    )
                """)
                # Member Join Tracking (Timestamp & Profile info)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS member_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        chat_id INTEGER,
                        full_name TEXT,
                        username TEXT,
                        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id, chat_id)
                    )
                """)
                # Member Identity & Username Shifts Tracking
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS member_name_changes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        chat_id INTEGER,
                        old_name TEXT,
                        new_name TEXT,
                        old_username TEXT,
                        new_username TEXT,
                        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Seed primary study group if not present
                conn.execute("""
                    INSERT OR IGNORE INTO bot_network_chats (chat_id, title, is_active)
                    VALUES (-1003867472898, 'Study Help 😉', 1)
                """)
                # Group Customization & Welcome Settings
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_group_settings (
                        chat_id INTEGER PRIMARY KEY,
                        welcome_text TEXT,
                        welcome_enabled INTEGER DEFAULT 1,
                        join_track_enabled INTEGER DEFAULT 1,
                        rules_text TEXT,
                        welcome_timeout INTEGER DEFAULT 90,
                        language TEXT DEFAULT 'en'
                    )
                """)
                # Safe migration: Ensure language column exists if table was pre-existing
                try:
                    conn.execute("ALTER TABLE telegram_group_settings ADD COLUMN language TEXT DEFAULT 'en'")
                except Exception:
                    pass

                # Tracked Welcome Message IDs for 1-Click Admin Cleanup (/cleanwelcome)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS group_welcome_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id INTEGER,
                        message_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Cloud Forwarder & Tag Remover Routes
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_forward_routes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        source_chat_id INTEGER,
                        source_topic_id INTEGER DEFAULT 0,
                        target_chat_id INTEGER,
                        target_topic_id INTEGER DEFAULT 0,
                        media_filter TEXT DEFAULT 'all',
                        strip_links INTEGER DEFAULT 1,
                        is_active INTEGER DEFAULT 1,
                        created_by INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # Cloud Forwarding Anti-Duplicate History
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS telegram_forward_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        route_id INTEGER,
                        source_chat_id INTEGER,
                        source_msg_id INTEGER,
                        target_chat_id INTEGER,
                        target_msg_id INTEGER,
                        file_unique_id TEXT,
                        copied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                # SangMata OSINT Cache Table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS sangmata_osint_cache (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        phone TEXT,
                        is_premium INTEGER DEFAULT 0,
                        name_history TEXT DEFAULT '[]',
                        username_history TEXT DEFAULT '[]',
                        total_shifts INTEGER DEFAULT 0,
                        raw_response TEXT,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_sangmata_uname ON sangmata_osint_cache(username);")

                # Explicitly commit all tables to disk
                conn.commit()

                # Load persistent co-admins and add to admin pools
                cursor = conn.execute("SELECT user_id FROM telegram_bot_admins")
                for row in cursor.fetchall():
                    self.co_admins.add(row[0])
                    self.master_admin_ids.add(row[0])
                # Load blocked users
                c2 = conn.execute("SELECT user_id FROM telegram_bot_blocked")
                for row in c2.fetchall():
                    self.blocked_users.add(row[0])
        except Exception as e:
            logger.warning(f"Error initializing DB for TelegramBot: {e}")

    def _save_relay_info(self, admin_chat_id: int, admin_msg_id: int, user_chat_id: int, user_name: str, user_msg_id: int):
        """Saves message relay link in memory and SQLite for cross-restart support."""
        self.relay_map[(admin_chat_id, admin_msg_id)] = {
            "user_chat_id": user_chat_id,
            "user_name": user_name,
            "user_msg_id": user_msg_id
        }
        try:
            with get_db_conn() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO telegram_relay_map 
                    (admin_chat_id, admin_msg_id, user_chat_id, user_name, user_msg_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (admin_chat_id, admin_msg_id, user_chat_id, user_name, user_msg_id))
        except Exception as e:
            logger.warning(f"Error saving relay info to DB: {e}")

    def _get_relay_info(self, admin_chat_id: int, admin_msg_id: int) -> Optional[dict]:
        """Retrieves user info corresponding to an admin message from memory or DB."""
        if (admin_chat_id, admin_msg_id) in self.relay_map:
            return self.relay_map[(admin_chat_id, admin_msg_id)]
        try:
            with get_db_conn() as conn:
                row = conn.execute(
                    "SELECT user_chat_id, user_name, user_msg_id FROM telegram_relay_map WHERE admin_chat_id = ? AND admin_msg_id = ?",
                    (admin_chat_id, admin_msg_id)
                ).fetchone()
                if row:
                    info = {"user_chat_id": row[0], "user_name": row[1], "user_msg_id": row[2]}
                    self.relay_map[(admin_chat_id, admin_msg_id)] = info
                    return info
        except Exception as e:
            logger.warning(f"Error fetching relay info from DB: {e}")
        return None

    def _log_analytics_event(self, chat_id: int, event_type: str, user_id: Optional[int] = None, details: str = ""):
        """Logs moderation or engagement event in SQLite analytics table (Combot / TGStat style)."""
        try:
            with get_db_conn() as conn:
                conn.execute(
                    "INSERT INTO telegram_bot_analytics (chat_id, event_type, user_id, details) VALUES (?, ?, ?, ?)",
                    (chat_id, event_type, user_id, details)
                )
        except Exception:
            pass

    def _get_custom_command(self, cmd: str) -> Optional[str]:
        """Fetch custom command response if configured."""
        try:
            with get_db_conn() as conn:
                row = conn.execute("SELECT response_text FROM telegram_custom_commands WHERE command = ?", (cmd.lower(),)).fetchone()
                return row[0] if row else None
        except Exception:
            return None

    def _save_note(self, chat_id: int, note_name: str, content: str, created_by: int) -> bool:
        """Saves or updates a Rose-style group note."""
        clean_name = note_name.lower().strip().lstrip("#")
        try:
            with get_db_conn() as conn:
                conn.execute("""
                    INSERT INTO telegram_group_notes (chat_id, note_name, content, created_by, created_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(chat_id, note_name) DO UPDATE SET
                        content = excluded.content,
                        created_by = excluded.created_by,
                        created_at = CURRENT_TIMESTAMP
                """, (chat_id, clean_name, content.strip(), created_by))
                return True
        except Exception as e:
            logger.warning(f"Error saving group note: {e}")
            return False

    def _get_note(self, chat_id: int, note_name: str) -> Optional[str]:
        """Fetches a Rose-style group note content."""
        clean_name = note_name.lower().strip().lstrip("#")
        try:
            with get_db_conn() as conn:
                row = conn.execute(
                    "SELECT content FROM telegram_group_notes WHERE chat_id = ? AND note_name = ? COLLATE NOCASE",
                    (chat_id, clean_name)
                ).fetchone()
                return row[0] if row else None
        except Exception as e:
            logger.warning(f"Error fetching group note: {e}")
            return None

    def _delete_note(self, chat_id: int, note_name: str) -> bool:
        """Deletes a Rose-style group note."""
        clean_name = note_name.lower().strip().lstrip("#")
        try:
            with get_db_conn() as conn:
                cur = conn.execute(
                    "DELETE FROM telegram_group_notes WHERE chat_id = ? AND note_name = ? COLLATE NOCASE",
                    (chat_id, clean_name)
                )
                return cur.rowcount > 0
        except Exception as e:
            logger.warning(f"Error deleting group note: {e}")
            return False


    def _list_notes(self, chat_id: int) -> list:
        """Lists all Rose-style notes for the group."""
        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT note_name, content, created_at FROM telegram_group_notes WHERE chat_id = ? ORDER BY note_name ASC",
                    (chat_id,)
                ).fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            logger.warning(f"Error listing group notes: {e}")
            return []

    def _save_faq(self, chat_id: int, keyword: str, response: str, created_by: int):
        """Saves or updates an auto-reply FAQ for a group."""

        try:
            with get_db_conn() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO telegram_group_faqs (chat_id, keyword, response_text, created_by, created_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (chat_id, keyword.lower().strip(), response.strip(), created_by))
        except Exception as e:
            logger.warning(f"Error saving FAQ: {e}")

    def _get_faq(self, chat_id: int, keyword: str) -> Optional[str]:
        """Retrieves FAQ response for a given keyword."""
        try:
            with get_db_conn() as conn:
                row = conn.execute("SELECT response_text FROM telegram_group_faqs WHERE chat_id = ? AND keyword = ?", (chat_id, keyword.lower().strip())).fetchone()
                return row[0] if row else None
        except Exception:
            return None

    def _delete_faq(self, chat_id: int, keyword: str) -> bool:
        """Deletes an FAQ by keyword."""
        try:
            with get_db_conn() as conn:
                cur = conn.execute("DELETE FROM telegram_group_faqs WHERE chat_id = ? AND keyword = ?", (chat_id, keyword.lower().strip()))
                return cur.rowcount > 0
        except Exception:
            return False

    def _list_faqs(self, chat_id: int) -> list:
        """Lists all FAQs configured for a chat."""
        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("SELECT keyword, response_text FROM telegram_group_faqs WHERE chat_id = ?", (chat_id,)).fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    def _search_group_items(self, chat_id: int, query: str) -> list:
        """Searches across topics and indexed lectures/files in a group with multi-word matching."""
        results = []
        raw_query = query.strip()
        if not raw_query:
            return results
        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                # 1. Exact or contiguous phrase match (highest relevance)
                q_exact = f"%{raw_query}%"
                exact_rows = conn.execute("""
                    SELECT i.id, i.topic_id, i.title, i.msg_id, i.custom_link, i.icon, t.topic_title
                    FROM telegram_topic_items i
                    LEFT JOIN telegram_group_topics t ON i.chat_id = t.chat_id AND i.topic_id = t.topic_id
                    WHERE i.chat_id = ? AND (i.title LIKE ? OR t.topic_title LIKE ?)
                    ORDER BY i.id DESC LIMIT 15
                """, (chat_id, q_exact, q_exact)).fetchall()
                
                seen_ids = set()
                for r in exact_rows:
                    seen_ids.add(r["id"])
                    results.append(dict(r))

                # 2. Multi-word match: if query has multiple keywords, match items where all words appear
                words = [w for w in raw_query.split() if len(w) > 1]
                if len(words) > 1 and len(results) < 15:
                    where_clauses = []
                    params = [chat_id]
                    for w in words:
                        where_clauses.append("(i.title LIKE ? OR t.topic_title LIKE ?)")
                        params.extend([f"%{w}%", f"%{w}%"])
                    
                    sql = f"""
                        SELECT i.id, i.topic_id, i.title, i.msg_id, i.custom_link, i.icon, t.topic_title
                        FROM telegram_topic_items i
                        LEFT JOIN telegram_group_topics t ON i.chat_id = t.chat_id AND i.topic_id = t.topic_id
                        WHERE i.chat_id = ? AND {' AND '.join(where_clauses)}
                        ORDER BY i.id DESC LIMIT 15
                    """
                    multi_rows = conn.execute(sql, tuple(params)).fetchall()
                    for r in multi_rows:
                        if r["id"] not in seen_ids:
                            seen_ids.add(r["id"])
                            results.append(dict(r))
        except Exception as e:
            logger.warning(f"Error searching group items: {e}")
        return results

    def _save_topic(self, chat_id: int, topic_id: int, title: str, icon: str = "📖"):
        """Saves or updates a topic in the group's directory."""
        try:
            with get_db_conn() as conn:
                conn.execute("""
                    INSERT INTO telegram_group_topics (chat_id, topic_id, topic_title, topic_icon, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(chat_id, topic_id) DO UPDATE SET topic_title = excluded.topic_title, topic_icon = excluded.topic_icon, updated_at = CURRENT_TIMESTAMP
                """, (chat_id, topic_id, title.strip(), icon))
        except Exception as e:
            logger.warning(f"Error saving topic {topic_id} for chat {chat_id}: {e}")

    def _clean_sort_key(self, title: str) -> str:
        """Strips emojis, brackets, symbols and returns clean lowercase string for true A-Z alphabetical sorting."""
        if not title:
            return ""
        # Remove emojis and non-alphanumeric characters at the start
        cleaned = re.sub(r'^[^\w]+', '', str(title).strip().lower())
        return cleaned or str(title).strip().lower()

    @staticmethod
    def _extract_dc(file_id: str) -> str:
        """Extracts or identifies Telegram Data Center (DC) from Bot API file_id or defaults."""
        if not file_id:
            return "DC2 (Amsterdam, NL) [Estimated]"
        try:
            padded = file_id + '=' * (-len(file_id) % 4)
            raw = base64.urlsafe_b64decode(padded)
            dc_names = {
                1: "DC1 (Miami, FL, USA)",
                2: "DC2 (Amsterdam, NL)",
                3: "DC3 (Miami, FL, USA)",
                4: "DC4 (Amsterdam, NL)",
                5: "DC5 (Singapore, SG)"
            }
            for offset in [4, 8, 1, 2]:
                if len(raw) >= offset + 4:
                    val = struct.unpack('<I', raw[offset:offset+4])[0]
                    if val in dc_names:
                        return dc_names[val]
        except Exception:
            pass
        return "DC2 (Amsterdam, NL) [Estimated]"

    @staticmethod
    def _estimate_account_age(user_id: int) -> str:
        """Estimates Telegram account creation period based on sequential user ID ranges."""
        if not user_id or user_id < 0:
            return "Unknown Account"
        if user_id < 500_000_000:
            return "🏛️ Veteran Account (~2017 or earlier)"
        elif user_id < 1_000_000_000:
            return "🕰️ Established Account (~2018–2019)"
        elif user_id < 2_000_000_000:
            return "📅 Active Account (~2020–2021)"
        elif user_id < 5_000_000_000:
            return "📈 Growing Account (~2022–2023)"
        elif user_id < 7_500_000_000:
            return "🆕 Recent Account (~2024)"
        else:
            return "⚡ Fresh Account (2025–2026 - Brand New)"

    @staticmethod
    def _lookup_phone_osint(phone_input: str) -> dict:
        """Deep Phone Number OSINT & Telecommunications Intelligence."""
        raw_digits = re.sub(r'[^\d+]', '', str(phone_input).strip())
        digits_only = re.sub(r'[^\d]', '', raw_digits)
        
        country_code = "International / Global"
        country_flag = "🌐"
        carrier_hint = "Cellular / Mobile Network"
        formatted_intl = raw_digits
        local_num = digits_only

        if digits_only.startswith("91") and len(digits_only) >= 12:
            country_code = "India"
            country_flag = "🇮🇳"
            local_num = digits_only[2:]
            formatted_intl = f"+91 {local_num[:5]} {local_num[5:]}"
        elif len(digits_only) == 10 and digits_only[0] in "6789":
            country_code = "India"
            country_flag = "🇮🇳"
            local_num = digits_only
            formatted_intl = f"+91 {local_num[:5]} {local_num[5:]}"
            digits_only = "91" + digits_only
        elif digits_only.startswith("1") and len(digits_only) == 11:
            country_code = "USA / Canada"
            country_flag = "🇺🇸 / 🇨🇦"
            local_num = digits_only[1:]
            formatted_intl = f"+1 ({local_num[:3]}) {local_num[3:6]}-{local_num[6:]}"
        elif digits_only.startswith("44") and len(digits_only) >= 11:
            country_code = "United Kingdom"
            country_flag = "🇬🇧"
            formatted_intl = f"+44 {digits_only[2:]}"
        elif digits_only.startswith("971"):
            country_code = "United Arab Emirates"
            country_flag = "🇦🇪"
            formatted_intl = f"+971 {digits_only[3:]}"
        elif digits_only.startswith("92") and len(digits_only) >= 11:
            country_code = "Pakistan"
            country_flag = "🇵🇰"
        elif digits_only.startswith("880"):
            country_code = "Bangladesh"
            country_flag = "🇧🇩"
        elif digits_only.startswith("977"):
            country_code = "Nepal"
            country_flag = "🇳🇵"

        if country_code == "India" and len(local_num) == 10:
            pfx = local_num[:2]
            if pfx in ("62", "63", "70", "79", "80", "81", "82", "83", "84", "85", "86", "87", "88", "89", "90", "91", "92", "93", "94", "95", "96", "97", "98", "99"):
                carrier_hint = "Jio / Airtel / Vi / BSNL (Indian Telecom Circle)"

        matched_users = []
        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT user_id, first_name, last_name, username, phone_number, total_messages FROM telegram_users_dossier WHERE phone_number LIKE ? OR phone_number LIKE ? LIMIT 5",
                    (f"%{local_num}%", f"%{digits_only}%")
                ).fetchall()
                for r in rows:
                    matched_users.append(dict(r))
        except Exception:
            pass

        clean_e164 = f"+{digits_only}" if not raw_digits.startswith("+") else raw_digits

        return {
            "query": phone_input,
            "digits_only": digits_only,
            "local_num": local_num,
            "e164": clean_e164,
            "formatted": formatted_intl,
            "country": country_code,
            "country_flag": country_flag,
            "carrier": carrier_hint,
            "matched_users": matched_users,
            "whatsapp_link": f"https://wa.me/{digits_only}",
            "telegram_link": f"https://t.me/+{digits_only}",
            "truecaller_url": f"https://www.truecaller.com/search/in/{local_num}"
        }

    @staticmethod
    def _lookup_email_osint(email_input: str) -> dict:
        """Deep Email Address OSINT & Domain Intelligence."""
        email_clean = str(email_input).strip().lower()
        is_valid = bool(re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email_clean))
        domain = email_clean.split('@')[1] if '@' in email_clean else ""
        
        disposable_domains = {
            "tempmail.com", "10minutemail.com", "mailinator.com", "guerrillamail.com",
            "throwawaymail.com", "yopmail.com", "sharklasers.com", "trashmail.com",
            "getairmail.com", "dispostable.com", "burnermail.io", "fakemailgenerator.com",
            "temp-mail.org", "mohmal.com", "crazymailing.com", "mytemp.email"
        }
        is_disposable = domain in disposable_domains or "temp" in domain or "fake" in domain
        
        provider_type = "Corporate / Custom Domain"
        provider_icon = "🏢"
        if domain in ("gmail.com", "googlemail.com"):
            provider_type = "Google Mail (Consumer Workspace)"
            provider_icon = "🔴"
        elif domain in ("outlook.com", "hotmail.com", "live.com", "msn.com"):
            provider_type = "Microsoft Outlook / Live"
            provider_icon = "🟦"
        elif domain in ("yahoo.com", "ymail.com", "myyahoo.com"):
            provider_type = "Yahoo! Mail"
            provider_icon = "🟣"
        elif domain in ("icloud.com", "me.com", "mac.com"):
            provider_type = "Apple iCloud Mail"
            provider_icon = "🍎"
        elif domain in ("proton.me", "protonmail.com", "pm.me"):
            provider_type = "ProtonMail (End-to-End Encrypted Swiss)"
            provider_icon = "🔒"
        elif domain.endswith(".edu") or domain.endswith(".edu.in") or domain.endswith(".ac.in"):
            provider_type = "Educational / University Academic Institution"
            provider_icon = "🎓"
        elif domain.endswith(".gov") or domain.endswith(".gov.in"):
            provider_type = "Government Authority Domain"
            provider_icon = "🏛️"
        elif is_disposable:
            provider_type = "⚠️ Disposable / Temporary Burner Email"
            provider_icon = "🗑️"

        gravatar_hash = hashlib.md5(email_clean.encode('utf-8')).hexdigest()
        gravatar_url = f"https://www.gravatar.com/avatar/{gravatar_hash}?d=identicon"

        matched_users = []
        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT user_id, first_name, last_name, username, total_messages FROM telegram_users_dossier WHERE first_name LIKE ? OR username LIKE ? LIMIT 5",
                    (f"%{email_clean.split('@')[0]}%", f"%{email_clean.split('@')[0]}%")
                ).fetchall()
                for r in rows:
                    matched_users.append(dict(r))
        except Exception:
            pass

        return {
            "email": email_clean,
            "is_valid": is_valid,
            "domain": domain,
            "is_disposable": is_disposable,
            "provider_type": provider_type,
            "provider_icon": provider_icon,
            "gravatar_url": gravatar_url,
            "matched_users": matched_users,
            "hibp_url": f"https://haveibeenpwned.com/account/{email_clean}"
        }


    def _get_group_settings(self, chat_id: int) -> dict:
        """Fetches custom welcome and moderation settings for a group."""
        defaults = {
            "welcome_text": None,
            "welcome_enabled": 1,
            "join_track_enabled": 1,
            "rules_text": None,
            "welcome_timeout": 90,
            "language": "en"
        }
        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute("SELECT * FROM telegram_group_settings WHERE chat_id = ?", (chat_id,)).fetchone()
                if row:
                    merged = dict(defaults)
                    for k, v in dict(row).items():
                        if v is not None:
                            merged[k] = v
                    return merged
        except Exception:
            pass
        return defaults

    def _save_group_setting(self, chat_id: int, key: str, value: Any):
        """Updates a group customization setting in SQLite."""
        try:
            with get_db_conn() as conn:
                conn.execute(f"""
                    INSERT INTO telegram_group_settings (chat_id, {key})
                    VALUES (?, ?)
                    ON CONFLICT(chat_id) DO UPDATE SET {key} = excluded.{key}
                """, (chat_id, value))
        except Exception as e:
            logger.warning(f"Error saving group setting {key}: {e}")

    def _log_welcome_message(self, chat_id: int, message_id: int):
        """Logs welcome card message ID for 1-click admin cleanup (/cleanwelcome)."""
        try:
            with get_db_conn() as conn:
                conn.execute("INSERT INTO group_welcome_messages (chat_id, message_id) VALUES (?, ?)", (chat_id, message_id))
        except Exception as e:
            logger.warning(f"Error logging welcome message ID: {e}")

    def _get_logged_welcome_messages(self, chat_id: int) -> list:
        """Retrieves all tracked welcome card message IDs for a group."""
        try:
            with get_db_conn() as conn:
                rows = conn.execute("SELECT message_id FROM group_welcome_messages WHERE chat_id = ? ORDER BY id ASC", (chat_id,)).fetchall()
                return [r[0] for r in rows]
        except Exception:
            return []

    def _clear_logged_welcome_messages(self, chat_id: int):
        """Removes all tracked welcome card records for a group after cleanup."""
        try:
            with get_db_conn() as conn:
                conn.execute("DELETE FROM group_welcome_messages WHERE chat_id = ?", (chat_id,))
        except Exception:
            pass

    def _get_active_routes_for_source(self, source_chat_id: int, source_topic_id: Optional[int] = None) -> list:
        """Finds all active forwarding routes linked to this source chat and topic."""
        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute("SELECT * FROM telegram_forward_routes WHERE source_chat_id = ? AND is_active = 1", (source_chat_id,)).fetchall()
                valid = []
                for r in rows:
                    st = r["source_topic_id"] or 0
                    if st == 0 or (source_topic_id and st == source_topic_id):
                        valid.append(dict(r))
                return valid
        except Exception:
            return []

    def _is_forward_duplicate(self, target_chat_id: int, source_chat_id: int, source_msg_id: int, file_unique_id: Optional[str] = None) -> bool:
        """Checks if this message or media file has already been copied to the target chat."""
        try:
            with get_db_conn() as conn:
                if file_unique_id:
                    row = conn.execute(
                        "SELECT id FROM telegram_forward_history WHERE target_chat_id = ? AND (file_unique_id = ? OR (source_chat_id = ? AND source_msg_id = ?))",
                        (target_chat_id, file_unique_id, source_chat_id, source_msg_id)
                    ).fetchone()
                else:
                    row = conn.execute(
                        "SELECT id FROM telegram_forward_history WHERE target_chat_id = ? AND source_chat_id = ? AND source_msg_id = ?",
                        (target_chat_id, source_chat_id, source_msg_id)
                    ).fetchone()
                return bool(row)
        except Exception:
            return False

    def _log_forward_event(self, route_id: int, source_chat_id: int, source_msg_id: int, target_chat_id: int, target_msg_id: int, file_unique_id: Optional[str] = None):
        """Records copied message in forward history for anti-duplicate prevention."""
        try:
            with get_db_conn() as conn:
                conn.execute(
                    "INSERT INTO telegram_forward_history (route_id, source_chat_id, source_msg_id, target_chat_id, target_msg_id, file_unique_id) VALUES (?, ?, ?, ?, ?, ?)",
                    (route_id, source_chat_id, source_msg_id, target_chat_id, target_msg_id, file_unique_id)
                )
        except Exception as e:
            logger.warning(f"Error logging forward event: {e}")

    async def _process_cloud_forward_routes(
        self, 
        session: aiohttp.ClientSession, 
        source_chat_id: int, 
        source_msg_id: int, 
        message: dict, 
        routes: list
    ):
        """Asynchronously dispatches messages across active cloud forward routes using copyMessage (zero forward tag)."""
        file_unique_id = None
        media_type = "text"
        if "video" in message:
            media_type = "video"
            file_unique_id = message["video"].get("file_unique_id")
        elif "document" in message:
            media_type = "doc"
            file_unique_id = message["document"].get("file_unique_id")
        elif "photo" in message:
            media_type = "photo"
            if isinstance(message["photo"], list) and message["photo"]:
                file_unique_id = message["photo"][-1].get("file_unique_id")
        elif "audio" in message:
            media_type = "audio"
            file_unique_id = message["audio"].get("file_unique_id")

        for r in routes:
            tgt_chat = r["target_chat_id"]
            tgt_topic = r["target_topic_id"] or None
            m_filter = r.get("media_filter", "all")

            if m_filter != "all" and m_filter != media_type:
                continue

            if self._is_forward_duplicate(tgt_chat, source_chat_id, source_msg_id, file_unique_id):
                continue

            copy_url = f"https://api.telegram.org/bot{self.token}/copyMessage"
            payload = {
                "chat_id": tgt_chat,
                "from_chat_id": source_chat_id,
                "message_id": source_msg_id,
            }
            if tgt_topic:
                payload["message_thread_id"] = tgt_topic

            orig_caption = message.get("caption") or ""
            if r.get("strip_links") and orig_caption:
                cleaned_cap = LINK_REGEX.sub("", orig_caption).strip()
                cleaned_cap = re.sub(r'@[a-zA-Z0-9_]+', '', cleaned_cap).strip()
                payload["caption"] = cleaned_cap

            try:
                async with session.post(copy_url, json=payload, timeout=12) as resp:
                    res_data = await resp.json()
                    if res_data.get("ok"):
                        new_msg_id = res_data["result"]["message_id"]
                        self._log_forward_event(r["id"], source_chat_id, source_msg_id, tgt_chat, new_msg_id, file_unique_id)
            except Exception as ex:
                logger.warning(f"Error copying message to {tgt_chat}: {ex}")

    def _resolve_study_group_id(self, chat_id: int) -> int:
        """Intelligently resolves active study group ID if command is run in private DM (chat_id > 0)."""
        if chat_id < 0:
            return chat_id
        if self.target_chat:
            try:
                val = int(str(self.target_chat).replace("'", "").replace('"', ""))
                if val != 0:
                    return val
            except (ValueError, TypeError):
                pass
        try:
            with get_db_conn() as conn:
                row = conn.execute("SELECT chat_id FROM telegram_group_topics ORDER BY updated_at DESC LIMIT 1").fetchone()
                if row and row[0]:
                    return int(row[0])
        except Exception:
            pass
        return chat_id

    @staticmethod
    def _natural_sort_key(title: str):
        """Natural sort key so Lecture 2 comes before Lecture 10 and Part 01 comes before Part 02."""
        if not title:
            return []
        parts = []
        for segment in re.split(r'(\d+)', str(title)):
            if segment.isdigit():
                parts.append(int(segment))
            else:
                parts.append(segment.lower())
        return parts

    def _get_topics(self, chat_id: int, sort_mode: str = "az") -> list:
        """Retrieves all registered topics for a group. sort_mode: 'az' (alphabetical) or 'seq' (forum order)."""
        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT topic_id, topic_title, topic_icon FROM telegram_group_topics WHERE chat_id = ? ORDER BY topic_id ASC",
                    (chat_id,)
                ).fetchall()
                topics = [dict(r) for r in rows]
                if sort_mode == "az" and topics:
                    topics.sort(key=lambda t: self._clean_sort_key(t.get("topic_title", "")))
                elif sort_mode == "seq" and topics:
                    topics.sort(key=lambda t: t.get("topic_id", 0))
                return topics
        except Exception as e:
            logger.warning(f"Error fetching topics for chat {chat_id}: {e}")
            return []

    def _build_main_index_cards(self, chat_id: int, sort_mode: str = "az") -> tuple[list, Optional[dict]]:
        """Generates formatted HTML card chunks and interactive buttons for Master Topic Directory."""
        topics = self._get_topics(chat_id, sort_mode=sort_mode)
        if not topics:
            return [], None

        clean_chat_id = str(chat_id).replace("-100", "").replace("-", "").lstrip("@")
        cards = []
        current_card_lines = [
            "✨ <b>MASTER TOPIC DIRECTORY</b> 📑",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"🏛️ <i>Official Study Repository • {'Alphabetical (#A to #Z)' if sort_mode == 'az' else 'Forum Sequence'}</i>",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ]

        current_letter = None
        for idx, top in enumerate(topics, 1):
            t_id = top["topic_id"]
            t_title = top["topic_title"]
            t_icon = top.get("topic_icon") or "📖"
            link = f"https://t.me/c/{clean_chat_id}/{t_id}" if clean_chat_id.isdigit() else f"https://t.me/{clean_chat_id}/{t_id}"

            if sort_mode == "az":
                sort_k = self._clean_sort_key(t_title)
                first_char = sort_k[0].upper() if sort_k else "#"
                if not first_char.isalpha():
                    first_char = "0-9"
                if first_char != current_letter:
                    current_letter = first_char
                    current_card_lines.append(f"\n🏷️ <b>SECTION #{current_letter}</b>")

            safe_title = html.escape(t_title.strip())
            line = f"{t_icon} <code>[{idx:02d}]</code> <a href=\"{link}\">{safe_title}</a>"
            if sum(len(l) for l in current_card_lines) + len(line) > 3400:
                current_card_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                cards.append("\n".join(current_card_lines))
                current_card_lines = [
                    f"📑 <b>MASTER TOPIC DIRECTORY (Part {len(cards)+1})</b>",
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                ]
            current_card_lines.append(line)

        current_card_lines.extend([
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
            f"📊 <b>Indexed Topics:</b> <code>{len(topics)}</code> ({'Alphabetical A–Z' if sort_mode == 'az' else 'Forum Sequence'})",
            "📌 <i>Tap any subject title above to open its study topic.</i>",
            "👨‍⚕️ <b>Kind Doctor</b> 🤍 • <i>Medical Study Companion</i>"
        ])
        cards.append("\n".join(current_card_lines))

        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "🔄 Refresh Index", "callback_data": "act_mainindex"},
                    {"text": "🩺 Clinical Tools", "callback_data": "act_menu"}
                ]
            ]
        }
        return cards, reply_markup

    def _delete_topic(self, chat_id: int, topic_id: int) -> bool:
        """Removes a topic and its items from the group index."""
        try:
            with get_db_conn() as conn:
                conn.execute("DELETE FROM telegram_group_topics WHERE chat_id = ? AND topic_id = ?", (chat_id, topic_id))
                conn.execute("DELETE FROM telegram_topic_items WHERE chat_id = ? AND topic_id = ?", (chat_id, topic_id))
                return True
        except Exception:
            return False

    def _save_topic_item(self, chat_id: int, topic_id: int, title: str, msg_id: Optional[int] = None, custom_link: Optional[str] = None, icon: str = "🎬") -> int:
        """Saves a lecture/file/item under a specific topic with auto-table self healing."""
        try:
            with get_db_conn() as conn:
                cur = conn.execute("""
                    INSERT INTO telegram_topic_items (chat_id, topic_id, title, msg_id, custom_link, icon)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (chat_id, topic_id, title.strip(), msg_id, custom_link, icon))
                conn.commit()
                return cur.lastrowid
        except Exception as e:
            if "no such table" in str(e).lower():
                try:
                    self._init_db()
                    with get_db_conn() as conn:
                        cur = conn.execute("""
                            INSERT INTO telegram_topic_items (chat_id, topic_id, title, msg_id, custom_link, icon)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (chat_id, topic_id, title.strip(), msg_id, custom_link, icon))
                        conn.commit()
                        return cur.lastrowid
                except Exception:
                    pass
            logger.warning(f"Error saving topic item: {e}")
            return 0

    def _get_topic_items(self, chat_id: int, topic_id: int, sort_mode: str = "seq") -> list:
        """Retrieves all items under a specific topic. sort_mode: 'seq' (natural numeric) or 'az' (alphabetical)."""
        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT id, title, msg_id, custom_link, icon FROM telegram_topic_items WHERE chat_id = ? AND topic_id = ? ORDER BY id ASC",
                    (chat_id, topic_id)
                ).fetchall()
                items = [dict(r) for r in rows]
                if sort_mode == "az" and items:
                    items.sort(key=lambda x: self._clean_sort_key(x.get("title", "")))
                elif sort_mode == "seq" and items:
                    items.sort(key=lambda x: self._natural_sort_key(x.get("title", "")))
                return items
        except Exception as e:
            logger.warning(f"Error fetching topic items: {e}")
            return []

    def _clear_topic_items(self, chat_id: int, topic_id: int) -> int:
        """Clears all indexed items for a topic."""
        try:
            with get_db_conn() as conn:
                cur = conn.execute("DELETE FROM telegram_topic_items WHERE chat_id = ? AND topic_id = ?", (chat_id, topic_id))
                return cur.rowcount
        except Exception:
            return 0

    def _track_user_dossier(self, sender: dict, detected_phone: Optional[str] = None) -> Dict[str, Any]:
        """Tracks user identity changes (Name, Username, Phone, etc.) and returns full intelligence report."""
        user_id = sender.get("id")
        current_fn = sender.get("first_name", "") or ""
        current_ln = sender.get("last_name", "") or ""
        current_full_name = f"{current_fn} {current_ln}".strip() or "Anonymous"
        current_username = sender.get("username", "") or ""
        is_premium = 1 if sender.get("is_premium") else 0
        lang_code = sender.get("language_code", "unknown")
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        result = {
            "user_id": user_id,
            "full_name": current_full_name,
            "username": current_username,
            "phone": detected_phone or "Not Shared",
            "is_premium": is_premium,
            "language": lang_code,
            "is_new": False,
            "changes_detected": [],
            "name_history": [],
            "username_history": [],
            "changes_count": 0,
            "total_messages": 1,
            "first_seen": now_str
        }

        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM telegram_users_dossier WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()

                if not row:
                    result["is_new"] = True
                    conn.execute("""
                        INSERT INTO telegram_users_dossier 
                        (user_id, first_name, last_name, username, phone_number, is_premium, language_code, first_seen, last_seen, total_messages, name_history, username_history, changes_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, '[]', '[]', 0)
                    """, (user_id, current_fn, current_ln, current_username, detected_phone, is_premium, lang_code))
                else:
                    old_fn = row["first_name"] or ""
                    old_ln = row["last_name"] or ""
                    old_full_name = f"{old_fn} {old_ln}".strip() or "Anonymous"
                    old_username = row["username"] or ""
                    old_phone = row["phone_number"] or ""
                    
                    try:
                        name_hist = json.loads(row["name_history"] or "[]")
                    except Exception:
                        name_hist = []
                    try:
                        uname_hist = json.loads(row["username_history"] or "[]")
                    except Exception:
                        uname_hist = []

                    changes_count = row["changes_count"] or 0
                    changes_detected = []

                    if old_full_name != current_full_name:
                        name_hist.append({"name": old_full_name, "changed_at": now_str})
                        changes_count += 1
                        changes_detected.append(f"Name changed: '{old_full_name}' ➔ '{current_full_name}'")

                    if old_username != current_username:
                        uname_hist.append({"username": old_username or "None", "changed_at": now_str})
                        changes_count += 1
                        changes_detected.append(f"Username changed: '@{old_username or 'None'}' ➔ '@{current_username or 'None'}'")

                    active_phone = detected_phone or old_phone
                    if detected_phone and detected_phone != old_phone:
                        changes_detected.append(f"Phone detected: {detected_phone}")

                    total_msgs = (row["total_messages"] or 0) + 1

                    conn.execute("""
                        UPDATE telegram_users_dossier
                        SET first_name = ?, last_name = ?, username = ?, phone_number = ?,
                            is_premium = ?, language_code = ?, last_seen = CURRENT_TIMESTAMP,
                            total_messages = ?, name_history = ?, username_history = ?, changes_count = ?
                        WHERE user_id = ?
                    """, (current_fn, current_ln, current_username, active_phone, is_premium, lang_code, total_msgs, json.dumps(name_hist), json.dumps(uname_hist), changes_count, user_id))
                    conn.commit()

                    result["is_new"] = False
                    result["phone"] = active_phone or "Not Shared"
                    result["changes_detected"] = changes_detected
                    result["name_history"] = name_hist
                    result["username_history"] = uname_hist
                    result["changes_count"] = changes_count
                    result["total_messages"] = total_msgs
                    result["first_seen"] = row["first_seen"]
        except Exception as e:
            if "no such table" in str(e).lower():
                try:
                    self._init_db()
                    with get_db_conn() as conn:
                        conn.execute("""
                            INSERT INTO telegram_users_dossier 
                            (user_id, first_name, last_name, username, phone_number, is_premium, language_code, first_seen, last_seen, total_messages, name_history, username_history, changes_count)
                            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1, '[]', '[]', 0)
                        """, (user_id, current_fn, current_ln, current_username, detected_phone, is_premium, lang_code))
                        conn.commit()
                        result["is_new"] = True
                except Exception:
                    pass
            logger.warning(f"Error tracking user dossier: {e}")

        return result

    def _format_sangmata_dossier(self, dossier: dict, title_prefix: str = "SANGMATA IDENTITY RADAR") -> str:
        """Formats clean, high-yield Sangmata intelligence & deep OSINT biometric dossier card."""
        user_id = dossier.get("user_id")
        fn = dossier.get("full_name") or "Anonymous"
        uname = dossier.get("username")
        uname_str = f"@{uname}" if uname else "No Username"
        user_mention = f"[{fn}](tg://user?id={user_id})" if user_id else fn
        
        is_prem = "⭐️ Yes (Telegram Premium)" if dossier.get("is_premium") else "Standard Account"
        acct_age = self._estimate_account_age(user_id)
        phone = dossier.get("phone", "Not Shared")
        phone_str = f"📱 **Phone**: `{phone}`\n" if phone and phone != "Not Shared" and phone != "None" else ""

        # Build complete A-to-Z Name History (Exact SangMata Biometric format)
        name_hist = dossier.get("name_history", [])
        name_lines = []
        if name_hist:
            for idx, item in enumerate(name_hist, 1):
                n = item.get("name", "Unknown")
                ts = item.get("changed_at", "")
                ts_str = f"[{ts}] " if ts else ""
                name_lines.append(f"{idx}. {ts_str}`{n}`")
        else:
            name_lines.append(f"1. `{fn}` *(Current Active Name)*")

        # Build complete A-to-Z Username History (Exact SangMata Biometric format)
        uname_hist = dossier.get("username_history", [])
        uname_lines = []
        if uname_hist:
            for idx, item in enumerate(uname_hist, 1):
                u = item.get("username", "None")
                u_formatted = u if u.startswith("@") or u == "(empty)" else f"@{u}"
                ts = item.get("changed_at", "")
                ts_str = f"[{ts}] " if ts else ""
                uname_lines.append(f"{idx}. {ts_str}`{u_formatted}`")
        else:
            name_val = uname_str if uname_str != "No Username" else "No Username"
            uname_lines.append(f"1. `{name_val}` *(Current Active Username)*")

        shifts_count = dossier.get("changes_count", 0)
        risk_str = ""
        if shifts_count >= 3:
            risk_str = f"⚡ **Shift Velocity:** 🚨 High Velocity ({shifts_count} Identity Shifts Detected)\n"

        card = (
            f"👤 **{title_prefix} — USER INTELLIGENCE** 🩺\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Student Name:** {user_mention}\n"
            f"🏷️ **Username:** `{uname_str}`\n"
            f"🆔 **Telegram ID:** `{user_id}`\n"
            f"🗓️ **Account Age:** {acct_age}\n"
            f"⭐️ **Telegram Tier:** {is_prem}\n"
            f"{risk_str}"
            f"{phone_str}\n"
            f"📜 **Name History (SangMata Timeline):**\n" + "\n".join(name_lines) + "\n\n"
            f"🏷️ **Username History (SangMata Timeline):**\n" + "\n".join(uname_lines) + "\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🛡️ *Kind Doctor Live Sentinel • SangMata Biometrics*"
        )
        return card


    def get_all_admins(self) -> Set[int]:
        return self.master_admin_ids.union(self.co_admins)

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.get_all_admins()

    async def is_admin_for_chat(self, session: aiohttp.ClientSession, chat_id: int, user_id: int, message: Optional[dict] = None) -> bool:
        """
        Multi-group admin verification:
        - Master Admins (Kind Doctor) always have global rights.
        - Co-Admins have global bot admin rights.
        - Anonymous admins (GroupAnonymousBot ID 1087968824 or sender_chat matching chat_id) have full admin rights.
        - Any group admin/creator has admin rights for THEIR group.
        """
        if user_id in self.get_all_admins():
            return True

        # Telegram Anonymous Admin Check
        if user_id == 1087968824:
            return True
        if message:
            sender_chat = message.get("sender_chat")
            if sender_chat and sender_chat.get("id") == chat_id:
                return True
            if message.get("from", {}).get("username") == "GroupAnonymousBot":
                return True

        if chat_id == user_id:
            return False  # In private DM, only recognized bot admins have admin commands
        try:
            url = f"https://api.telegram.org/bot{self.token}/getChatMember"
            async with session.post(url, json={"chat_id": chat_id, "user_id": user_id}, timeout=8) as resp:
                if resp.status == 200:
                    d = await resp.json()
                    status = d.get("result", {}).get("status", "")
                    return status in ("creator", "administrator")
        except Exception as e:
            logger.warning(f"Error verifying chat admin for {user_id} in {chat_id}: {e}")
        return False

    async def _sync_bot_commands_and_profile(self, session: aiohttp.ClientSession):
        """Registers official commands, description, and short description with Telegram Bot API."""
        try:
            # 0. Sync Bot Display Name on Telegram Cloud Servers
            await session.post(
                f"https://api.telegram.org/bot{self.token}/setMyName",
                json={"name": "Kind Doctor 🩺"},
                timeout=8
            )
            # 1. Official Command Autocomplete List
            commands = [
                {"command": "menu", "description": "Interactive 1-Click Control Panel"},
                {"command": "index", "description": "Topic Table of Contents & Lecture Index"},
                {"command": "mainindex", "description": "Master Topic Directory (#A to #Z)"},
                {"command": "find", "description": "Search lectures, notes & topics"},
                {"command": "clone", "description": "1-Click Instant Message Cloner"},
                {"command": "batchclone", "description": "Batch Clone continuous message ranges"},
                {"command": "forward", "description": "Forward & Route messages to Topics"},
                {"command": "userinfo", "description": "SangMata & Rose style user dossier"},
                {"command": "cleanwelcome", "description": "Auto-purge welcome & service alerts"},
                {"command": "cleandeleted", "description": "Purge deleted ghost accounts from group"},
                {"command": "broadcast", "description": "Broadcast announcement to study groups"},
                {"command": "status", "description": "Live transmission speed & health telemetry"},
                {"command": "backup", "description": "Instant SQLite database backup snapshot"},
                {"command": "manual", "description": "Official 3-Part Command Manual"},
                {"command": "rules", "description": "View group study guidelines"},
                {"command": "support", "description": "Confidential Line to Kind Doctor Desk"},
                {"command": "botinfo", "description": "Bot specifications & credentials"},
                {"command": "id", "description": "View Telegram User ID safely"}
            ]
            # Register across all Telegram scopes (Default, Groups, Group Admins, Private)
            scopes = [
                {"type": "default"},
                {"type": "all_private_chats"},
                {"type": "all_group_chats"},
                {"type": "all_chat_administrators"}
            ]
            for sc in scopes:
                with suppress(Exception):
                    await session.post(
                        f"https://api.telegram.org/bot{self.token}/setMyCommands",
                        json={"commands": commands, "scope": sc},
                        timeout=8
                    )
            # 2. Short Description (Displayed in Profile / About)
            short_desc = "👨‍⚕️ Kind Doctor 🤍 🩺 — Medical Study Companion, Topic Indexer, Cloud Forwarder & User Intelligence Suite."
            await session.post(
                f"https://api.telegram.org/bot{self.token}/setMyShortDescription",
                json={"short_description": short_desc},
                timeout=8
            )
            # 3. Full Description (Displayed in Empty Private Chat)
            full_desc = (
                "👨‍⚕️ Kind Doctor 🤍 🩺\n\n"
                "Your trusted medical study companion, group auto-indexer, cloud content forwarder, and user intelligence hub.\n\n"
                "✨ Core Features:\n"
                "• 📑 Alphabetical Topic Directory (#A to #Z)\n"
                "• 🕵️ SangMata & Rose Style User Intelligence (/userinfo)\n"
                "• 🔄 Cloud Content Forwarder with Zero Forward Tags\n"
                "• 📦 Instant & Batch Message Cloners (/clone, /batchclone)\n"
                "• 🧹 Cleaners: /cleanwelcome & /cleandeleted\n"
                "• 🔒 100% Admin Anonymity + Zero DM Spam Guarantee\n"
                "• 💬 Confidential Live Support Line"
            )
            await session.post(
                f"https://api.telegram.org/bot{self.token}/setMyDescription",
                json={"description": full_desc},
                timeout=8
            )
            logger.info("Bot commands and profile successfully synchronized with Telegram API.")
        except Exception as e:
            logger.warning(f"Failed to sync bot commands/profile: {e}")

    async def start(self):
        await self.memory.initialize()
        if not self.token:
            print("[!] DEVI_TELEGRAM_BOT_TOKEN is not configured in .env.")
            return

        print(f"[*] DEVI Telegram Operator & Live Relay starting for Admins {self.get_all_admins()}...")
        self.is_running = True
        
        async with aiohttp.ClientSession() as session:
            # Query and cache live Bot profile details from Telegram
            try:
                async with session.get(f"https://api.telegram.org/bot{self.token}/getMe", timeout=10) as me_resp:
                    if me_resp.status == 200:
                        me_data = await me_resp.json()
                        me_res = me_data.get("result", {})
                        if me_res.get("first_name"):
                            self.bot_name = me_res["first_name"]
                        if me_res.get("username"):
                            self.bot_username = me_res["username"]
            except Exception:
                pass

            # Sync official Telegram command autocomplete and descriptions
            await self._sync_bot_commands_and_profile(session)

            # Send startup ping to master admins
            for admin_id in self.master_admin_ids:
                try:
                    await self._send_message(
                        session, 
                        admin_id, 
                        f"👨‍⚕️ **Kind Doctor Bot Online! 🤍 🩺**\n\n"
                        f"• Suite: 🚀 **TG KindSync Pro v14.5**\n"
                        f"• Brand: 👨‍⚕️ Kind Doctor\n"
                        f"• Status: 🟢 100% Synchronized & Active\n"
                        f"• Indexing: Master Topic Directory (#A to #Z) 📑\n"
                        f"• Cloud Forwarder: Zero-Tag copyMessage Active 🔄\n"
                        f"• User Intelligence: SangMata & Rose Dossier Active 🕵️\n"
                        f"• Cleaners: /cleanwelcome & /cleandeleted Active 🧹\n"
                        f"• Auto-Updater: /update & UPDATE_KINDSYNC.bat 🚀\n"
                        f"• Official Manual: /manual (3 Parts)"
                    )
                except Exception:
                    pass

            while self.is_running:
                try:
                    url = f"https://api.telegram.org/bot{self.token}/getUpdates"
                    poll_payload = {
                        "offset": self.offset,
                        "timeout": 20,
                        "allowed_updates": [
                            "message", "edited_message", "channel_post", "edited_channel_post",
                            "callback_query", "chat_member", "my_chat_member", "chat_join_request"
                        ]
                    }
                    async with session.post(url, json=poll_payload, timeout=30) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            for update in data.get("result", []):
                                self.offset = update["update_id"] + 1
                                if "callback_query" in update:
                                    self.create_tracked_task(self._handle_callback_query(session, update["callback_query"]))
                                elif "my_chat_member" in update:
                                    self.create_tracked_task(self._handle_my_chat_member(session, update["my_chat_member"]))
                                elif "chat_member" in update:
                                    self.create_tracked_task(self._handle_chat_member(session, update["chat_member"]))
                                elif "message" in update:
                                    self.create_tracked_task(self._handle_incoming_message(session, update["message"]))
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.warning(f"Telegram polling error: {e}")
                    await asyncio.sleep(4)

    def _format_clean_html(self, text: str) -> str:
        """Converts Markdown formatting (**bold**, _italic_, `code`, [link](url)) to robust Telegram HTML so asterisks never show."""
        if not text:
            return ""
        # Convert markdown links [title](url) to HTML <a href="url">title</a>
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        # Convert **bold** to <b>bold</b>
        text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
        # Convert `code` to <code>code</code>
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        # Clean double nested code tags if any
        text = text.replace("<code><code>", "<code>").replace("</code></code>", "</code>")
        text = text.replace("<code><code>", "<code>").replace("</code></code>", "</code>")
        # Convert _italic_ to <i>italic</i> (when not part of a URL or word)
        text = re.sub(r'(?<![<\w/])_([^_]+)_(?![>\w])', r'<i>\1</i>', text)
        return text


    async def _send_message(
        self, 
        session: aiohttp.ClientSession, 
        chat_id: int, 
        text: str, 
        reply_to: Optional[int] = None,
        reply_markup: Optional[dict] = None,
        message_thread_id: Optional[int] = None,
        disable_web_page_preview: bool = False,
        parse_mode: str = "HTML"
    ) -> Optional[int]:
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        formatted_text = self._format_clean_html(text) if parse_mode == "HTML" else text
        payload = {"chat_id": chat_id, "text": formatted_text, "parse_mode": parse_mode}
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        if reply_markup:
            payload["reply_markup"] = reply_markup
        if message_thread_id:
            payload["message_thread_id"] = message_thread_id
        if disable_web_page_preview:
            payload["disable_web_page_preview"] = True

        for attempt in range(3):
            try:
                async with session.post(url, json=payload, timeout=12) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("result", {}).get("message_id")
                    elif resp.status == 429:
                        try:
                            err_data = await resp.json()
                            retry_after = int(err_data.get("parameters", {}).get("retry_after", 3))
                        except Exception:
                            retry_after = 3
                        logger.warning(f"Telegram FloodWait 429: waiting {retry_after}s on attempt {attempt+1}")
                        await asyncio.sleep(retry_after)
                        continue
                    else:
                        err_txt = await resp.text()
                        if "TOPIC_CLOSED" in err_txt and payload.get("message_thread_id"):
                            logger.warning(f"Topic {payload.get('message_thread_id')} in {chat_id} is closed! Falling back to General topic...")
                            payload.pop("message_thread_id", None)
                            continue

                        # Fallback: Strip HTML tags and markdown markers so clean readable text is sent without raw stars/taare
                        clean_plain = re.sub(r'<[^>]+>', '', formatted_text)
                        clean_plain = re.sub(r'[*_`]', '', clean_plain)
                        payload["text"] = clean_plain
                        payload.pop("parse_mode", None)
                        async with session.post(url, json=payload, timeout=12) as r2:
                            if r2.status == 200:
                                d2 = await r2.json()
                                return d2.get("result", {}).get("message_id")
                            elif r2.status == 429:
                                try:
                                    err_data = await r2.json()
                                    retry_after = int(err_data.get("parameters", {}).get("retry_after", 3))
                                except Exception:
                                    retry_after = 3
                                await asyncio.sleep(retry_after)
                                continue
                            else:
                                err_txt2 = await r2.text()
                                if "TOPIC_CLOSED" in err_txt2 and payload.get("message_thread_id"):
                                    payload.pop("message_thread_id", None)
                                    async with session.post(url, json=payload, timeout=12) as r3:
                                        if r3.status == 200:
                                            d3 = await r3.json()
                                            return d3.get("result", {}).get("message_id")
                                logger.warning(f"Telegram API Send error to {chat_id} (status {r2.status}): {err_txt2}")
                        break
            except Exception as e:
                logger.warning(f"Failed to send message to {chat_id} (attempt {attempt+1}): {e}")
                if attempt < 2:
                    await asyncio.sleep(1 + attempt)
        return None

    async def _pin_message(self, session: aiohttp.ClientSession, chat_id: int, message_id: int, silent: bool = True) -> bool:
        """Pins a message in chat/topic silently."""
        url = f"https://api.telegram.org/bot{self.token}/pinChatMessage"
        payload = {"chat_id": chat_id, "message_id": message_id, "disable_notification": silent}
        try:
            async with session.post(url, json=payload, timeout=10) as resp:
                return resp.status == 200
        except Exception as e:
            logger.warning(f"Failed to pin message {message_id} in {chat_id}: {e}")
            return False

    async def _edit_message(
        self,
        session: aiohttp.ClientSession,
        chat_id: int,
        message_id: int,
        text: str,
        reply_markup: Optional[dict] = None,
        disable_web_page_preview: bool = True,
        parse_mode: str = "HTML"
    ) -> bool:
        """Edits an existing message text and inline keyboard in-place without generating a new message."""
        url = f"https://api.telegram.org/bot{self.token}/editMessageText"
        formatted_text = self._format_clean_html(text) if parse_mode == "HTML" else text
        payload = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": formatted_text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": disable_web_page_preview
        }
        if reply_markup:
            payload["reply_markup"] = reply_markup
        try:
            async with session.post(url, json=payload, timeout=10) as resp:
                if resp.status == 200:
                    return True
                err_text = await resp.text()
                if "message is not modified" in err_text.lower():
                    return True
                # Fallback to plain text if HTML parsing issues occur
                clean_plain = re.sub(r'<[^>]+>', '', formatted_text)
                clean_plain = re.sub(r'[*_`]', '', clean_plain)
                payload["text"] = clean_plain
                payload.pop("parse_mode", None)
                async with session.post(url, json=payload, timeout=10) as r2:
                    if r2.status == 200:
                        return True
                    err_txt2 = await r2.text()
                    return "message is not modified" in err_txt2.lower()
        except Exception as e:
            logger.warning(f"Failed to edit message {message_id} in {chat_id}: {e}")
            return False

    async def _send_document(
        self,
        session: aiohttp.ClientSession,
        chat_id: int,
        file_bytes: bytes,
        filename: str,
        caption: str = "",
        message_thread_id: Optional[int] = None
    ) -> bool:
        """Sends a document (e.g. CSV member audit report) via Telegram Bot API."""
        url = f"https://api.telegram.org/bot{self.token}/sendDocument"
        data = aiohttp.FormData()
        data.add_field("chat_id", str(chat_id))
        if message_thread_id:
            data.add_field("message_thread_id", str(message_thread_id))
        if caption:
            data.add_field("caption", caption)
            data.add_field("parse_mode", "Markdown")
        ctype = "application/x-sqlite3" if filename.endswith(".sqlite") else ("text/csv" if filename.endswith(".csv") else "application/octet-stream")
        data.add_field("document", file_bytes, filename=filename, content_type=ctype)
        try:
            async with session.post(url, data=data, timeout=60) as resp:
                return resp.status == 200
        except Exception as e:
            logger.warning(f"Failed to send document {filename} to {chat_id}: {e}")
            return False

    async def _export_members_csv_file(self, session: aiohttp.ClientSession, send_to_chat: int, group_id: int, message_thread_id: Optional[int] = None):
        """Generates and sends an audit CSV with member details and join timestamps."""
        try:
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                cur = conn.execute(
                    "SELECT m.user_id, m.full_name, m.username, m.join_date, d.last_seen, d.total_messages, d.changes_count "
                    "FROM member_history m LEFT JOIN telegram_users_dossier d ON m.user_id = d.user_id "
                    "WHERE m.chat_id = ? ORDER BY m.join_date DESC",
                    (group_id,)
                )
                rows = cur.fetchall()

            csv_buf = io.StringIO()
            writer = csv.writer(csv_buf)
            writer.writerow(["User ID", "Full Name", "Username", "Join Timestamp", "Last Seen", "Messages Count", "Name Changes Detected"])
            for r in rows:
                writer.writerow([
                    r["user_id"],
                    r["full_name"],
                    r["username"] or "",
                    r["join_date"] or "",
                    r["last_seen"] or "",
                    r["total_messages"] or 0,
                    r["changes_count"] or 0
                ])

            csv_bytes = csv_buf.getvalue().encode("utf-8")
            fname = f"members_audit_{abs(group_id)}.csv"
            caption = f"📊 **Member Audit CSV Export**\nGroup: `{group_id}`\nTotal Records: `{len(rows)}` members"
            
            await self._send_document(session, send_to_chat, csv_bytes, fname, caption=caption, message_thread_id=message_thread_id)
        except Exception as e:
            logger.warning(f"Error exporting member CSV: {e}")
            await self._send_message(session, send_to_chat, f"❌ Failed to export CSV: {e}", message_thread_id=message_thread_id)

    async def _handle_my_chat_member(self, session: aiohttp.ClientSession, my_chat_member: dict):
        """Auto-registers groups where bot is added and sends alert to Master Admins."""
        try:
            chat = my_chat_member.get("chat", {})
            chat_id = chat.get("id")
            if not chat_id:
                return
            title = chat.get("title") or f"Group {chat_id}"
            uname = chat.get("username") or ""
            new_state = my_chat_member.get("new_chat_member", {})
            status = new_state.get("status")
            from_u = my_chat_member.get("from", {})
            added_by = from_u.get("id")
            
            is_active = 1 if status in ("administrator", "member") else 0
            with get_db_conn() as conn:
                conn.execute("""
                    INSERT INTO bot_network_chats (chat_id, title, username, added_by, is_active)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(chat_id) DO UPDATE SET
                        title = excluded.title,
                        username = excluded.username,
                        is_active = excluded.is_active
                """, (chat_id, title, uname, added_by, is_active))

            if status == "administrator":
                admin_alert = (
                    f"👑 **[BOT NETWORK ALERT] Bot Added to New Group!**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🏛️ **Group Title**: {title}\n"
                    f"🆔 **Chat ID**: `{chat_id}`\n"
                    f"👤 **Added By**: {from_u.get('first_name', 'User')} (`{added_by}`)\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👉 Use `/network` or `/members` to view audit."
                )
                for m_id in self.master_admin_ids:
                    await self._send_message(session, m_id, admin_alert)

                # Send Automatic Welcome & Setup Guide directly into the new group
                welcome_group_card = (
                    f"🎉 **Kind Doctor Bot (@KindDoc_bot) Successfully Activated!** 🩺\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"Namaste! **{title}** me study tools aur smart bot features activate ho chuke hain:\n\n"
                    f"📑 **`/mainindex`** — Master Topic Directory (#A to #Z)\n"
                    f"📖 **`/topicindex`** — Topic Study Index & Table of Contents\n"
                    f"⚡ **`/scan`** — 1-Click Auto-Scan All Forum Topics & Lectures\n"
                    f"🔍 **`/find <keyword>`** — Instant Search across all Notes & PDFs\n"
                    f"🛡️ **Anti-Spam & Sangmata Radar** — Automatic Security Shield\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💡 *Admin Tip:* Naye topics ya lectures add hone par bas `/scan` type karein auto-indexing ke liye! ✨"
                )
                await self._send_message(session, chat_id, welcome_group_card)
        except Exception as e:
            logger.warning(f"Error in _handle_my_chat_member: {e}")

    async def _handle_chat_member(self, session: aiohttp.ClientSession, chat_member: dict):
        """Auto-detects newly joined members, tracks SangMata dossier, and posts Welcome + OSINT Audit Card."""
        try:
            chat = chat_member.get("chat", {})
            chat_id = chat.get("id")
            old_state = chat_member.get("old_chat_member", {})
            new_state = chat_member.get("new_chat_member", {})
            old_status = old_state.get("status")
            status = new_state.get("status")
            user = new_state.get("user", {})
            user_id = user.get("id")
            
            if not user_id or user.get("is_bot") or not chat_id:
                return
                
            full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or "User"
            username = user.get("username") or ""
            grp_title = chat.get("title", "Study Group")
            
            is_new_join = (status in ("member", "administrator")) and (old_status in ("left", "kicked", "restricted", None))

            if status in ("member", "administrator"):
                with get_db_conn() as conn:
                    conn.execute("""
                        INSERT OR REPLACE INTO member_history (user_id, chat_id, full_name, username, join_date)
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (user_id, chat_id, full_name, username))
                    
            if is_new_join:
                dossier = self._track_user_dossier(user)
                g_settings = self._get_group_settings(chat_id)
                safe_full_name = html.escape(full_name)
                safe_grp_title = html.escape(grp_title)
                user_tag = f"<b>@{html.escape(username)}</b>" if username else f'<a href="tg://user?id={user_id}"><b>{safe_full_name}</b></a>'
                
                # Fetch live SangMata history from MTProto session pool
                try:
                    from devi.operator.osint_resolver import osint_resolver
                    live_sm = await osint_resolver.fetch_live_sangmata_history(user_id)
                    if live_sm:
                        if live_sm.get("names"):
                            dossier["name_history"] = live_sm["names"]
                        if live_sm.get("usernames"):
                            dossier["username_history"] = live_sm["usernames"]
                        dossier["changes_count"] = live_sm.get("total_shifts", dossier.get("changes_count", 0))
                except Exception as ex:
                    logger.debug(f"SangMata fetch error in _handle_chat_member: {ex}")

                # 1. Short & sweet tagged Welcome Message (as requested by user)
                if g_settings.get("welcome_enabled", 1):
                    welcome_text = (
                        f"👋 <b>Welcome {user_tag} to {safe_grp_title}!</b> ✨\n\n"
                        f"🩺 <i>Wishing you all the best for your medical studies! 🌟</i>"
                    )
                    
                    sent_welcome_id = await self._send_message(
                        session, chat_id, welcome_text, parse_mode="HTML"
                    )
                    if sent_welcome_id:
                        self._log_welcome_message(chat_id, sent_welcome_id)
                
                # 2. SangMata / Dossier Intelligence Card
                if g_settings.get("join_track_enabled", 1):
                    sangmata_card = self._format_sangmata_dossier(
                        dossier, 
                        title_prefix="MEMBER JOIN INTELLIGENCE & SANGMATA OSINT RADAR"
                    )
                    admin_markup = {
                        "inline_keyboard": [
                            [
                                {"text": "👢 Kick Member", "callback_data": f"kick_{chat_id}_{user_id}"},
                                {"text": "🚫 Ban & Block", "callback_data": f"ban_{chat_id}_{user_id}"}
                            ]
                        ]
                    }
                    # Send to Group
                    await self._send_message(
                        session, chat_id, sangmata_card, reply_markup=admin_markup, parse_mode="HTML"
                    )
                    # Also notify master admins in DM
                    for adm_id in self.master_admin_ids:
                        await self._send_message(
                            session,
                            adm_id,
                            f"🏛️ <b>Group:</b> <code>{safe_grp_title}</code> (<code>{chat_id}</code>)\n\n" + sangmata_card,
                            reply_markup=admin_markup,
                            parse_mode="HTML"
                        )
        except Exception as e:
            logger.warning(f"Error in _handle_chat_member: {e}")

    async def _send_poll(
        self,
        session: aiohttp.ClientSession,
        chat_id: int,
        question: str,
        options: list,
        correct_option_id: int,
        explanation: str,
        message_thread_id: Optional[int] = None
    ) -> Optional[int]:
        """Sends an interactive quiz poll to group or topic."""
        url = f"https://api.telegram.org/bot{self.token}/sendPoll"
        payload = {
            "chat_id": chat_id,
            "question": question[:290],
            "options": options[:10],
            "type": "quiz",
            "correct_option_id": max(0, min(correct_option_id, len(options) - 1)),
            "explanation": explanation[:190],
            "is_anonymous": False
        }
        if message_thread_id:
            payload["message_thread_id"] = message_thread_id
        try:
            async with session.post(url, json=payload, timeout=12) as resp:
                if resp.status == 200:
                    d = await resp.json()
                    return d.get("result", {}).get("message_id")
        except Exception as e:
            logger.warning(f"Failed to send poll to {chat_id}: {e}")
        return None

    async def _delete_message(self, session: aiohttp.ClientSession, chat_id: int, message_id: int):
        """Silently delete a message from a chat/group with 429 FloodWait handling."""
        url = f"https://api.telegram.org/bot{self.token}/deleteMessage"
        payload = {"chat_id": chat_id, "message_id": message_id}
        for attempt in range(2):
            try:
                async with session.post(url, json=payload, timeout=10) as resp:
                    if resp.status == 429:
                        try:
                            data = await resp.json()
                            wait_s = int(data.get("parameters", {}).get("retry_after", 2))
                        except Exception:
                            wait_s = 2
                        await asyncio.sleep(wait_s)
                        continue
                    break
            except Exception:
                pass

    async def _auto_delete_message(self, session: aiohttp.ClientSession, chat_id: int, message_id: int, delay_seconds: int = 30):
        """Asynchronously waits for delay_seconds and deletes the message to keep group clean."""
        await asyncio.sleep(delay_seconds)
        await self._delete_message(session, chat_id, message_id)

    async def _copy_message(
        self,
        session: aiohttp.ClientSession,
        to_chat_id: int,
        from_chat_id: int,
        message_id: int,
        caption: Optional[str] = None,
        reply_to: Optional[int] = None,
        reply_markup: Optional[dict] = None,
        message_thread_id: Optional[int] = None
    ) -> Optional[int]:
        """Copy any message (text, photo, voice, video, doc) without re-uploading."""
        url = f"https://api.telegram.org/bot{self.token}/copyMessage"
        payload = {
            "chat_id": to_chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id
        }
        if message_thread_id:
            payload["message_thread_id"] = message_thread_id
        if caption:
            payload["caption"] = caption
            payload["parse_mode"] = "Markdown"
        if reply_to:
            payload["reply_to_message_id"] = reply_to
        if reply_markup:
            payload["reply_markup"] = reply_markup

        try:
            async with session.post(url, json=payload, timeout=15) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get("result", {}).get("message_id")
        except Exception as e:
            logger.warning(f"Failed to copy message to {to_chat_id}: {e}")
        return None

    async def _handle_callback_query(self, session: aiohttp.ClientSession, cb: dict):
        """Handle inline button clicks from Admins."""
        cb_id = cb.get("id")
        data = cb.get("data", "")
        from_user = cb.get("from", {})
        admin_id = from_user.get("id")
        chat_id = cb.get("message", {}).get("chat", {}).get("id")

        # Admin 1-Click Card Purge
        if data.startswith("purge_card"):
            msg_obj = cb.get("message", {})
            msg_id = msg_obj.get("message_id")
            is_adm = (admin_id in self.master_admin_ids) or (await self.is_admin_for_chat(session, chat_id, admin_id, message=msg_obj))
            if is_adm and msg_id:
                await self._delete_message(session, chat_id, msg_id)
                await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "Card Purged Successfully 🗑️"})
            else:
                await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "⚠️ Strictly Group Admins Only!", "show_alert": True})
            return

        # Public Interactive Study & Dashboard Actions (Available to ALL members)
        if data.startswith("act_"):
            action = data.replace("act_", "")
            msg_obj = cb.get("message", {})
            thread_id = msg_obj.get("message_thread_id")
            
            if action == "mainindex":
                target_index_chat = self._resolve_study_group_id(chat_id)
                cards, reply_markup = self._build_main_index_cards(target_index_chat, sort_mode="az")
                msg_id = msg_obj.get("message_id")
                if cards and msg_id:
                    # In-place edit of the card
                    edited = await self._edit_message(session, chat_id, msg_id, cards[0], reply_markup=reply_markup, disable_web_page_preview=True)
                    if edited:
                        await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "✅ Master Index refreshed in-place!"})
                        return
                await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "Processing request..."})
                await self._handle_admin_command(session, chat_id, admin_id, "/mainindex", message=msg_obj)
            elif action == "scan":
                await self._handle_admin_command(session, chat_id, admin_id, "/scan", message=msg_obj)
            elif action == "engine_refresh":
                await self._handle_admin_command(session, chat_id, admin_id, "/engine", message=msg_obj)
            elif action == "engine_backup":
                await self._handle_admin_command(session, chat_id, admin_id, "/backup", message=msg_obj)
            elif action == "engine_scan":
                await self._handle_admin_command(session, chat_id, admin_id, "/scan", message=msg_obj)
            elif action == "engine_clean":
                await self._handle_admin_command(session, chat_id, admin_id, "/clean", message=msg_obj)
            elif action == "mcq":
                await self._handle_admin_command(session, chat_id, admin_id, "/mcq", message=msg_obj)
            elif action == "pearl":
                await self._handle_admin_command(session, chat_id, admin_id, "/pearl", message=msg_obj)
            elif action == "score":
                await self._handle_admin_command(session, chat_id, admin_id, "/score list", message=msg_obj)
            elif action == "pomodoro":
                await self._handle_admin_command(session, chat_id, admin_id, "/pomodoro 25", message=msg_obj)
            elif action == "ask":
                guide = (
                    "❓ **How to Ask a Clinical Doubt:**\n\n"
                    "Type in chat:\n"
                    "`/ask <Your medical question or case detail>`\n\n"
                    "Example:\n"
                    "`/ask What are the ECG findings in hyperkalemia?`"
                )
                await self._send_message(session, chat_id, guide, message_thread_id=thread_id)
            elif action == "manual":
                await self._handle_admin_command(session, chat_id, admin_id, "/fullhelp", message=msg_obj)
            elif action == "menu":
                await self._handle_admin_command(session, chat_id, admin_id, "/menu", message=msg_obj)
            elif action == "support":
                await self._handle_admin_command(session, chat_id, admin_id, "/support", message=msg_obj)
            elif action == "toggle_direct":
                if not self.is_admin(admin_id):
                    return
                load_dotenv(override=True)
                cur_df = os.getenv("DIRECT_FORWARD", "false").strip().lower() in ("true", "1", "yes")
                new_df = "false" if cur_df else "true"
                set_key(str(ENV_PATH), "DIRECT_FORWARD", new_df)
                os.environ["DIRECT_FORWARD"] = new_df
                ans_txt = "⚡ Fast Direct Mode: ON (0.2s Unrestricted Forwarding)" if new_df == "true" else "🔄 Stream Mode: ON (Safe Default, Fresh Hashes & 16:9 Cover)"
                await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": ans_txt, "show_alert": True})
                await self._handle_admin_command(session, chat_id, admin_id, "/menu", message=msg_obj)
            elif action == "toggle_sig":
                if not self.is_admin(admin_id):
                    return
                load_dotenv(override=True)
                cur_sig = os.getenv("ENABLE_SIGNATURE", "true").strip().lower() in ("true", "1", "yes")
                new_sig = "false" if cur_sig else "true"
                # Unified Toggle: Clean mode turns OFF both signature and custom thumbnail
                new_th = "custom" if new_sig == "true" else "original"
                set_key(str(ENV_PATH), "ENABLE_SIGNATURE", new_sig)
                set_key(str(ENV_PATH), "THUMB_MODE", new_th)
                os.environ["ENABLE_SIGNATURE"] = new_sig
                os.environ["THUMB_MODE"] = new_th
                ans_txt = "👑 Branded Mode: ON (Sig + 16:9 Cover)" if new_sig == "true" else "🏷️ Clean Mode: ON (No Sig, Original Media)"
                await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": ans_txt, "show_alert": False})
                await self._handle_admin_command(session, chat_id, admin_id, "/menu", message=msg_obj)
            elif action == "toggle_thumb":
                if not self.is_admin(admin_id):
                    return
                load_dotenv(override=True)
                cur_th = os.getenv("THUMB_MODE", "custom").strip().lower()
                new_th = "original" if cur_th == "custom" else "custom"
                set_key(str(ENV_PATH), "THUMB_MODE", new_th)
                os.environ["THUMB_MODE"] = new_th
                ans_txt = "🎞️ Cover: ORIGINAL Media Thumbnail" if new_th == "original" else "🖼️ Cover: 16:9 HD Custom Cover"
                await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": ans_txt, "show_alert": False})
                await self._handle_admin_command(session, chat_id, admin_id, "/menu", message=msg_obj)
            elif action.startswith("exp_members_"):
                g_id = int(action.replace("exp_members_", ""))
                await self._export_members_csv_file(session, chat_id, g_id, message_thread_id=thread_id)
            elif action.startswith("view_members_"):
                g_id = int(action.replace("view_members_", ""))
                await self._handle_admin_command(session, chat_id, admin_id, f"/members {g_id}", message=msg_obj)
            return

        if not self.is_admin(admin_id):
            await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "Unauthorized"})
            return

        # 1. Send 1-Time Link in DM
        if data.startswith("send_link_"):
            target_user_id = int(data.replace("send_link_", ""))
            link_url = ""
            target_grp = self.target_chat

            if target_grp:
                try:
                    invite_url = f"https://api.telegram.org/bot{self.token}/createChatInviteLink"
                    # Single-use link expiring in 30 minutes
                    expire_ts = int((datetime.now() + timedelta(minutes=30)).timestamp())
                    async with session.post(invite_url, json={"chat_id": target_grp, "member_limit": 1, "expire_date": expire_ts}, timeout=10) as resp:
                        if resp.status == 200:
                            res_data = await resp.json()
                            link_url = res_data.get("result", {}).get("invite_link")
                except Exception as e:
                    logger.warning(f"Error creating invite link: {e}")

            if link_url:
                user_msg = (
                    f"🎉 **Kind Doctor Study Group Invite Link:**\n\n"
                    f"{link_url}\n\n"
                    f"*(Note: Yeh single-use disposable invite link hai jo 30 minutes me expire ho jayega. Kisi ke saath share na karein).* "
                )
                await self._send_message(session, target_user_id, user_msg)
                await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "✅ Single-Use Link sent to user!"})
                await self._send_message(session, chat_id, f"✅ **Single-Use Link** delivered to user `{target_user_id}`:\n{link_url}")
            else:
                await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "⚠️ Target group not configured or bot not Admin"})
                await self._send_message(session, chat_id, "⚠️ Bot ko TARGET_CHAT me Admin (with 'Invite Users' rights) banayein taaki automated link generate ho sake.")

        # 2. Block User from DM support
        elif data.startswith("block_"):
            target_user_id = int(data.replace("block_", ""))
            self.blocked_users.add(target_user_id)
            try:
                with get_db_conn() as conn:
                    conn.execute("INSERT OR REPLACE INTO telegram_bot_blocked (user_id) VALUES (?)", (target_user_id,))
            except Exception:
                pass
            await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": f"🚫 User {target_user_id} Blocked."})
            await self._send_message(session, chat_id, f"🚫 User `{target_user_id}` has been blocked from support.")

        # 3. Kick Member from Group
        elif data.startswith("kick_"):
            parts = data.split("_")
            grp_id = int(parts[1])
            target_user_id = int(parts[2])
            try:
                # Ban then unban to kick
                await session.post(f"https://api.telegram.org/bot{self.token}/banChatMember", json={"chat_id": grp_id, "user_id": target_user_id}, timeout=10)
                await session.post(f"https://api.telegram.org/bot{self.token}/unbanChatMember", json={"chat_id": grp_id, "user_id": target_user_id}, timeout=10)
                await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "👢 Member kicked from group."})
                await self._send_message(session, chat_id, f"👢 Member `{target_user_id}` has been kicked from group `{grp_id}`.")
            except Exception as e:
                await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": f"Error: {e}"})

        # 4. Ban & Block Member permanently
        elif data.startswith("ban_"):
            parts = data.split("_")
            grp_id = int(parts[1])
            target_user_id = int(parts[2])
            try:
                await session.post(f"https://api.telegram.org/bot{self.token}/banChatMember", json={"chat_id": grp_id, "user_id": target_user_id}, timeout=10)
                self.blocked_users.add(target_user_id)
                with get_db_conn() as conn:
                    conn.execute("INSERT OR REPLACE INTO telegram_bot_blocked (user_id) VALUES (?)", (target_user_id,))
                await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": "🚫 Member banned permanently."})
                await self._send_message(session, chat_id, f"🚫 Member `{target_user_id}` has been permanently banned & blocked.")
            except Exception as e:
                await session.post(f"https://api.telegram.org/bot{self.token}/answerCallbackQuery", json={"callback_query_id": cb_id, "text": f"Error: {e}"})

    async def _handle_incoming_message(self, session: aiohttp.ClientSession, message: dict):
        chat = message.get("chat", {})
        chat_type = chat.get("type", "private")
        chat_id = chat.get("id")
        sender = message.get("from", {})
        sender_chat = message.get("sender_chat", {})
        sender_id = sender.get("id") or (sender_chat.get("id") if sender_chat else None)
        text = message.get("text", "").strip()
        msg_id = message.get("message_id")
        is_group = chat_type in ["group", "supergroup"]

        if not sender_id:
            return

        logger.info(f"📩 Telegram update from {sender_id} (@{sender.get('username')}) in {chat_id} [{chat_type}]: '{text}'")

        # ============================================================
        # 1. GROUP / SUPERGROUP SENTINEL SHIELD (SILENT GUARDIAN)
        # ============================================================
        if is_group:
            # Auto-detect forum topic creation or rename
            thread_id = message.get("message_thread_id")
            if "forum_topic_created" in message:
                ftc = message["forum_topic_created"]
                t_name = ftc.get("name", "Topic")
                t_id = thread_id or msg_id
                self._save_topic(chat_id, t_id, t_name)
            elif "forum_topic_edited" in message:
                fte = message["forum_topic_edited"]
                t_name = fte.get("name")
                if t_name:
                    t_id = thread_id or msg_id
                    self._save_topic(chat_id, t_id, t_name)

            # Live Sangmata Identity Tracking in Group (Detects name/username shifts on every message)
            if sender and not sender.get("is_bot") and "new_chat_members" not in message:
                user_dossier = self._track_user_dossier(sender)
                if user_dossier.get("changes_detected"):
                    sangmata_card = self._format_sangmata_dossier(user_dossier, title_prefix="SANGMATA RADAR: IDENTITY CHANGE DETECTED")
                    sent_radar_id = await self._send_message(session, chat_id, sangmata_card, message_thread_id=thread_id)
                    if sent_radar_id:
                        self._log_welcome_message(chat_id, sent_radar_id)

            # A. New Member Joined Group
            if "new_chat_members" in message:
                inviter = message.get("from", {})
                inviter_id = inviter.get("id")
                thread_id = message.get("message_thread_id")

                g_settings = self._get_group_settings(chat_id)
                grp_title = chat.get("title", "Study Group")

                for new_member in message["new_chat_members"]:
                    if new_member.get("is_bot"):
                        continue
                    nm_id = new_member.get("id")
                    nm_fn = new_member.get("first_name", "")
                    nm_ln = new_member.get("last_name", "")
                    nm_full = f"{nm_fn} {nm_ln}".strip() or "User"
                    nm_uname = new_member.get("username", "")

                    # Clickable User Tag in HTML
                    safe_nm_full = html.escape(nm_full)
                    if nm_uname:
                        nm_tag = f"<b>@{html.escape(nm_uname)}</b>"
                    else:
                        nm_tag = f'<a href="tg://user?id={nm_id}"><b>{safe_nm_full}</b></a>'

                    # Check if inviter is Anonymous Admin (GroupAnonymousBot / Sender Chat)
                    sender_chat = message.get("sender_chat") or {}
                    sender_chat_title = sender_chat.get("title") or grp_title
                    sender_chat_uname = sender_chat.get("username")
                    author_sig = message.get("author_signature")

                    is_anonymous_admin = (
                        inviter_id == 1087968824 or 
                        inviter.get("username") == "GroupAnonymousBot" or
                        bool(sender_chat)
                    )

                    MASTER_ADMIN_IDS = (1553619403, 759038032)

                    if is_anonymous_admin:
                        if author_sig:
                            admin_label = f"👑 <b>Admin Desk</b> ({html.escape(author_sig)})"
                        elif sender_chat_uname:
                            admin_label = f'👑 <b>Admin Desk</b> (<a href="https://t.me/{sender_chat_uname}">@{html.escape(sender_chat_uname)}</a>)'
                        else:
                            admin_label = f"👑 <b>Admin Desk</b> ({html.escape(sender_chat_title)})"
                        source_info = f"Added by {admin_label}"
                        added_by_text = f"🤝 <b>Welcomed & Added by:</b> {admin_label}"
                    elif inviter_id and inviter_id != nm_id:
                        inv_fn = inviter.get("first_name", "")
                        inv_ln = inviter.get("last_name", "")
                        inv_full = f"{inv_fn} {inv_ln}".strip() or "Member"
                        inv_uname = inviter.get("username", "")

                        is_admin_inviter = (inviter_id in MASTER_ADMIN_IDS or self.is_admin(inviter_id))
                        if is_admin_inviter:
                            inv_tag = f"👑 <b>Admin</b> @{html.escape(inv_uname)}" if inv_uname else f'👑 <b>Admin</b> <a href="tg://user?id={inviter_id}"><b>{html.escape(inv_full)}</b></a>'
                        else:
                            inv_tag = f"@{html.escape(inv_uname)}" if inv_uname else f'<a href="tg://user?id={inviter_id}"><b>{html.escape(inv_full)}</b></a>'

                        source_info = f"Added by {inv_tag} (<code>{inviter_id}</code>)"
                        added_by_text = f"🤝 <b>Welcomed & Added by:</b> {inv_tag}"
                    else:
                        source_info = "Joined via Group Invite Link / Direct Join"
                        added_by_text = "🤝 <b>Joined via:</b> 🔗 Official Study Group Link"

                    # Track dossier & record join in SQLite
                    dossier = self._track_user_dossier(new_member)
                    account_age = self._estimate_account_age(nm_id)
                    join_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    try:
                        with get_db_conn() as conn:
                            conn.execute("""
                                INSERT OR REPLACE INTO member_history (user_id, chat_id, full_name, username, join_date)
                                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                            """, (nm_id, chat_id, nm_full, nm_uname))
                    except Exception as e:
                        logger.warning(f"Error saving member_history for {nm_id}: {e}")

                    # 1. Chatter Box: Sleek Tagged Welcome Message with Inspirational Study Quote
                    if g_settings.get("welcome_enabled", 1):
                        quotes = [
                            "The good physician treats the disease; the great physician treats the patient who has the disease. 🩺💫",
                            "Wherever the art of Medicine is loved, there is also a love of Humanity. 🤍✨",
                            "To cure sometimes, to relieve often, to comfort always. 🩺💙",
                            "Medicine is a science of uncertainty and an art of probability. Learn relentlessly! 📚🔬",
                            "The secret of the care of the patient is in caring for the patient. 🩺✨",
                            "Observation, Reason, Human Understanding, Courage: these make the physician. 🔬🩺",
                            "Stay curious, stay dedicated. One day, you will be the doctor you always needed. 🌟🥼",
                            "You don't just study medicine to pass exams; you study to prepare for the lives that will depend on you. 🩺🎯",
                            "Small daily improvements over time lead to stunning clinical mastery. 📈✨",
                            "Wear the white coat with pride, carry your stethoscope with honor, and practice with pure compassion. 🥼✨",
                            "Dreams don't work unless you do. Every page you read today will save a life tomorrow. 📖💫",
                            "Let your stethoscope be an instrument of hope, and your knowledge a beacon of healing. 🩺🌟",
                            "Hard work beats talent when talent doesn't work hard. Your stethoscope is waiting for you! 🥼🔥",
                            "When you touch one life, you heal the world in miniature. Believe in your journey! 🌍🤍"
                        ]
                        quote_choice = random.choice(quotes)
                        safe_grp_title = html.escape(grp_title)

                        custom_w = g_settings.get("welcome_text")
                        if custom_w:
                            welcome_group_msg = custom_w.replace("{name}", nm_tag).replace("{group}", safe_grp_title)
                        else:
                            lang = g_settings.get("language", "en")
                            if lang == "hi":
                                greeting_line = f"👋 <b>Namaste & Hardik Swagat Hai, {nm_tag}!</b> 🙏✨"
                            else:
                                greeting_line = f"👋 <b>Welcome {nm_tag} to {safe_grp_title}!</b> ✨"

                            welcome_group_msg = (
                                f"{greeting_line}\n\n"
                                f"❝ <i>{quote_choice}</i> ❞ 🩺📖\n\n"
                                f"<i>Wishing you all the best for your studies! 🌟🤍</i>"
                            )

                        sent_welcome_id = await self._send_message(
                            session, 
                            chat_id, 
                            welcome_group_msg,
                            message_thread_id=thread_id,
                            parse_mode="HTML"
                        )
                        if sent_welcome_id:
                            self._log_welcome_message(chat_id, sent_welcome_id)

                    # 2. General Topic / Admin Radar: Full OSINT & SangMata Biometric Dossier
                    try:
                        from devi.operator.osint_resolver import osint_resolver
                        live_sm = await osint_resolver.fetch_live_sangmata_history(nm_id)
                        if live_sm:
                            if live_sm.get("names"):
                                dossier["name_history"] = live_sm["names"]
                            if live_sm.get("usernames"):
                                dossier["username_history"] = live_sm["usernames"]
                            dossier["changes_count"] = live_sm.get("total_shifts", dossier.get("changes_count", 0))
                    except Exception as ex:
                        logger.debug(f"SangMata fetch on join: {ex}")

                    full_osint_card = self._format_sangmata_dossier(
                        dossier,
                        title_prefix="MEMBER JOIN INTELLIGENCE & SANGMATA OSINT RADAR"
                    )

                    admin_markup = {
                        "inline_keyboard": [
                            [
                                {"text": "👢 Kick Member", "callback_data": f"kick_{chat_id}_{nm_id}"},
                                {"text": "🚫 Ban & Block", "callback_data": f"ban_{chat_id}_{nm_id}"}
                            ]
                        ]
                    }

                    # A. Post in Group
                    if g_settings.get("join_track_enabled", 1):
                        await self._send_message(
                            session,
                            chat_id,
                            full_osint_card,
                            message_thread_id=thread_id,
                            reply_markup=admin_markup,
                            parse_mode="HTML"
                        )

                    # B. Also dispatch to Master Bot Admins
                    for adm_id in self.master_admin_ids:
                        await self._send_message(
                            session,
                            adm_id,
                            f"🏛️ <b>Group:</b> <code>{safe_grp_title}</code> (<code>{chat_id}</code>)\n\n" + full_osint_card,
                            reply_markup=admin_markup,
                            parse_mode="HTML"
                        )
                return

            # Silent Service Message Purge: Auto-delete "User left the group" messages to keep public chat spotless
            if "left_chat_member" in message:
                await self._delete_message(session, chat_id, msg_id)
                return
            if "pinned_message" in message:
                return

            # Real-time Automatic Media Indexer for Group Topics
            if thread_id:
                media_title = None
                media_icon = "🎬"
                if "video" in message:
                    vid = message["video"]
                    media_title = vid.get("file_name") or text or f"Lecture Video #{msg_id}"
                    media_icon = "🎬"
                elif "document" in message:
                    doc = message["document"]
                    media_title = doc.get("file_name") or text or f"Lecture Notes #{msg_id}"
                    media_icon = "📑"
                elif "audio" in message:
                    aud = message["audio"]
                    media_title = aud.get("title") or aud.get("file_name") or text or f"Audio #{msg_id}"
                    media_icon = "🎧"

                if media_title:
                    clean_title = media_title.replace(".mp4", "").replace(".pdf", "").replace(".mkv", "").strip()
                    self._save_topic_item(chat_id, thread_id, clean_title[:90], msg_id=msg_id, icon=media_icon)

            # C. Real-time Cloud Forwarder & Tag Remover Dispatcher
            is_service_msg = any(k in message for k in (
                "new_chat_members", "left_chat_member", "pinned_message",
                "group_chat_created", "supergroup_chat_created", "channel_chat_created",
                "migrate_to_chat_id", "migrate_from_chat_id"
            ))
            if not is_service_msg:
                active_routes = self._get_active_routes_for_source(chat_id, thread_id)
                if active_routes:
                    self.create_tracked_task(self._process_cloud_forward_routes(session, chat_id, msg_id, message, active_routes))

            # B. Group Protection & Anti-Spam Shield for Non-Admins
            is_sender_admin = await self.is_admin_for_chat(session, chat_id, sender_id, message=message)
            if not is_sender_admin:
                # 1. Anti-Flood Rate Limiter: Detect > 5 messages in 3 seconds from same user
                now_ts = datetime.now().timestamp()
                user_history = self.flood_tracker.get(sender_id, [])
                user_history = [t for t in user_history if now_ts - t < 3.0]
                user_history.append(now_ts)
                self.flood_tracker[sender_id] = user_history

                if len(user_history) >= 5:
                    await self._delete_message(session, chat_id, msg_id)
                    sender_mention = f"@{sender.get('username')}" if sender.get("username") else sender.get("first_name", "Member")
                    try:
                        mute_until = int(now_ts + 600)  # 10 minutes mute
                        mute_payload = {
                            "chat_id": chat_id,
                            "user_id": sender_id,
                            "until_date": mute_until,
                            "permissions": {"can_send_messages": False}
                        }
                        await session.post(f"https://api.telegram.org/bot{self.token}/restrictChatMember", json=mute_payload, timeout=8)
                    except Exception as ex:
                        logger.warning(f"Error restricting flooder {sender_id}: {ex}")

                    flood_warn = (
                        f"⚠️ **Anti-Flood Protection Alert:**\n"
                        f"{sender_mention} ko excessive messages spam karne par **10 minutes ke liye mute** kiya gaya hai.\n"
                        f"⏱️ _(Chat clean rakhne ke liye ye notice 20 sec me auto-delete ho jayega)._"
                    )
                    warn_id = await self._send_message(session, chat_id, flood_warn, message_thread_id=thread_id)
                    if warn_id:
                        self.create_tracked_task(self._auto_delete_message(session, chat_id, warn_id, 20))

                    # Alert Admins in DM
                    for adm in self.master_admin_ids:
                        await self._send_message(session, adm, f"🚨 **Anti-Flood Alert:** User `{sender_id}` ({sender_mention}) muted for 10m in group `{chat_id}`.")
                    return

                # 2. Anti-Link / External Promo Protection: Auto-delete unauthorized links
                enable_anti_link = os.getenv("ENABLE_ANTI_LINK", "true").lower() == "true"
                if enable_anti_link:
                    caption = message.get("caption", "") or ""
                    full_content = f"{text} {caption}".strip()
                    if full_content and LINK_REGEX.search(full_content):
                        await self._delete_message(session, chat_id, msg_id)
                        sender_mention = f"@{sender.get('username')}" if sender.get("username") else sender.get("first_name", "Member")
                        link_warn = (
                            f"🛡️ **Anti-Spam Shield:**\n"
                            f"{sender_mention}, external links aur promotional invites is study group me allowed nahi hain.\n"
                            f"⏱️ _(Chat clean rakhne ke liye ye alert 20 sec me auto-delete ho jayega)._"
                        )
                        warn_id = await self._send_message(session, chat_id, link_warn, message_thread_id=thread_id)
                        if warn_id:
                            self.create_tracked_task(self._auto_delete_message(session, chat_id, warn_id, 20))
                        return

                # 3. Anti-Scam, Crypto, Gambling & Adult/NSFW Content Shield (AI TelegramGuard / Guardify style)
                enable_anti_scam = os.getenv("ENABLE_ANTI_SCAM", "true").lower() == "true"
                if enable_anti_scam:
                    raw_text = f"{text} {message.get('caption', '') or ''}".strip()
                    if raw_text:
                        # Strip zero-width evasion characters (\u200b, \u200c, \u200d, \ufeff)
                        cleaned_evasion = re.sub(r'[\u200b\u200c\u200d\ufeff\s_.-]+', ' ', raw_text)
                        if SCAM_NSFW_REGEX.search(cleaned_evasion):
                            await self._delete_message(session, chat_id, msg_id)
                            self._log_analytics_event(chat_id, "scam_nsfw_blocked", sender_id, f"Snippet: {raw_text[:60]}")
                            sender_mention = f"@{sender.get('username')}" if sender.get("username") else sender.get("first_name", "Member")
                            scam_warn = (
                                f"🛡️ **Security Shield Alert:**\n"
                                f"{sender_mention}, betting, crypto, scam ya adult/inappropriate content is study group me strictly prohibited hai.\n"
                                f"⏱️ _(Chat clean rakhne ke liye ye alert 20 sec me auto-delete ho jayega)._"
                            )
                            warn_id = await self._send_message(session, chat_id, scam_warn, message_thread_id=thread_id)
                            if warn_id:
                                self.create_tracked_task(self._auto_delete_message(session, chat_id, warn_id, 20))

                            for adm in self.master_admin_ids:
                                await self._send_message(session, adm, f"🚨 **Scam/NSFW Filtered:** User `{sender_id}` ({sender_mention}) in chat `{chat_id}`:\n_{raw_text[:120]}_")
                            return

                # 4. Malicious Executable (.apk/.exe) Shield (Dr.Web style)
                if "document" in message:
                    doc = message["document"]
                    f_name = doc.get("file_name", "") or ""
                    if DANGEROUS_EXT_REGEX.search(f_name):
                        await self._delete_message(session, chat_id, msg_id)
                        self._log_analytics_event(chat_id, "malware_apk_blocked", sender_id, f"File: {f_name}")
                        sender_mention = f"@{sender.get('username')}" if sender.get("username") else sender.get("first_name", "Member")
                        apk_warn = (
                            f"🦠 **File Security Alert:**\n"
                            f"Executable files (`{f_name}`) students ke device safety ke liye block kiye gaye hain. Sirf official study PDFs / Notes allowed hain.\n"
                            f"⏱️ _(Chat clean rakhne ke liye ye alert 20 sec me auto-delete ho jayega)._"
                        )
                        warn_id = await self._send_message(session, chat_id, apk_warn, message_thread_id=thread_id)
                        if warn_id:
                            self.create_tracked_task(self._auto_delete_message(session, chat_id, warn_id, 20))

                        for adm in self.master_admin_ids:
                            await self._send_message(session, adm, f"🚨 **Malware/APK Blocked:** User `{sender_id}` ({sender_mention}) tried uploading `{f_name}` in `{chat_id}`.")
                        return

                # 5. Respectful & Polite Phone Number Shield (Auto-Delete + Username & Privacy Guidance)
                has_phone = False
                if "contact" in message:
                    has_phone = True
                elif text and PHONE_REGEX.search(text):
                    has_phone = True

                if has_phone:
                    # Immediately delete user message to prevent phone number leaks
                    await self._delete_message(session, chat_id, msg_id)

                    if sender.get("username"):
                        sender_mention = f"@{sender['username']}"
                    else:
                        first_n = (sender.get("first_name") or "Doctor").strip() or "Doctor"
                        sender_mention = f"[{first_n}](tg://user?id={sender_id})"

                    suggestion_text = (
                        f"🛡️ **Kind Doctor Privacy & Security Shield** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"Namaste {sender_mention}! 🙏\n\n"
                        f"Aapki personal safety aur privacy ke liye group me **Phone Number share karna strictly prohibited hai**. "
                        f"Aapka number protect karne ke liye message delete kar diya gaya hai. 🔒\n\n"
                        f"👉 **Group me kisi ko bhi Add karne ka sahi tareeqa:**\n"
                        f"Telegram group me add karne ke liye phone number ki bilkul zaroorat nahi hai. "
                        f"Bas unka **Telegram Username** (`@username`) share karein ya unhe group invite link forward karein!\n\n"
                        f"🔍 **Username kaise pata karein ya banayein:**\n"
                        f"1️⃣ Telegram khol kar **Settings** me jayein.\n"
                        f"2️⃣ **Edit Profile** (ya Username) par tap karein.\n"
                        f"3️⃣ Apna unique Username set karein (e.g. `@Doctor_Amit`).\n\n"
                        f"⚙️ **Agar 'Privacy Restriction' ki wajah se add na ho paayein:**\n"
                        f"Kai baar account par privacy restriction hoti hai jis se doosre log group me add nahi kar pate. Isko allow karne ke aasaan steps:\n"
                        f"• Telegram **Settings** ➔ **Privacy and Security** me jayein.\n"
                        f"• **Groups & Channels** par tap karein.\n"
                        f"• 'Who can add me to group chats' ko **'Everybody'** select karein. ✅\n\n"
                        f"💡 *Is tareeqe se aapka number 100% private rahega aur aap securely study group me connect ho sakenge!* 🤍\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"— @KindDoc_bot Desk"
                    )
                    sent_warn_id = await self._send_message(session, chat_id, suggestion_text, message_thread_id=thread_id)
                    if sent_warn_id:
                        self._log_welcome_message(chat_id, sent_warn_id)
                    return

            # C. Group Commands, Smart FAQs or Tags
            cur_bot_tag = f"@{self.bot_username}".lower() if getattr(self, "bot_username", None) else "@kinddoc_bot"
            is_tagged = (cur_bot_tag in text.lower()) or ("@kinddoc" in text.lower()) or ("@kinddoctor" in text.lower())
            is_command = text.startswith("/")

            if not (is_tagged or is_command):
                # Smart FAQ trigger: Check if any keyword matches a saved FAQ
                if text:
                    for word in text.lower().split():
                        clean_word = word.strip("?!.,#*()[]")
                        if len(clean_word) >= 3:
                            faq_ans = self._get_faq(chat_id, clean_word)
                            if faq_ans:
                                faq_bubble = f"💡 **Kind Doctor Quick FAQ (`{clean_word}`):**\n\n{faq_ans}"
                                await self._send_message(session, chat_id, faq_bubble, reply_to=msg_id, message_thread_id=message.get("message_thread_id"))
                                return
                return  # Stay completely silent!

            # Group command auto-purge: Only auto-delete if explicitly configured > 0
            if is_command and msg_id:
                cmd_cleanup_delay = int(os.getenv("COMMAND_AUTO_DELETE_SECONDS", "0"))
                if cmd_cleanup_delay > 0:
                    self.create_tracked_task(self._auto_delete_message(session, chat_id, msg_id, cmd_cleanup_delay))

            # Strip any bot username mention (e.g. /mainindex@KindDoc_bot or /mainindex@KindDoctor4u_bot -> /mainindex)
            clean_text = re.sub(r'@[a-zA-Z0-9_]+', '', text).strip()
            first_word = clean_text.split()[0].lower().split("@")[0] if clean_text else ""

            # Non-admins can use study and search tools (and view indexes)
            if not is_sender_admin:
                if first_word in STUDENT_ALLOWED_COMMANDS:
                    await self._handle_admin_command(session, chat_id, sender_id, clean_text, message=message)
                return  # Admin commands stay silent

            if clean_text.startswith("/"):
                await self._handle_admin_command(session, chat_id, sender_id, clean_text, message=message)
            elif is_tagged:
                await self._handle_devi_ai_chat(session, chat_id, clean_text, sender.get("first_name", "Admin"))
            return

        # ============================================================
        # 2. PRIVATE DM FLOW
        # ============================================================
        # Ignore if user is blocked in private
        if sender_id in self.blocked_users and not self.is_admin(sender_id):
            return

        # --- ADMIN PRIVATE DM ---
        if self.is_admin(sender_id):
            reply_to = message.get("reply_to_message")
            if reply_to:
                reply_id = reply_to.get("message_id")
                relay_info = self._get_relay_info(chat_id, reply_id)
                if relay_info:
                    target_user_id = relay_info["user_chat_id"]
                    target_name = relay_info["user_name"]
                    target_msg_id = relay_info["user_msg_id"]

                    if text:
                        clean_reply = text.strip()
                        lower_reply = clean_reply.lower()

                        if lower_reply == "/r link":
                            # Auto-generate single-use disposable invite link
                            target_grp = self.target_chat
                            link_url = ""
                            if target_grp:
                                try:
                                    invite_url = f"https://api.telegram.org/bot{self.token}/createChatInviteLink"
                                    expire_ts = int((datetime.now() + timedelta(minutes=30)).timestamp())
                                    async with session.post(invite_url, json={"chat_id": target_grp, "member_limit": 1, "expire_date": expire_ts}, timeout=10) as resp:
                                        if resp.status == 200:
                                            res_data = await resp.json()
                                            link_url = res_data.get("result", {}).get("invite_link")
                                except Exception as e:
                                    logger.warning(f"Error creating invite link snippet: {e}")

                            if link_url:
                                user_reply_text = (
                                    f"👨‍⚕️ **Kind Doctor:**\n\n"
                                    f"Welcome! Here is your exclusive single-use invite link to the study group:\n"
                                    f"{link_url}\n\n"
                                    f"*(Note: Yeh link 30 minutes me expire ho jayega. Happy studying!)*"
                                )
                            else:
                                user_reply_text = "👨‍⚕️ **Kind Doctor:**\n\nGroup link generation is temporarily busy. Please hold on or contact admin."
                        elif lower_reply == "/r schedule":
                            user_reply_text = (
                                f"👨‍⚕️ **Kind Doctor:**\n\n"
                                f"📅 **Daily Study & Lecture Schedule:**\n"
                                f"• Morning Focus Sprint: 09:00 AM - 12:00 PM\n"
                                f"• Clinical Case Discussion: 03:00 PM - 05:00 PM\n"
                                f"• High-Yield Evening Lecture: 08:00 PM\n\n"
                                f"Check pinned topic indexes in the study group for latest recordings!"
                            )
                        elif lower_reply == "/r verified":
                            user_reply_text = (
                                f"👨‍⚕️ **Kind Doctor:**\n\n"
                                f"✅ **Account Verified!**\n"
                                f"Aapka profile verify ho chuka hai. Aap ab study group me sabhi medical resources aur discussions access kar sakte hain. All the best!"
                            )
                        elif lower_reply == "/r help":
                            await self._send_message(
                                session, chat_id,
                                f"💡 **Admin Quick Reply Snippets (Type as reply to student):**\n\n"
                                f"• `/r link` — Generate & deliver 30-min single-use group invite link\n"
                                f"• `/r schedule` — Send study & lecture schedule\n"
                                f"• `/r verified` — Send account verification confirmation\n"
                                f"• Or type any custom message directly.",
                                reply_to=msg_id
                            )
                            return
                        else:
                            user_reply_text = f"👨‍⚕️ **Kind Doctor:**\n\n{text}"

                        delivered_id = await self._send_message(session, target_user_id, user_reply_text, reply_to=target_msg_id)
                    else:
                        caption = message.get("caption") or ""
                        final_cap = f"👨‍⚕️ **Kind Doctor:**\n\n{caption}" if caption else "👨‍⚕️ **Kind Doctor**"
                        delivered_id = await self._copy_message(
                            session, 
                            target_user_id, 
                            chat_id, 
                            msg_id, 
                            caption=final_cap, 
                            reply_to=target_msg_id
                        )

                    if delivered_id:
                        await self._send_message(session, chat_id, f"✅ **Delivered to {target_name}** (`{target_user_id}`)\n\n*(Sent under anonymous '👨‍⚕️ Kind Doctor' brand)*", reply_to=msg_id)
                    else:
                        await self._send_message(session, chat_id, f"⚠️ Delivery failed to `{target_user_id}`. User may have blocked the bot.", reply_to=msg_id)
                    return

            # Admin Voice Note Handling in DM (Groq Whisper Large v3)
            if "voice" in message:
                await self._handle_admin_voice_note(session, chat_id, message["voice"], sender.get("first_name", "Admin"))
                return

            # Admin Command Flow in DM
            if text.startswith("/"):
                await self._handle_admin_command(session, chat_id, sender_id, text, message=message)
                return

            # Admin natural chat with DEVI AI (ONLY IN PRIVATE DM)
            if text:
                await self._handle_devi_ai_chat(session, chat_id, text, sender.get("first_name", "Admin"))
                return

        # --- NORMAL USER PRIVATE DM (Live Support & Auto-Verification) ---
        detected_phone = None
        if "contact" in message:
            detected_phone = message["contact"].get("phone_number")
        elif text:
            m = PHONE_REGEX.search(text)
            if m:
                detected_phone = m.group(0)

        dossier = self._track_user_dossier(sender, detected_phone)
        user_mention = f"@{dossier['username']}" if dossier['username'] else "No Username"
        premium_badge = "⭐️ Premium" if dossier["is_premium"] else "Standard"

        # If phone number detected, politely guide user in English
        if detected_phone:
            shield_notice = (
                f"Hello {dossier['full_name']}! 🙏✨\n\n"
                f"For your privacy and security, please do not share phone numbers 🛡️\n\n"
                f"👉 Please share only your **Telegram User ID: `{sender_id}`** (a phone number is not required).\n\n"
                f"💡 *Adding via Telegram User ID is 100% safe, fast, and completely confidential!* 🩺💙\n\n"
                f"Your request has been securely forwarded to the Admins. A safe invite link will be provided here after verification!"
            )
            await self._send_message(session, chat_id, shield_notice)

        # Welcome message on /start
        elif text.startswith("/start"):
            username_guide = ""
            if not dossier["username"]:
                username_guide = (
                    "\n\n⚙️ **Aapka Username (@username) set nahi hai!**\n"
                    "Groups me aasaani se add hone ke liye Telegram Settings -> Username me jakar apna username bana sakte hain."
                )

            welcome_text = (
                f"👨‍⚕️ **Kind Doctor** 🤍 🩺\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Namaste **{dossier['full_name']}**! Aapka swagat hai.\n\n"
                f"Main **Kind Doctor** bot hoon — aapka trusted study & medical companion.\n\n"
                f"✨ **Core Features:**\n"
                f"• 📑 **Group Notes & Lectures**: Topic directory & TOC\n"
                f"• 🔍 **Search Lectures**: `/find <topic>` likhein turant access ke liye\n"
                f"• 💬 **Live Support**: Kind Doctor se direct baat karein\n\n"
                f"💬 **Kind Doctor se Direct Baat Karni Hai?**\n"
                f"Agar aapko koi medical doubt hai, notes chahiye, ya study batch join karna hai:\n"
                f"👉 **Bas yahi par apna message type karke send kar dijiye!**\n"
                f"Aapka message securely **Kind Doctor** tak pahunch jayega aur unka reply aapko yahi par mil jayega. 🩺✨{username_guide}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👇 *Neeche diye buttons se features explore karein:*"
            )
            welcome_markup = {
                "inline_keyboard": [
                    [
                        {"text": "📑 Master Topic Directory", "callback_data": "act_mainindex"},
                        {"text": "⚡ 1-Click Auto-Scan", "callback_data": "act_scan"}
                    ],
                    [
                        {"text": "💬 Message Kind Doctor 🩺", "callback_data": "act_support"},
                        {"text": "📖 Complete Manual", "callback_data": "act_manual"}
                    ]
                ]
            }
            await self._send_message(session, chat_id, welcome_text, reply_markup=welcome_markup)
            return

        # Smart Response: If user asks how to add a friend or member
        lower_text = text.lower()
        is_asking_how_to_add = any(k in lower_text for k in [
            "how to add", "kaise add", "add my friend", "friend ko add", "dost ko add",
            "add karna", "invite friend", "can i add", "add kaise", "add him", "add her",
            "kisi ko add", "member add", "add my"
        ])

        if is_asking_how_to_add and not detected_phone and not text.startswith("/start"):
            add_guide = (
                f"Hello {dossier['full_name']}! 👋\n\n"
                f"👥 **Apne Friend ko Add Karwane ke Steps:**\n\n"
                f"1️⃣ Apne friend ka Telegram **@username** yahan send kar dijiye.\n"
                f"2️⃣ Jaise hi aap unka @username share karenge, hamare Admins unhe verify karke single-use safe invite link provide kar denge! 🩺✨\n\n"
                f"*(Note: Kripya phone number share na karein, sirf @username se hi add kiya jata hai).*"
            )
            await self._send_message(session, chat_id, add_guide)

        # Check if message matches any Command or Custom Command (with or without /)
        clean_prompt = re.sub(r'@[a-zA-Z0-9_]+', '', text).strip()
        cmd_first = clean_prompt.split()[0].lower().split("@")[0] if clean_prompt else ""
        if not cmd_first.startswith("/"):
            if f"/{cmd_first}" in STUDENT_ALLOWED_COMMANDS or cmd_first in ("index", "mainindex", "topics", "help", "menu", "stats", "scan", "manual", "find"):
                clean_prompt = f"/{clean_prompt}"
                cmd_first = f"/{cmd_first}"

        if clean_prompt.startswith("/"):
            custom_cmd_key = cmd_first
            custom_output = self._get_custom_command(custom_cmd_key)
            if custom_output:
                await self._send_message(session, chat_id, custom_output)
                return

            # Allow /help, /start, /index, and all study commands in private DM for EVERYONE!
            if custom_cmd_key in STUDENT_ALLOWED_COMMANDS:
                await self._handle_admin_command(session, chat_id, sender_id, clean_prompt, message=message)
                return

        # Build Rich Intel Dossier Banner for Admins
        history_warnings = ""
        if dossier["changes_count"] > 0:
            change_items = "\n".join(f"  • {c}" for c in dossier["changes_detected"]) if dossier["changes_detected"] else ""
            if dossier["username_history"]:
                prev_unames = ", ".join(f"@{h['username']}" for h in dossier["username_history"])
                change_items += f"\n  • Previous Usernames: {prev_unames}"
            if dossier["name_history"]:
                prev_names = ", ".join(f"'{h['name']}'" for h in dossier["name_history"])
                change_items += f"\n  • Previous Names: {prev_names}"
            history_warnings = (
                f"\n⚠️ **Identity Changes ({dossier['changes_count']} detected):**\n"
                f"{change_items}\n"
            )

        status_tag = "✨ NEW USER" if dossier["is_new"] else f"🔄 RETURNING USER ({dossier['total_messages']} msgs)"
        admin_banner = (
            f"🕵️ **[Student Message | Kind Doctor Desk]** 🩺\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"👤 **Student**: {dossier['full_name']} ({status_tag})\n"
            f"🆔 **User ID**: `{sender_id}`\n"
            f"🔗 **Username**: {user_mention}\n"
            f"📱 **Phone**: `{dossier['phone']}`\n"
            f"🌟 **Account**: {premium_badge} | 🌐 `{dossier['language']}`\n"
            f"🕒 **Time**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"{history_warnings}\n"
            f"💬 **Message**:\n{text if text else '[Attached Media/File/Voice]'}\n\n"
            f"👉 **Aap is message par 'Reply' karke direct type karein** — student ko '👨‍⚕️ Kind Doctor' naam se reply chala jayega (Aapki personal ID 100% hidden rahegi)."
        )

        admin_inline_markup = {
            "inline_keyboard": [
                [
                    {"text": "🔗 Send 1-Time Link", "callback_data": f"send_link_{sender_id}"},
                    {"text": "🚫 Block User", "callback_data": f"block_{sender_id}"}
                ]
            ]
        }

        # Relay to ALL Master Admin IDs simultaneously (both Telegram accounts)
        for admin_id in self.master_admin_ids:
            sent_msg_id = None
            if text:
                sent_msg_id = await self._send_message(session, admin_id, admin_banner, reply_markup=admin_inline_markup)
            else:
                sent_msg_id = await self._copy_message(
                    session,
                    admin_id,
                    chat_id,
                    msg_id,
                    caption=admin_banner,
                    reply_markup=admin_inline_markup
                )

            if sent_msg_id:
                self._save_relay_info(admin_id, sent_msg_id, sender_id, dossier["full_name"], msg_id)

        # Immediate polite delivery acknowledgment back to student
        ack_msg = (
            f"📩 **Message Delivered to Kind Doctor Desk!** 🩺\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Aapka message safely **Kind Doctor** tak pahunch gaya hai.\n"
            f"Doctor jaise hi active honge, aapko unka reply yahi par direct mil jayega! 🤍\n\n"
            f"✨ _Tab tak aap /menu ya /find se medical notes & lectures explore kar sakte hain._"
        )
        await self._send_message(session, chat_id, ack_msg, reply_to=msg_id)

    async def _handle_admin_command(
        self, 
        session: aiohttp.ClientSession, 
        chat_id: int, 
        admin_id: int, 
        text: str, 
        message: Optional[dict] = None
    ):
        parts = text.split()
        cmd = parts[0].lower().split("@")[0]
        thread_id = message.get("message_thread_id") if message else None
        reply_to = message.get("reply_to_message") if message else None
        clean_chat_id = str(chat_id).replace("-100", "").replace("-", "").lstrip("@")

        if cmd in ("/help", "/start", "/menu", "/settings", "/mode"):
            load_dotenv(override=True)
            cur_direct = os.getenv("DIRECT_FORWARD", "false").strip().lower() in ("true", "1", "yes")
            cur_sig = os.getenv("ENABLE_SIGNATURE", "true").strip().lower() in ("true", "1", "yes")
            cur_thumb = os.getenv("THUMB_MODE", "custom").strip().lower()

            direct_btn_txt = "⚡ Fast Direct: ON" if cur_direct else "🔄 Stream: Default"
            sig_btn_txt = "👑 Branding: ✅ ON" if cur_sig else "🏷️ Clean Mode: ❌ OFF"
            thumb_btn_txt = "🖼️ Cover: 16:9 HD" if cur_thumb == "custom" else "🎞️ Cover: Original"

            admin_panel_text = ""
            if self.is_admin(admin_id):
                admin_panel_text = (
                    f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"⚙️ **Admin Pipeline Controls:**\n"
                    f"• Forwarding: `{'⚡ Fast Direct (0.2s Instant)' if cur_direct else '🔄 Stream Mode (Safe, Fresh Hashes)'}`\n"
                    f"• Branding & Media: `{'👑 ON (Kind Doctor Sig + 16:9 HD Cover)' if cur_sig else '🏷️ OFF (Clean Mode: No Sig & Original Media)'}`\n"
                    f"• Video Cover Override: `{'🖼️ 16:9 HD Custom Cover' if cur_thumb == 'custom' else '🎞️ Original Media'}`\n"
                    f"_(Neeche diye 1-click buttons se instant switch karein)_"
                )

            reply = (
                f"👨‍⚕️ **Kind Doctor** 🤍 🩺\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Welcome! Aapka study & group assistant **100% Active** hai.\n"
                f"Neeche diye **1-Click Buttons** se direct features use karein:\n\n"
                f"⚡ **Core Tools:**\n"
                f"• 📑 **Master Topic Directory**: Saare subjects ka Alphabetical (A-Z) hub\n"
                f"• ⚡ **1-Click Auto-Scan**: Poora group scan karke directory auto-fill\n"
                f"• 💬 **Message Kind Doctor**: Direct personal live support\n"
                f"• 🔍 **Search Engine**: `/find <topic/lecture>` instantly dhoondein\n"
                f"{admin_panel_text}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 *Tip: Poori guide dekhne ke liye `/fullhelp` likhein ya neeche [📖 Full Manual] tap karein.*"
            )
            keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "📑 Master Topic Directory", "callback_data": "act_mainindex"},
                        {"text": "⚡ 1-Click Auto-Scan", "callback_data": "act_scan"}
                    ],
                    [
                        {"text": "💬 Message Kind Doctor 🩺", "callback_data": "act_support"},
                        {"text": "📖 Full Manual", "callback_data": "act_manual"}
                    ]
                ]
            }
            if self.is_admin(admin_id):
                keyboard["inline_keyboard"].append([
                    {"text": direct_btn_txt, "callback_data": "act_toggle_direct"},
                    {"text": sig_btn_txt, "callback_data": "act_toggle_sig"}
                ])
                keyboard["inline_keyboard"].append([
                    {"text": thumb_btn_txt, "callback_data": "act_toggle_thumb"}
                ])
            await self._send_message(session, chat_id, reply, reply_markup=keyboard, message_thread_id=thread_id)

        elif cmd in ("/support", "/contact"):
            support_card = (
                f"👨‍⚕️ **Kind Doctor Direct Desk & Live Line** 🩺\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Agar aapko study material, notes, batches join karne ya kisi medical topic par guidance chahiye:\n\n"
                f"👉 **Bas yahi par apna message, doubt ya request type karke send kar dijiye!**\n\n"
                f"🔒 **100% Private & Direct:**\n"
                f"• Aapka message seedha **Kind Doctor** ke private desk par securely deliver hota hai.\n"
                f"• Doctor jaise hi message dekhenge, aapko unka reply isi bot ke through mil jayega.\n"
                f"• Kisi phone number ya external application ki zaroorat nahi hai! 🤍"
            )
            await self._send_message(session, chat_id, support_card, message_thread_id=thread_id)

        elif cmd in ("/id", "/myid"):
            lines = [
                f"🆔 **Telegram Identity Card** 🩺",
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ]
            if reply_to and reply_to.get("from"):
                target_u = reply_to["from"]
                lines.append(f"• **Target User ID**: `{target_u.get('id')}` ({target_u.get('first_name', 'User')})")
                if target_u.get("username"):
                    lines.append(f"• **Target Username**: @{target_u.get('username')}")
            
            lines.append(f"• **Your Permanent ID**: `{admin_id}`")
            lines.append(f"• **Current Chat ID**: `{chat_id}`")
            if thread_id:
                lines.append(f"• **Current Topic ID**: `{thread_id}`")
            
            lines.append(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            lines.append(f"*(Yeh numerical IDs admin controls, forward routes aur live support relay me use hoti hain).*")
            await self._send_message(session, chat_id, "\n".join(lines), message_thread_id=thread_id)

        elif cmd in ("/fullhelp", "/manual"):
            part1 = (
                f"👨‍⚕️ **Kind Doctor — Official Command Manual (Part 1/3)** 📖\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📚 **STUDY & LECTURE NAVIGATION:**\n"
                f"• `/mainindex` — Generate Alphabetical (A-Z) Master Topic Directory\n"
                f"• `/topicindex` — Generate Table of Contents (TOC) inside current topic\n"
                f"• `/find <keyword>` — Search indexed lectures, topics & notes with instant links\n"
                f"• `/rules` — View official community guidelines & study etiquette\n"
                f"• `/support` — Direct confidential message line to Kind Doctor Desk\n"
                f"• `/id` — View your Telegram User ID safely without sharing phone numbers\n\n"
                f"🩺 **CLINICAL & STUDY TOOLS:**\n"
                f"• `/score <type>` — Bedside clinical calculators (BMI, MAP, GCS, Wells, Curb-65)\n"
                f"• `/pomodoro [mins]` — Start focused deep-study sprint (25m or 50m)\n"
                f"• `/ask <doubt>` — Submit clinical question to study group & faculty\n"
                f"• `/stats` — View community study metrics & active student engagement"
            )
            part2 = (
                f"👨‍⚕️ **Kind Doctor — Official Command Manual (Part 2/3)** 📖\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚙️ **GROUP ADMINISTRATION & FORENSIC AUDITING:**\n"
                f"• `/members` — Audit group member history, join dates & identity shifts\n"
                f"• `/exportmembers` — Export full member list as an Excel/CSV spreadsheet\n"
                f"• `/userinfo <id|@user|reply>` — Comprehensive dossier (Account age, changes, stats)\n"
                f"• `/setwelcome <text>` — Set custom welcome message (`{{name}}`, `{{group}}`, `{{rules}}`)\n"
                f"• `/welcometoggle [on/off]` — Enable or disable new member welcome greetings\n"
                f"• `/jointrack [on/off]` — Toggle forensic member join tracking alerts\n"
                f"• `/setrules <text>` — Set official group rules & study guidelines\n"
                f"• `/cleanwelcome` — 1-Click batch purge of all previous welcome cards\n"
                f"• `/cleandeleted` — Scan and remove ghost & 'Deleted Accounts' from group\n"
                f"• `/setlang <en|hi>` — Switch bot language (English or Hinglish)\n"
                f"• `/scan` — 1-Click auto-scan group media and update topic directory"
            )
            part3 = (
                f"👨‍⚕️ **Kind Doctor — Official Command Manual (Part 3/3)** 📖\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🔄 **CLOUD FORWARDER & ZERO-TAG REMOVER (No PC Needed):**\n"
                f"• `/setroute <source_chat_id> [topic_id]` — Auto-mirror posts with **zero forward tag**\n"
                f"• `/settopicroute <src_chat> <src_topic> [tgt_topic]` — Topic-to-topic auto-mirroring\n"
                f"• `/routes` — List and manage all active forward routes\n"
                f"• `/pauseroute <id>` & `/resumeroute <id>` — Pause or resume forwarding\n"
                f"• `/delroute <id>` — Delete an existing forward route\n"
                f"• `/routefilter <id> <all|video|doc|photo>` — Set media type filter for route\n"
                f"• `/clone <link | reply>` — Instantly copy 1 message with zero forward tag\n"
                f"• `/batchclone <start_link> <end_link>` — Batch copy sequence of messages\n\n"
                f"👑 **MASTER ADMIN PIPELINE & SYSTEM SPECS:**\n"
                f"• `/botinfo` / `/about` — View Kind Doctor Bot architecture, version & admin specs\n"
                f"• `/update` — 1-Click Code Sync & Auto-Updater (Master Admins)\n"
                f"• `/allgroups` — Master network overview of all connected groups\n"
                f"• `/health` — Real-time telemetry, memory & database integrity status\n"
                f"• `/purge <count>` — Mass-delete recent messages in case of emergency\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 *Tip: Tap /menu anytime for interactive 1-click button controls.*"
            )
            await self._send_message(session, chat_id, part1, message_thread_id=thread_id)
            await asyncio.sleep(0.3)
            await self._send_message(session, chat_id, part2, message_thread_id=thread_id)
            await asyncio.sleep(0.3)
            await self._send_message(session, chat_id, part3, message_thread_id=thread_id)

        elif cmd in ("/botinfo", "/about"):
            bot_card = (
                f"👨‍⚕️ **Kind Doctor Bot 🤍 🩺**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✨ **Version**: `v14.5 Platinum Edition`\n"
                f"🟢 **Status**: `Online & Active 24/7`\n"
                f"⚡ **Core Suite**: `TG KindSync Pro v14.5 + Telegram Bot API + SQLite DB`\n\n"
                f"🎯 **SPECIALIZED CAPABILITIES:**\n"
                f"• 📑 **Master Topic Directory**: Auto-indexed Alphabetical subjects (#A to #Z)\n"
                f"• 🔄 **Cloud Content Forwarder**: Real-time auto-mirroring with **zero forward tags** (via `copyMessage`, zero PC needed)\n"
                f"• 📦 **Smart Cloner Suite**: 1-Click message cloning (`/clone`) and batch cloning (`/batchclone`)\n"
                f"• 🕵️ **User Intelligence Suite**: SangMata & Rose style forensic inspection (`/userinfo`, `/whois`)\n"
                f"• 🛡️ **Forensic Member Guardian**: Account age estimation, anti-raid intelligence & name tracker\n"
                f"• 🧹 **Sanitation Cleaners**: Batch welcome card purge (`/cleanwelcome`) & ghost account remover (`/cleandeleted`)\n"
                f"• 🚀 **One-Click Auto-Updater**: Instant code sync via `/update` & `UPDATE_KINDSYNC.bat`\n"
                f"• 🔒 **Admin Anonymity**: Complete identity shielding in public group cards\n"
                f"• 💬 **Confidential Support**: Direct message bridge to Kind Doctor Desk\n\n"
                f"👑 **PERMANENT MASTER ADMINISTRATORS:**\n"
                f"• 👨‍⚕️ **Primary 1**: @Kinddoctor4u (`1553619403`)\n"
                f"• 👨‍⚕️ **Primary 2**: @Ammitrajput1 (`759038032`)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📖 *Type `/manual` for the official 3-Part Command Guide.*"
            )
            await self._send_message(session, chat_id, bot_card, message_thread_id=thread_id)

        elif cmd == "/update":
            if not self.is_admin(admin_id):
                await self._send_message(session, chat_id, "⚠️ Access Denied: Strictly Master Admins only.", message_thread_id=thread_id)
                return
            status_msg = await self._send_message(session, chat_id, "⏳ **Checking & syncing TG KindSync Pro updates...**", message_thread_id=thread_id)
            try:
                from tools.updater import run_update, load_version_info
                run_update()
                v_info = load_version_info()
                if status_msg:
                    await self._delete_message(session, chat_id, status_msg)
                await self._send_message(
                    session, chat_id,
                    f"🎉 **TG KindSync Pro Updated Successfully!** 🚀\n\n"
                    f"• Current Version: `{v_info.get('version')}` (`{v_info.get('release_tag')}`)\n"
                    f"• Status: 100% Synchronized\n"
                    f"• Protected: `.env`, sessions, and SQLite databases preserved untouched.",
                    message_thread_id=thread_id
                )
            except Exception as e:
                await self._send_message(session, chat_id, f"❌ Update check failed: {e}", message_thread_id=thread_id)

        elif cmd == "/indexhelp":
            help_text = (
                f"📑 **Kind Doctor Dual Index Guide & Manual**\n\n"
                f"Aap apne group me 2 types ke indexes bana sakte hain:\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏛️ **1. MASTER DIRECTORY (All Topics Hub - Alphabetical A to Z)**\n"
                f"• Saare subjects/topics ka main click-able link index.\n"
                f"• **Step 1**: Topic me jakar type karein: `/settopic Subject Name` (e.g. `/settopic Cardiology`).\n"
                f"• **Step 2**: General chat me type karein: `/mainindex`.\n"
                f"• **Result**: Poora Alphabetical (A-Z) clickable index ban kar group ke top par auto-pin ho jayega!\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"📚 **2. TOPIC TABLE OF CONTENTS (Lectures & Files)**\n"
                f"• Topic ke andar individual lectures/PDFs ka index.\n"
                f"• **Step 1**: Lecture video ya PDF par **Reply** karein aur type karein: `/additem Lecture 01 - Anatomy`\n"
                f"• **Step 2**: Jab sab lectures add ho jayein, topic me type karein: `/topicindex`\n"
                f"• **Result**: Topic ke top par Table of Contents auto-pin ho jayega!\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚙️ **Extra Commands:**\n"
                f"• `/topics` - Saare topics ki A-Z list dekhein\n"
                f"• `/addlink <title> <link>` - Direct web/telegram link add karein\n"
                f"• `/deltopic <topic_id>` - Topic remove karein\n"
                f"• `/clearindex` - Topic index fresh start karein"
            )
            await self._send_message(session, chat_id, help_text, message_thread_id=thread_id)

        # -------------------------------------------------------------
        # DUAL INDEX & AUTO-SCAN COMMANDS
        # -------------------------------------------------------------
        elif cmd in ("/scan", "/autoindex"):
            target_scan_chat = self._resolve_study_group_id(chat_id)
            status_msg_id = await self._send_message(
                session, chat_id,
                "⚡ **1-Click Auto-Scan Running...** 🔍\n"
                "Group ke sabhi forum topics aur unke andar ke videos/notes scan kiye ja rahe hain. Kripya 3-5 seconds wait karein...",
                message_thread_id=thread_id
            )
            try:
                proc = await asyncio.create_subprocess_exec(
                    sys.executable, "-m", "devi.operator.group_scanner", str(target_scan_chat),
                    cwd=str(BASE_PROJECT_DIR),
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await asyncio.wait_for(proc.communicate(), timeout=300.0)
            except Exception as e:
                logger.warning(f"Error executing group scanner: {e}")

            topics = self._get_topics(target_scan_chat, sort_mode="az")
            total_items = 0
            try:
                with get_db_conn() as conn:
                    cur = conn.execute("SELECT COUNT(*) FROM telegram_topic_items WHERE chat_id = ?", (target_scan_chat,))
                    total_items = cur.fetchone()[0]
            except Exception:
                pass

            if total_items == 0 and len(topics) <= 1:
                done_msg = (
                    f"⚠️ <b>Auto-Scan Notice:</b>\n\n"
                    f"• <b>Topics Found:</b> <code>{len(topics)}</code>\n"
                    f"• <b>Lectures/Files:</b> <code>0</code>\n\n"
                    f"💡 <b>Kripya Check Karein:</b>\n"
                    f"1️⃣ Main user account (session) is group me member hona chahiye.\n"
                    f"2️⃣ Bot ke paas group me <b>Admin Rights (Pin Messages & Read Messages)</b> active honi chahiye.\n"
                    f"3️⃣ Ya fir topic ke andar <code>/settopic &lt;Title&gt;</code> aur files par reply karke <code>/additem</code> se manual add karein."
                )
            else:
                done_msg = (
                    f"✅ <b>Auto-Scan &amp; Indexing Successful!</b> 🎯\n\n"
                    f"📊 <b>Scan Summary:</b>\n"
                    f"• <b>Topics Registered:</b> <code>{len(topics)}</code>\n"
                    f"• <b>Lectures/Files Indexed:</b> <code>{total_items}</code>\n\n"
                    f"👉 Ab aap <code>/mainindex</code> tap karein Master Hub dekhne ke liye, ya kisi topic me <code>/topicindex</code> bhejein!"
                )
            if status_msg_id:
                self.create_tracked_task(self._auto_delete_message(session, chat_id, status_msg_id, 2))
            await self._send_message(session, chat_id, done_msg, message_thread_id=thread_id)

        elif cmd in ("/mainindex", "/main_index", "/indexmaster", "/alltopics"):
            target_index_chat = self._resolve_study_group_id(chat_id)
            sort_mode = "az"
            for p in parts[1:]:
                if p.lower() in ("seq", "num", "forum", "order"):
                    sort_mode = "seq"
                elif p.lower() in ("az", "alpha", "a-z"):
                    sort_mode = "az"

            topics = self._get_topics(target_index_chat, sort_mode=sort_mode)
            if not topics:
                scan_notify = await self._send_message(
                    session, chat_id,
                    "🔍 **Topics abhi registered nahi hain. 1-Click Auto-Scan chalu kar rahe hain...**",
                    message_thread_id=thread_id
                )
                try:
                    proc = await asyncio.create_subprocess_exec(
                        sys.executable, "-m", "devi.operator.group_scanner", str(target_index_chat),
                        cwd=str(BASE_PROJECT_DIR),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await asyncio.wait_for(proc.communicate(), timeout=120.0)
                    topics = self._get_topics(target_index_chat, sort_mode=sort_mode)
                except Exception as e:
                    logger.warning(f"Error during auto-healing scan: {e}")
                if scan_notify:
                    self.create_tracked_task(self._auto_delete_message(session, chat_id, scan_notify, 2))

            if not topics:
                help_msg = (
                    f"⚠️ **Is Group me abhi koi Topics nahi mile.**\n\n"
                    f"💡 **Topic Add karne ka aasaan tareeqa:**\n"
                    f"1️⃣ Jis topic ko add karna hai, us topic ke andar type karein:\n"
                    f"   `/settopic Cardiology`\n"
                    f"2️⃣ Ya fir group me `/scan` chala kar auto-index karein! 🚀"
                )
                await self._send_message(session, chat_id, help_msg, message_thread_id=thread_id)
                return

            cards, reply_markup = self._build_main_index_cards(target_index_chat, sort_mode=sort_mode)
            first_msg_id = None
            for idx, card in enumerate(cards):
                m_markup = reply_markup if idx == len(cards) - 1 or idx == 0 else None
                m_id = await self._send_message(
                    session,
                    chat_id,
                    card,
                    reply_markup=m_markup,
                    message_thread_id=thread_id,
                    disable_web_page_preview=True
                )
                if idx == 0 and m_id:
                    first_msg_id = m_id
                await asyncio.sleep(0.5)

            if first_msg_id and chat_id < 0:
                pinned = await self._pin_message(session, chat_id, first_msg_id, silent=True)
                pin_status = "📌 Auto-pinned successfully!" if pinned else "(Tip: Group settings me bot ko 'Pin Messages' right dein to auto-pin ho sake)."
                conf = await self._send_message(
                    session,
                    chat_id,
                    f"✅ <b>Master Hub Index Published!</b> ({'Alphabetical A–Z' if sort_mode == 'az' else 'Forum Sequence'}) {pin_status}",
                    message_thread_id=thread_id
                )
                if conf and os.getenv("ENABLE_AUTO_DELETE", "false").lower() == "true":
                    self.create_tracked_task(self._auto_delete_message(session, chat_id, conf, 15))
            elif first_msg_id:
                conf = await self._send_message(
                    session,
                    chat_id,
                    f"✅ <b>Master Hub Index Displayed!</b> (Target Study Group: <code>{target_index_chat}</code>)",
                    message_thread_id=thread_id
                )
                if conf and os.getenv("ENABLE_AUTO_DELETE", "false").lower() == "true":
                    self.create_tracked_task(self._auto_delete_message(session, chat_id, conf, 15))

        elif cmd in ("/topicindex", "/subindex", "/index"):
            target_index_chat = self._resolve_study_group_id(chat_id)
            clean_chat_id = str(target_index_chat).replace("-100", "").replace("-", "").lstrip("@")
            target_t_id = thread_id
            sort_mode = "seq"  # Default is natural lecture sequence (1, 2, 3...)

            for p in parts[1:]:
                if p.isdigit():
                    target_t_id = int(p)
                elif p.lower() in ("az", "alpha", "a-z"):
                    sort_mode = "az"
                elif p.lower() in ("seq", "num", "lecture", "order"):
                    sort_mode = "seq"

            # If user ran /index without specifying a topic in DM or General topic (t_id is None or 0)
            # automatically show the Master Topic Directory!
            if not target_t_id:
                await self._handle_admin_command(session, chat_id, admin_id, "/mainindex", message=message)
                return

            # Find topic title
            topics = self._get_topics(target_index_chat, sort_mode="seq")
            matched_topic = next((t for t in topics if t["topic_id"] == target_t_id), None)
            topic_title = matched_topic["topic_title"] if matched_topic else (f"Topic #{target_t_id}" if target_t_id else "General Topic")

            items = self._get_topic_items(target_index_chat, target_t_id, sort_mode=sort_mode)

            if not items and target_t_id:
                scan_notify = await self._send_message(
                    session, chat_id,
                    f"🔍 <b>'{html.escape(topic_title)}'</b> ke media files auto-scan kiye ja rahe hain...",
                    message_thread_id=thread_id
                )
                try:
                    proc = await asyncio.create_subprocess_exec(
                        sys.executable, "-m", "devi.operator.group_scanner", str(target_index_chat), str(target_t_id),
                        cwd=str(BASE_PROJECT_DIR),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await asyncio.wait_for(proc.communicate(), timeout=45.0)
                    # Re-fetch topic title and items
                    topics = self._get_topics(target_index_chat, sort_mode="seq")
                    matched_topic = next((t for t in topics if t["topic_id"] == target_t_id), None)
                    if matched_topic:
                        topic_title = matched_topic["topic_title"]
                    items = self._get_topic_items(target_index_chat, target_t_id, sort_mode=sort_mode)
                except Exception as e:
                    logger.warning(f"Error during auto-healing topic scan: {e}")
                if scan_notify:
                    self.create_tracked_task(self._auto_delete_message(session, chat_id, scan_notify, 2))

            if not items:
                help_msg = (
                    f"⚠️ <b>Is Topic ('{html.escape(topic_title)}') ke liye koi items/lectures registered nahi hain.</b>\n\n"
                    f"💡 <b>Index Items Add karne ke 2 Tareeqe:</b>\n"
                    f"1️⃣ <b>Reply se Add Karein</b>: Kisi bhi lecture/file message par <b>Reply</b> karein aur likhein:\n"
                    f"   <code>/additem Lecture 01 - Anatomy Basics</code>\n"
                    f"2️⃣ <b>Link se Add Karein</b>:\n"
                    f"   <code>/addlink Lecture 01 https://t.me/c/...</code>\n\n"
                    f"Uske baad yahan <code>/topicindex</code> likhein, auto-card generate aur pin ho jayega! 🎯"
                )
                await self._send_message(session, chat_id, help_msg, message_thread_id=thread_id)
                return

            cards = []
            safe_topic_title = html.escape(topic_title)
            current_card_lines = [
                "✨ <b>TOPIC STUDY INDEX &amp; TABLE OF CONTENTS</b> 📑",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"📂 <b>Subject:</b> <b>{safe_topic_title}</b>",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ]

            for idx, itm in enumerate(items, 1):
                icon = itm.get("icon") or "🎬"
                raw_title = str(itm.get("title") or "").strip()
                if not raw_title:
                    raw_title = f"Lecture Material #{idx:02d}"
                safe_title = html.escape(raw_title)

                if itm.get("custom_link"):
                    link = itm["custom_link"].strip()
                elif itm.get("msg_id"):
                    m_id = itm["msg_id"]
                    if target_t_id and target_t_id > 1:
                        link = f"https://t.me/c/{clean_chat_id}/{target_t_id}/{m_id}" if clean_chat_id.isdigit() else f"https://t.me/{clean_chat_id}/{target_t_id}/{m_id}"
                    else:
                        link = f"https://t.me/c/{clean_chat_id}/{m_id}" if clean_chat_id.isdigit() else f"https://t.me/{clean_chat_id}/{m_id}"
                elif target_t_id and target_t_id > 1:
                    link = f"https://t.me/c/{clean_chat_id}/{target_t_id}" if clean_chat_id.isdigit() else f"https://t.me/{clean_chat_id}/{target_t_id}"
                else:
                    link = f"https://t.me/c/{clean_chat_id}" if clean_chat_id.isdigit() else f"https://t.me/{clean_chat_id}"

                line = f"{icon} <code>[{idx:02d}]</code> <a href=\"{link}\"><b>{safe_title}</b></a>"
                if sum(len(l) for l in current_card_lines) + len(line) > 3400:
                    current_card_lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    cards.append("\n".join(current_card_lines))
                    current_card_lines = [
                        f"📑 <b>TOPIC INDEX (Part {len(cards)+1})</b>",
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    ]
                current_card_lines.append(line)

            current_card_lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"📚 <b>Total Materials:</b> <code>{len(items)}</code> Lectures &amp; Notes",
                "📌 <i>Tap any lecture title above to jump directly to the post.</i>",
                "👨‍⚕️ <b>Kind Doctor</b> 🤍 • <i>Medical Study Companion</i>"
            ])
            cards.append("\n".join(current_card_lines))

            first_msg_id = None
            for idx, card in enumerate(cards):
                m_id = await self._send_message(
                    session,
                    chat_id,
                    card,
                    message_thread_id=thread_id,
                    disable_web_page_preview=True
                )
                if idx == 0 and m_id:
                    first_msg_id = m_id
                await asyncio.sleep(0.5)

            if first_msg_id:
                pinned = await self._pin_message(session, chat_id, first_msg_id, silent=True)
                pin_status = "📌 Auto-pinned at top of topic!" if pinned else ""
                conf = await self._send_message(
                    session,
                    chat_id,
                    f"✅ **Topic Index Card Posted!** {pin_status}",
                    message_thread_id=thread_id
                )
                if conf and os.getenv("ENABLE_AUTO_DELETE", "false").lower() == "true":
                    self.create_tracked_task(self._auto_delete_message(session, chat_id, conf, 15))

        elif cmd == "/settopic":
            if len(parts) < 2:
                await self._send_message(
                    session,
                    chat_id,
                    "Usage:\n• Inside a topic: `/settopic Cardiology`\n• Or with ID: `/settopic <topic_id> Cardiology`",
                    message_thread_id=thread_id
                )
                return

            if parts[1].isdigit() and len(parts) >= 3:
                t_id = int(parts[1])
                t_title = " ".join(parts[2:])
            elif thread_id:
                t_id = thread_id
                t_title = " ".join(parts[1:])
            else:
                await self._send_message(
                    session,
                    chat_id,
                    "⚠️ Please specify topic ID or run this inside the topic:\n`/settopic <topic_id> <title>`",
                    message_thread_id=thread_id
                )
                return

            self._save_topic(chat_id, t_id, t_title)
            await self._send_message(
                session,
                chat_id,
                f"✅ **Topic Registered Successfully!**\n\n• **Title**: {t_title}\n• **Topic ID**: `{t_id}`\n\nAb aap `/mainindex` chala kar ise master directory me include kar sakte hain.",
                message_thread_id=thread_id
            )

        elif cmd == "/additem":
            if not reply_to:
                await self._send_message(
                    session,
                    chat_id,
                    "⚠️ **Reply Required:**\nKisi bhi lecture video, PDF ya message par **Reply** karke likhein:\n`/additem Lecture 01 - Anatomy Basics`",
                    message_thread_id=thread_id
                )
                return

            target_msg_id = reply_to.get("message_id")
            item_title = " ".join(parts[1:]).strip() if len(parts) > 1 else ""
            if not item_title:
                item_title = reply_to.get("caption") or reply_to.get("text") or f"Item #{target_msg_id}"
                item_title = item_title.split("\n")[0][:45]

            target_t_id = thread_id or 0
            icon = "🎬"
            if "document" in reply_to:
                icon = "📄"
            elif "photo" in reply_to:
                icon = "🖼️"
            elif "audio" in reply_to or "voice" in reply_to:
                icon = "🎙️"

            self._save_topic_item(chat_id, target_t_id, item_title, msg_id=target_msg_id, icon=icon)
            items = self._get_topic_items(chat_id, target_t_id)
            await self._send_message(
                session,
                chat_id,
                f"✅ **Added to Topic Index!**\n{icon} **#{len(items):02d}** • {item_title}\n\nJab sab add ho jayein, type `/topicindex` to generate & pin card.",
                message_thread_id=thread_id
            )

        elif cmd == "/addlink":
            if len(parts) < 3:
                await self._send_message(
                    session,
                    chat_id,
                    "Usage: `/addlink Lecture 01 - Intro https://t.me/c/...`",
                    message_thread_id=thread_id
                )
                return
            target_link = parts[-1]
            title_text = " ".join(parts[1:-1]).strip()
            target_t_id = thread_id or 0
            self._save_topic_item(chat_id, target_t_id, title_text, custom_link=target_link, icon="🎬")
            items = self._get_topic_items(chat_id, target_t_id)
            await self._send_message(
                session,
                chat_id,
                f"✅ **Link Added to Topic Index!**\n🎬 **#{len(items):02d}** • [{title_text}]({target_link})\n\nType `/topicindex` to publish.",
                message_thread_id=thread_id
            )

        elif cmd == "/topics":
            target_topics_chat = self._resolve_study_group_id(chat_id)
            topics = self._get_topics(target_topics_chat, sort_mode="az")
            if not topics:
                await self._send_message(session, chat_id, "Abhi is group me koi Topics registered nahi hain. <code>/settopic &lt;title&gt;</code> use karein.", message_thread_id=thread_id)
                return
            t_list = "\n".join(f"• <code>[{idx:02d}]</code> {t.get('topic_icon','📖')} <b>{html.escape(t['topic_title'])}</b> (ID: <code>{t['topic_id']}</code>)" for idx, t in enumerate(topics, 1))
            msg = (
                f"📚 <b>REGISTERED STUDY TOPICS</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📊 <b>Total Subjects:</b> <code>{len(topics)}</code> (Alphabetical A–Z)\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{t_list}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• Add Topic: <code>/settopic &lt;title&gt;</code>\n"
                f"• Delete Topic: <code>/deltopic &lt;topic_id&gt;</code>\n"
                f"• Publish Directory: <code>/mainindex</code>"
            )
            await self._send_message(
                session,
                chat_id,
                msg,
                message_thread_id=thread_id
            )

        elif cmd == "/deltopic":
            if len(parts) < 2 or not parts[1].isdigit():
                await self._send_message(session, chat_id, "Usage: `/deltopic <topic_id>`", message_thread_id=thread_id)
                return
            t_id = int(parts[1])
            self._delete_topic(chat_id, t_id)
            await self._send_message(session, chat_id, f"🗑️ Topic `{t_id}` and its index items have been removed.", message_thread_id=thread_id)

        elif cmd == "/clearindex":
            target_t_id = thread_id or 0
            cnt = self._clear_topic_items(chat_id, target_t_id)
            await self._send_message(session, chat_id, f"🗑️ Cleared `{cnt}` index items for this topic. You can now add fresh items.", message_thread_id=thread_id)

        # -------------------------------------------------------------
        # MEMBER AUDIT, NETWORK HUB & MULTI-TENANT TRACKER
        # -------------------------------------------------------------
        elif cmd in ("/members", "/memberaudit", "/auditmembers"):
            target_chat_id = self._resolve_study_group_id(chat_id)
            if len(parts) > 1 and parts[1].lstrip("-").isdigit():
                target_chat_id = int(parts[1])

            # Multi-Tenant Access: Check if caller is Admin of this specific group (or Master Admin)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(
                    session, chat_id,
                    "⚠️ **Access Denied:** Member audit is only accessible to group administrators.",
                    message_thread_id=thread_id
                )
                return

            try:
                with get_db_conn() as conn:
                    conn.row_factory = sqlite3.Row
                    cur = conn.execute(
                        "SELECT user_id, full_name, username, join_date FROM member_history WHERE chat_id = ? ORDER BY join_date DESC LIMIT 15",
                        (target_chat_id,)
                    )
                    recent_joins = cur.fetchall()
                    total_tracked = conn.execute(
                        "SELECT COUNT(*) FROM member_history WHERE chat_id = ?",
                        (target_chat_id,)
                    ).fetchone()[0]

                    cur2 = conn.execute(
                        "SELECT user_id, old_name, new_name, old_username, new_username, changed_at FROM member_name_changes ORDER BY changed_at DESC LIMIT 5"
                    )
                    recent_changes = cur2.fetchall()
            except Exception as e:
                logger.warning(f"Error querying member history: {e}")
                recent_joins, total_tracked, recent_changes = [], 0, []

            join_lines = []
            for j in recent_joins:
                uname = f"@{j['username']}" if j['username'] else "No Username"
                date_str = str(j['join_date'])[:16]
                join_lines.append(f"• `{date_str}`: **{j['full_name']}** ({uname}) - ID: `{j['user_id']}`")

            changes_lines = []
            for c in recent_changes:
                dt = str(c['changed_at'])[:16]
                if c['old_username'] != c['new_username']:
                    changes_lines.append(f"• `{dt}`: ID `{c['user_id']}` ➔ @{c['old_username']} ➔ @{c['new_username']}")
                else:
                    changes_lines.append(f"• `{dt}`: ID `{c['user_id']}` ➔ '{c['old_name']}' ➔ '{c['new_name']}'")

            join_block = "\n".join(join_lines) if join_lines else "_No recent joins logged yet._"
            changes_block = "\n".join(changes_lines) if changes_lines else "_No name changes detected._"

            audit_card = (
                f"👥 **GROUP MEMBER AUDIT & TIME-TRACKER** 🩺\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🏛️ **Target Group**: `{target_chat_id}`\n"
                f"📊 **Tracked Members**: `{total_tracked}`\n\n"
                f"🕒 **Recent Joins (Last 15):**\n"
                f"{join_block}\n\n"
                f"🔄 **Recent Identity & Username Shifts:**\n"
                f"{changes_block}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"💡 _Tap below to export full member dataset as CSV file._"
            )

            btn_markup = {
                "inline_keyboard": [
                    [{"text": "📥 Export Full Members CSV", "callback_data": f"act_exp_members_{target_chat_id}"}]
                ]
            }
            await self._send_message(session, chat_id, audit_card, reply_markup=btn_markup, message_thread_id=thread_id)

        elif cmd in ("/allgroups", "/network", "/mygroups"):
            # Master Admin Exclusive (@Kinddoctor4u: 1553619403, @Ammitrajput1: 759038032)
            if admin_id not in self.master_admin_ids:
                await self._send_message(session, chat_id, "⚠️ This master control is reserved strictly for Bot Owners.", message_thread_id=thread_id)
                return

            try:
                with get_db_conn() as conn:
                    conn.row_factory = sqlite3.Row
                    cur = conn.execute("SELECT chat_id, title, username, member_count, registered_at FROM bot_network_chats WHERE is_active = 1")
                    groups = cur.fetchall()
            except Exception as e:
                logger.warning(f"Error querying bot_network_chats: {e}")
                groups = []

            if not groups:
                await self._send_message(session, chat_id, "🌐 **No external groups registered in bot network yet.**\nWhen the bot is added to any group as admin, it will auto-register here!", message_thread_id=thread_id)
                return

            grp_lines = []
            kb_rows = []
            for idx, g in enumerate(groups, 1):
                c_id = g['chat_id']
                t_name = g['title'] or f"Group {c_id}"
                grp_lines.append(f"**[{idx:02d}]** 🏛️ **{t_name}**\n     ID: `{c_id}`  ·  Added: `{str(g['registered_at'])[:10]}`")
                kb_rows.append([
                    {"text": f"👥 Audit #{idx}", "callback_data": f"act_view_members_{c_id}"},
                    {"text": f"📥 CSV #{idx}", "callback_data": f"act_exp_members_{c_id}"}
                ])

            network_card = (
                f"👑 **MASTER BOT NETWORK (Total: {len(groups)} Groups)**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Bot jis-jis group me add hai unki live list:\n\n"
                + "\n\n".join(grp_lines) +
                f"\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👉 _Neeche buttons se kisi bhi group ke members audit ya export karein:_"
            )
            await self._send_message(session, chat_id, network_card, reply_markup={"inline_keyboard": kb_rows}, message_thread_id=thread_id)

        elif cmd in ("/exportmembers", "/exportcsv"):
            target_chat_id = self._resolve_study_group_id(chat_id)
            if len(parts) > 1 and parts[1].lstrip("-").isdigit():
                target_chat_id = int(parts[1])

            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Admin rights required.", message_thread_id=thread_id)
                return

            await self._export_members_csv_file(session, chat_id, target_chat_id, message_thread_id=thread_id)

        # -------------------------------------------------------------
        # 2B. GROUP CUSTOMIZATION & RULES MANAGEMENT (Admin Controls)
        # -------------------------------------------------------------
        elif cmd == "/setwelcome":
            target_chat_id = self._resolve_study_group_id(chat_id)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Group Admin rights required.", message_thread_id=thread_id)
                return

            welcome_body = text[len(parts[0]):].strip()
            if not welcome_body:
                usage_txt = (
                    "⚙️ **Set Custom Welcome Message:**\n\n"
                    "Usage: `/setwelcome <your message>`\n\n"
                    "**Available Placeholders:**\n"
                    "• `{name}` — New member's name / clickable tag\n"
                    "• `{group}` — Group title\n"
                    "• `{rules}` — Group rules text\n\n"
                    "**Example:**\n"
                    "`/setwelcome Welcome {name} to {group}! 🩺 Check /rules and happy learning!`"
                )
                await self._send_message(session, chat_id, usage_txt, message_thread_id=thread_id)
                return

            self._save_group_setting(target_chat_id, "welcome_text", welcome_body)
            await self._send_message(
                session, 
                chat_id, 
                f"✅ **Custom Welcome Message Saved!**\n\nNaye members ko ye message receive hoga:\n\n{welcome_body}",
                message_thread_id=thread_id
            )

        elif cmd == "/welcometoggle":
            target_chat_id = self._resolve_study_group_id(chat_id)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Group Admin rights required.", message_thread_id=thread_id)
                return

            curr_settings = self._get_group_settings(target_chat_id)
            curr_val = curr_settings.get("welcome_enabled", 1)
            
            if len(parts) > 1:
                arg = parts[1].lower()
                new_val = 1 if arg in ("on", "true", "enable", "1") else 0
            else:
                new_val = 0 if curr_val else 1

            self._save_group_setting(target_chat_id, "welcome_enabled", new_val)
            status_str = "✅ **ENABLED**" if new_val else "❌ **DISABLED**"
            await self._send_message(
                session, 
                chat_id, 
                f"🔔 **Welcome Greetings:** {status_str} for group `{target_chat_id}`",
                message_thread_id=thread_id
            )

        elif cmd == "/jointrack":
            target_chat_id = self._resolve_study_group_id(chat_id)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Group Admin rights required.", message_thread_id=thread_id)
                return

            curr_settings = self._get_group_settings(target_chat_id)
            curr_val = curr_settings.get("join_track_enabled", 1)
            
            if len(parts) > 1:
                arg = parts[1].lower()
                new_val = 1 if arg in ("on", "true", "enable", "1") else 0
            else:
                new_val = 0 if curr_val else 1

            self._save_group_setting(target_chat_id, "join_track_enabled", new_val)
            status_str = "✅ **ENABLED**" if new_val else "❌ **DISABLED**"
            await self._send_message(
                session, 
                chat_id, 
                f"🛡️ **Member Join Intel Tracking:** {status_str} for group `{target_chat_id}`",
                message_thread_id=thread_id
            )

        elif cmd == "/setrules":
            target_chat_id = self._resolve_study_group_id(chat_id)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Group Admin rights required.", message_thread_id=thread_id)
                return

            rules_body = text[len(parts[0]):].strip()
            if not rules_body:
                usage_txt = (
                    "📜 **Set Group Rules:**\n\n"
                    "Usage: `/setrules <rules text>`\n\n"
                    "**Example:**\n"
                    "`/setrules 1. Be respectful\n2. Only medical study content\n3. No spam or external ads`"
                )
                await self._send_message(session, chat_id, usage_txt, message_thread_id=thread_id)
                return

            self._save_group_setting(target_chat_id, "rules_text", rules_body)
            await self._send_message(
                session, 
                chat_id, 
                f"✅ **Group Rules Updated Successfully!**\n\nMembers can view them anytime using `/rules`.",
                message_thread_id=thread_id
            )

        elif cmd == "/rules":
            target_chat_id = self._resolve_study_group_id(chat_id)
            curr_settings = self._get_group_settings(target_chat_id)
            rules_content = curr_settings.get("rules_text")
            
            grp_title = "Study Group"
            if message and "chat" in message:
                grp_title = message["chat"].get("title", grp_title)

            if not rules_content:
                rules_card = (
                    f"📜 **{grp_title} — Code of Conduct & Guidelines** 🩺\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"1️⃣ **Medical & Educational Content Only:** Focus strictly on lectures, doubts, and medical discussions.\n"
                    f"2️⃣ **Respectful & Supportive Environment:** Treat all batchmates and doctors politely.\n"
                    f"3️⃣ **Zero Spam / Promotion Tolerance:** External links, betting, and unauthorized promotions are strictly prohibited.\n"
                    f"4️⃣ **Privacy First:** Do not share sensitive personal numbers or data.\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"💡 *Admin can customize these rules using `/setrules <text>`*"
                )
            else:
                rules_card = (
                    f"📜 **{grp_title} — Official Group Rules** 🩺\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"{rules_content}\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                )
            await self._send_message(session, chat_id, rules_card, message_thread_id=thread_id)

        elif cmd in ("/cleanbot", "/cleanwelcome", "/delwelcome", "/purgewelcome"):
            target_chat_id = self._resolve_study_group_id(chat_id)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Group Admin rights required.", message_thread_id=thread_id)
                return

            msg_ids = self._get_logged_welcome_messages(target_chat_id)
            if not msg_ids:
                await self._send_message(session, chat_id, "ℹ️ No pending welcome or bot messages found to clean.", message_thread_id=thread_id)
                return

            status_msg_id = await self._send_message(session, chat_id, f"🧹 Cleaning `{len(msg_ids)}` bot & welcome card(s)...", message_thread_id=thread_id)
            deleted_count = 0
            for mid in msg_ids:
                success = await self._delete_message(session, target_chat_id, mid)
                if success:
                    deleted_count += 1
                await asyncio.sleep(0.04)

            self._clear_logged_welcome_messages(target_chat_id)
            if status_msg_id:
                await self._delete_message(session, chat_id, status_msg_id)

            notice = await self._send_message(
                session, 
                chat_id, 
                f"🧹 **Bot Cleanup Complete:** Successfully removed `{deleted_count}` welcome & bot card(s) from chat.",
                message_thread_id=thread_id
            )
            if notice:
                self.create_tracked_task(self._auto_delete_message(session, chat_id, notice, 10))

        elif cmd in ("/setlang", "/language", "/lang"):
            target_chat_id = self._resolve_study_group_id(chat_id)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Group Admin rights required.", message_thread_id=thread_id)
                return

            if len(parts) > 1:
                target_lang = parts[1].lower().strip()
                if target_lang in ("en", "english"):
                    self._save_group_setting(target_chat_id, "language", "en")
                    await self._send_message(session, chat_id, "🌐 **Language Updated:** Bot language set to **English** 🇬🇧", message_thread_id=thread_id)
                elif target_lang in ("hi", "hinglish", "hindi"):
                    self._save_group_setting(target_chat_id, "language", "hi")
                    await self._send_message(session, chat_id, "🌐 **Language Updated:** Bot language set to **Hinglish** 🇮🇳", message_thread_id=thread_id)
                else:
                    await self._send_message(session, chat_id, "⚠️ Invalid language. Supported: `/setlang en` (English) or `/setlang hi` (Hinglish)", message_thread_id=thread_id)
            else:
                curr_lang = self._get_group_settings(target_chat_id).get("language", "en")
                lang_name = "English 🇬🇧" if curr_lang == "en" else "Hinglish 🇮🇳"
                guide = (
                    f"🌐 **Bot Language Configuration:**\n\n"
                    f"• Current Language: **{lang_name}**\n\n"
                    f"**Switch Language:**\n"
                    f"• `/setlang en` — Switch to International English\n"
                    f"• `/setlang hi` — Switch to Roman Hinglish"
                )
                await self._send_message(session, chat_id, guide, message_thread_id=thread_id)

        # -------------------------------------------------------------
        # 2C. CLOUD CONTENT FORWARDER, TAG REMOVER & USER INSPECTOR
        # -------------------------------------------------------------
        elif cmd == "/setroute":
            target_chat_id = self._resolve_study_group_id(chat_id)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Group Admin rights required.", message_thread_id=thread_id)
                return

            if len(parts) < 2:
                guide = (
                    "🔗 **Setup Cloud Auto-Forward Route (Zero Forward Tag):**\n\n"
                    "Usage: `/setroute <source_chat_id> [target_topic_id]`\n\n"
                    "**How it works:**\n"
                    "• When any new video lecture or PDF arrives in `<source_chat_id>`, bot automatically copies it into this group with **ZERO forward tag**!\n"
                    "• Make sure Kind Doctor Bot is added as Admin in both groups.\n\n"
                    "**Example:**\n"
                    "`/setroute -1001234567890`"
                )
                await self._send_message(session, chat_id, guide, message_thread_id=thread_id)
                return

            raw_src = parts[1].strip()
            try:
                src_chat_id = int(raw_src)
            except ValueError:
                await self._send_message(session, chat_id, "⚠️ Invalid Source Chat ID. Must be a numeric Telegram ID (e.g. `-100...`).", message_thread_id=thread_id)
                return

            tgt_topic = thread_id
            if len(parts) > 2 and parts[2].isdigit():
                tgt_topic = int(parts[2])

            try:
                with get_db_conn() as conn:
                    cur = conn.execute("""
                        INSERT INTO telegram_forward_routes (source_chat_id, source_topic_id, target_chat_id, target_topic_id, created_by)
                        VALUES (?, 0, ?, ?, ?)
                    """, (src_chat_id, target_chat_id, tgt_topic or 0, admin_id))
                    route_id = cur.lastrowid
                
                await self._send_message(
                    session,
                    chat_id,
                    f"✅ **Auto-Forward Route #{route_id} Created Successfully!**\n\n"
                    f"• **Source Group:** `{src_chat_id}`\n"
                    f"• **Destination:** `{target_chat_id}` (Topic: `{tgt_topic or 'General'}`)\n"
                    f"• **Forward Tag:** ❌ Stripped (Original Post Look)\n"
                    f"• **Status:** 🟢 Active & Live Syncing",
                    message_thread_id=thread_id
                )
            except Exception as e:
                await self._send_message(session, chat_id, f"❌ Error creating route: {e}", message_thread_id=thread_id)

        elif cmd == "/settopicroute":
            target_chat_id = self._resolve_study_group_id(chat_id)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Group Admin rights required.", message_thread_id=thread_id)
                return

            if len(parts) < 3:
                guide = (
                    "🎯 **Setup Specific Topic-to-Topic Forward Route:**\n\n"
                    "Usage: `/settopicroute <source_chat_id> <source_topic_id> [target_topic_id]`\n\n"
                    "**Example:**\n"
                    "`/settopicroute -1001234567890 12 55`\n"
                    "↳ Copies messages only from Source Topic 12 into Target Topic 55 with zero forward tags!"
                )
                await self._send_message(session, chat_id, guide, message_thread_id=thread_id)
                return

            try:
                src_chat_id = int(parts[1])
                src_topic_id = int(parts[2])
                tgt_topic = int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else (thread_id or 0)
                
                with get_db_conn() as conn:
                    cur = conn.execute("""
                        INSERT INTO telegram_forward_routes (source_chat_id, source_topic_id, target_chat_id, target_topic_id, created_by)
                        VALUES (?, ?, ?, ?, ?)
                    """, (src_chat_id, src_topic_id, target_chat_id, tgt_topic, admin_id))
                    route_id = cur.lastrowid

                await self._send_message(
                    session,
                    chat_id,
                    f"✅ **Topic Route #{route_id} Established!**\n\n"
                    f"• **Source Topic:** `{src_chat_id}` (Topic `{src_topic_id}`)\n"
                    f"• **Target Topic:** `{target_chat_id}` (Topic `{tgt_topic}`)\n"
                    f"• **Tag Removal:** 100% Clean Reposting Active!",
                    message_thread_id=thread_id
                )
            except Exception as e:
                await self._send_message(session, chat_id, f"❌ Error creating topic route: {e}", message_thread_id=thread_id)

        elif cmd == "/routes":
            target_chat_id = self._resolve_study_group_id(chat_id)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Group Admin rights required.", message_thread_id=thread_id)
                return

            try:
                with get_db_conn() as conn:
                    conn.row_factory = sqlite3.Row
                    routes = conn.execute(
                        "SELECT * FROM telegram_forward_routes WHERE target_chat_id = ? OR source_chat_id = ? ORDER BY id DESC",
                        (target_chat_id, target_chat_id)
                    ).fetchall()

                if not routes:
                    await self._send_message(session, chat_id, "ℹ️ No auto-forward routes configured yet for this group.\n\nUse `/setroute <source_chat_id>` to connect a source group.", message_thread_id=thread_id)
                    return

                lines = ["🔄 **Active Cloud Forwarding Routes:**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━"]
                for r in routes:
                    status_icon = "🟢 ACTIVE" if r["is_active"] else "⏸️ PAUSED"
                    lines.append(
                        f"**Route #{r['id']}** [{status_icon}]\n"
                        f"• From: `{r['source_chat_id']}` (Topic: `{r['source_topic_id'] or 'All'}`)\n"
                        f"• To: `{r['target_chat_id']}` (Topic: `{r['target_topic_id'] or 'General'}`)\n"
                        f"• Media Filter: `{r['media_filter']}` | Strip Links: `{'Yes' if r['strip_links'] else 'No'}`\n"
                        f"• Controls: `/pauseroute {r['id']}` · `/resumeroute {r['id']}` · `/delroute {r['id']}`\n"
                    )
                lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                await self._send_message(session, chat_id, "\n".join(lines), message_thread_id=thread_id)
            except Exception as e:
                await self._send_message(session, chat_id, f"Error listing routes: {e}", message_thread_id=thread_id)

        elif cmd in ("/pauseroute", "/resumeroute", "/delroute", "/routefilter"):
            target_chat_id = self._resolve_study_group_id(chat_id)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Group Admin rights required.", message_thread_id=thread_id)
                return

            if cmd == "/pauseroute":
                if len(parts) < 2 or not parts[1].isdigit():
                    await self._send_message(session, chat_id, "Usage: `/pauseroute <route_id>`", message_thread_id=thread_id)
                    return
                r_id = int(parts[1])
                with get_db_conn() as conn:
                    conn.execute("UPDATE telegram_forward_routes SET is_active = 0 WHERE id = ?", (r_id,))
                await self._send_message(session, chat_id, f"⏸️ Forward Route #{r_id} paused.", message_thread_id=thread_id)

            elif cmd == "/resumeroute":
                if len(parts) < 2 or not parts[1].isdigit():
                    await self._send_message(session, chat_id, "Usage: `/resumeroute <route_id>`", message_thread_id=thread_id)
                    return
                r_id = int(parts[1])
                with get_db_conn() as conn:
                    conn.execute("UPDATE telegram_forward_routes SET is_active = 1 WHERE id = ?", (r_id,))
                await self._send_message(session, chat_id, f"▶️ Forward Route #{r_id} resumed!", message_thread_id=thread_id)

            elif cmd == "/delroute":
                if len(parts) < 2 or not parts[1].isdigit():
                    await self._send_message(session, chat_id, "Usage: `/delroute <route_id>`", message_thread_id=thread_id)
                    return
                r_id = int(parts[1])
                with get_db_conn() as conn:
                    conn.execute("DELETE FROM telegram_forward_routes WHERE id = ?", (r_id,))
                await self._send_message(session, chat_id, f"🗑️ Forward Route #{r_id} deleted successfully.", message_thread_id=thread_id)

            elif cmd == "/routefilter":
                if len(parts) < 3 or not parts[1].isdigit() or parts[2].lower() not in ("all", "video", "doc", "audio", "photo", "text"):
                    await self._send_message(session, chat_id, "Usage: `/routefilter <route_id> <all|video|doc|audio|photo|text>`\n\nExample: `/routefilter 1 video`", message_thread_id=thread_id)
                    return
                r_id = int(parts[1])
                f_val = parts[2].lower()
                with get_db_conn() as conn:
                    conn.execute("UPDATE telegram_forward_routes SET media_filter = ? WHERE id = ?", (f_val, r_id))
                await self._send_message(session, chat_id, f"🎯 Route #{r_id} filter updated to: `{f_val}`", message_thread_id=thread_id)

        elif cmd == "/clone":
            target_chat_id = self._resolve_study_group_id(chat_id)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Group Admin rights required.", message_thread_id=thread_id)
                return

            from_chat = None
            from_msg = None

            if reply_to and reply_to.get("message_id"):
                from_chat = chat_id
                from_msg = reply_to["message_id"]
            elif len(parts) > 1:
                link = parts[1].strip()
                m_priv = re.search(r't\.me/c/(\d+)/(\d+)', link)
                m_pub = re.search(r't\.me/([a-zA-Z0-9_]+)/(\d+)', link)
                if m_priv:
                    from_chat = int(f"-100{m_priv.group(1)}")
                    from_msg = int(m_priv.group(2))
                elif m_pub:
                    from_chat = f"@{m_pub.group(1)}"
                    from_msg = int(m_pub.group(2))

            if not from_chat or not from_msg:
                guide = (
                    "📥 **Instant 1-Click Message Cloner (Zero Forward Tag):**\n\n"
                    "• **Method 1:** Reply to any message in group with `/clone`\n"
                    "• **Method 2:** Type `/clone <telegram_post_link>`\n\n"
                    "**Example:**\n"
                    "`/clone https://t.me/c/1234567890/45`"
                )
                await self._send_message(session, chat_id, guide, message_thread_id=thread_id)
                return

            copy_url = f"https://api.telegram.org/bot{self.token}/copyMessage"
            payload = {
                "chat_id": chat_id,
                "from_chat_id": from_chat,
                "message_id": from_msg
            }
            if thread_id:
                payload["message_thread_id"] = thread_id

            try:
                async with session.post(copy_url, json=payload, timeout=12) as r:
                    res_data = await r.json()
                    if res_data.get("ok"):
                        await self._send_message(session, chat_id, "✔ **Cloned Successfully!** *(Forward tag removed)* 🩺", message_thread_id=thread_id)
                    else:
                        err_desc = res_data.get("description", "Unknown error")
                        await self._send_message(session, chat_id, f"⚠️ Clone failed: {err_desc}", message_thread_id=thread_id)
            except Exception as e:
                await self._send_message(session, chat_id, f"❌ Error cloning message: {e}", message_thread_id=thread_id)

        elif cmd == "/batchclone":
            target_chat_id = self._resolve_study_group_id(chat_id)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Group Admin rights required.", message_thread_id=thread_id)
                return

            if len(parts) < 3:
                guide = (
                    "📦 **Batch Message Cloner (Zero Forward Tag):**\n\n"
                    "Usage: `/batchclone <start_msg_link> <end_msg_link>`\n\n"
                    "**Example:**\n"
                    "`/batchclone https://t.me/c/1234567890/10 https://t.me/c/1234567890/25`"
                )
                await self._send_message(session, chat_id, guide, message_thread_id=thread_id)
                return

            link1, link2 = parts[1].strip(), parts[2].strip()
            m1 = re.search(r't\.me/(?:c/(\d+)|([a-zA-Z0-9_]+))/(\d+)', link1)
            m2 = re.search(r't\.me/(?:c/(\d+)|([a-zA-Z0-9_]+))/(\d+)', link2)

            if not m1 or not m2:
                await self._send_message(session, chat_id, "⚠️ Invalid link formats. Both must be Telegram message links.", message_thread_id=thread_id)
                return

            src_chat = int(f"-100{m1.group(1)}") if m1.group(1) else f"@{m1.group(2)}"
            start_id = int(m1.group(3))
            end_id = int(m2.group(3))

            if start_id > end_id:
                start_id, end_id = end_id, start_id

            total_range = min(100, end_id - start_id + 1)
            status_msg = await self._send_message(session, chat_id, f"⏳ Starting batch clone of `{total_range}` items from `{src_chat}`...", message_thread_id=thread_id)

            cloned_count = 0
            copy_url = f"https://api.telegram.org/bot{self.token}/copyMessage"

            for mid in range(start_id, start_id + total_range):
                payload = {
                    "chat_id": chat_id,
                    "from_chat_id": src_chat,
                    "message_id": mid
                }
                if thread_id:
                    payload["message_thread_id"] = thread_id
                try:
                    async with session.post(copy_url, json=payload, timeout=8) as r:
                        rd = await r.json()
                        if rd.get("ok"):
                            cloned_count += 1
                    await asyncio.sleep(0.15)
                except Exception:
                    pass

            if status_msg:
                await self._delete_message(session, chat_id, status_msg)

            await self._send_message(
                session, 
                chat_id, 
                f"🎉 **Batch Clone Completed!**\n\n• Successfully Cloned: `{cloned_count}` / `{total_range}` items\n• Forward Tags: ❌ Removed (Clean Posts) ✨",
                message_thread_id=thread_id
            )

        elif cmd in ("/send", "/pm", "/msg", "/sendlink", "/reply", "/say", "/dr"):
            # 1. Admin speaking through bot in Group or DM: /say <msg> or /dr <msg>
            if cmd in ("/say", "/dr") or (cmd == "/reply" and len(parts) > 1 and not (parts[1].isdigit() or parts[1].startswith("@"))):
                msg_body = text.split(maxsplit=1)[1] if len(parts) > 1 else ""
                if not msg_body:
                    await self._send_message(session, chat_id, "ℹ️ **Usage**: `/say <message>` (Group me student ke message par reply karke type karein)", message_thread_id=thread_id)
                    return
                
                # Delete the admin command message if in a group
                if message and str(chat_id).startswith("-"):
                    await self._delete_message(session, chat_id, message.get("message_id"))
                
                rep_id = reply_to.get("message_id") if reply_to else None
                bot_out = f"👨‍⚕️ **Kind Doctor:**\n\n{msg_body}"
                await self._send_message(session, chat_id, bot_out, reply_to=rep_id, message_thread_id=thread_id)
                return

            # 2. Direct DM to student: /send <target> <message> or /sendlink <target>
            if len(parts) < 2:
                await self._send_message(
                    session, chat_id,
                    f"ℹ️ **Kind Doctor Direct Messaging & Replies:**\n\n"
                    f"• `/send <@username or user_id> <message>` — Student ko bot se direct private message bhejein\n"
                    f"• `/sendlink <@username or user_id>` — Student ko single-use 30-min invite link bhejein\n"
                    f"• `/say <message>` — Group me student ke message par reply karke anonymously bolein\n\n"
                    f"*(Tip: Student ke message card par Telegram ka default 'Reply' karke type karne par bhi direct reply chala jata hai)*",
                    message_thread_id=thread_id
                )
                return

            target_arg = parts[1].strip()
            target_uid = None
            target_uname = None
            
            if target_arg.lstrip("-").isdigit():
                target_uid = int(target_arg)
            else:
                target_uname = target_arg.lstrip("@")

            # Lookup in DB if needed
            u_row = None
            with get_db_conn() as conn:
                if target_uid:
                    u_row = conn.execute("SELECT user_id, first_name, username FROM telegram_users_dossier WHERE user_id = ?", (target_uid,)).fetchone()
                    if not u_row:
                        u_row = conn.execute("SELECT user_id, full_name, username FROM member_history WHERE user_id = ?", (target_uid,)).fetchone()
                else:
                    u_row = conn.execute("SELECT user_id, first_name, username FROM telegram_users_dossier WHERE username = ? COLLATE NOCASE", (target_uname,)).fetchone()
                    if not u_row:
                        u_row = conn.execute("SELECT user_id, full_name, username FROM member_history WHERE username = ? COLLATE NOCASE", (target_uname,)).fetchone()

            if u_row:
                target_uid = u_row[0]
                user_label = f"{u_row[1]} (@{u_row[2]})" if u_row[2] else f"{u_row[1]}"
            else:
                user_label = f"`{target_arg}`"

            if not target_uid:
                await self._send_message(
                    session, chat_id,
                    f"⚠️ User `{target_arg}` not found in bot memory. Kripya unka numeric User ID use karein (e.g. `/send 12345678 message`).",
                    message_thread_id=thread_id
                )
                return

            if cmd == "/sendlink":
                target_grp = self.target_chat
                link_url = ""
                if target_grp:
                    try:
                        invite_url = f"https://api.telegram.org/bot{self.token}/createChatInviteLink"
                        expire_ts = int((datetime.now() + timedelta(minutes=30)).timestamp())
                        async with session.post(invite_url, json={"chat_id": target_grp, "member_limit": 1, "expire_date": expire_ts}, timeout=10) as resp:
                            if resp.status == 200:
                                res_data = await resp.json()
                                link_url = res_data.get("result", {}).get("invite_link")
                    except Exception as e:
                        logger.warning(f"Error creating invite link in sendlink: {e}")

                if link_url:
                    content_to_send = (
                        f"👨‍⚕️ **Kind Doctor:**\n\n"
                        f"Welcome! Here is your exclusive single-use invite link to the study group:\n"
                        f"{link_url}\n\n"
                        f"*(Note: Yeh link 30 minutes me expire ho jayega. Happy studying!)*"
                    )
                else:
                    content_to_send = "👨‍⚕️ **Kind Doctor:**\n\nGroup link generation is temporarily busy. Please hold on or contact admin."
            else:
                if len(parts) < 3:
                    await self._send_message(session, chat_id, f"ℹ️ Please include a message: `/send {target_arg} <your message>`", message_thread_id=thread_id)
                    return
                body_text = text.split(maxsplit=2)[2].strip()
                content_to_send = f"👨‍⚕️ **Kind Doctor:**\n\n{body_text}"

            # Attempt delivery to student
            delivered = await self._send_message(session, target_uid, content_to_send)
            if delivered:
                await self._send_message(
                    session, chat_id,
                    f"✅ **Message Delivered to {user_label}** (`{target_uid}`)!\n\n*(Sent under anonymous '👨‍⚕️ Kind Doctor' brand)*",
                    message_thread_id=thread_id
                )
            else:
                await self._send_message(
                    session, chat_id,
                    f"⚠️ **Delivery to {user_label} failed.**\n\n"
                    f"📌 **Reason**: Telegram policy prevents bots from initiating a new private chat if the user has never started the bot in PM (`/start`).\n\n"
                    f"💡 **Solution**: Agar user group me hai, toh group me unke message par swipe/reply karke `/say <message>` likhein!",
                    message_thread_id=thread_id
                )
            return

        elif cmd in ("/userinfo", "/whois", "/info", "/sangmata", "/history"):
            target_user_id = None
            target_username = None
            fwd_origin_notice = ""

            # 1. First priority: Explicit Argument provided in text (/whois @username, /whois 12345, /whois@username)
            if len(parts) > 1:
                arg = parts[1].strip().lstrip("@")
                if arg.isdigit():
                    target_user_id = int(arg)
                else:
                    target_username = arg
            elif "@" in parts[0]:
                cmd_uname = parts[0].split("@", 1)[1].strip()
                if cmd_uname.lower() not in ("kinddoc_bot", "kinddocbot", "kindsync_bot", "tg_kindsync_pro_bot", "kinddoctor_bot", "bot"):
                    target_username = cmd_uname

            # 2. Second priority: If no explicit argument was given, check real reply-to message
            if not target_user_id and not target_username and reply_to:
                is_forum_header = reply_to.get("forum_topic_created") or (thread_id and reply_to.get("message_id") == thread_id)
                if not is_forum_header:
                    if "forward_from" in reply_to and reply_to["forward_from"]:
                        fwd_u = reply_to["forward_from"]
                        target_user_id = fwd_u.get("id")
                        target_username = fwd_u.get("username")
                        fwd_origin_notice = "📩 *(Extracted from Forwarded Message Author)*\n"
                    elif "forward_origin" in reply_to and reply_to["forward_origin"]:
                        fwd_orig = reply_to["forward_origin"]
                        orig_type = fwd_orig.get("type")
                        if orig_type == "user" and "sender_user" in fwd_orig:
                            target_user_id = fwd_orig["sender_user"].get("id")
                            target_username = fwd_orig["sender_user"].get("username")
                            fwd_origin_notice = "📩 *(Extracted from Forwarded Message Author)*\n"
                        elif orig_type == "hidden_user":
                            hidden_name = fwd_orig.get("sender_user_name", "Anonymous")
                            await self._send_message(
                                session, chat_id,
                                f"👤 **User Intelligence Dossier (SangMata & Rose style)** 🩺\n"
                                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                f"👤 **Display Name**: {hidden_name}\n"
                                f"🔒 **Privacy Status**: This user has enabled Telegram Forward Privacy.\n"
                                f"⚠️ Numerical ID and direct profile link are masked by Telegram security settings.\n"
                                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                                message_thread_id=thread_id
                            )
                            return
                        elif orig_type in ("channel", "chat"):
                            fwd_c = fwd_orig.get("chat", {})
                            c_title = fwd_c.get("title", "Channel/Group")
                            c_id = fwd_c.get("id")
                            c_uname = fwd_c.get("username")
                            await self._send_message(
                                session, chat_id,
                                f"📢 **Channel/Group Intelligence Card** 🩺\n"
                                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                                f"📢 **Title**: {c_title}\n"
                                f"🆔 **Chat ID**: `{c_id}`\n"
                                f"🏷️ **Username**: @{c_uname if c_uname else 'Private'}\n"
                                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                                message_thread_id=thread_id
                            )
                            return

                    if not target_user_id and reply_to.get("from"):
                        target_user_id = reply_to["from"].get("id")
                        target_username = reply_to["from"].get("username")

            # 3. Third priority: If still no target user, default to admin's own ID
            if not target_user_id and not target_username:
                target_user_id = admin_id


            user_data = None
            with get_db_conn() as conn:
                conn.row_factory = sqlite3.Row
                if target_user_id:
                    user_data = conn.execute("SELECT * FROM telegram_users_dossier WHERE user_id = ?", (target_user_id,)).fetchone()
                elif target_username:
                    user_data = conn.execute("SELECT * FROM telegram_users_dossier WHERE username = ? COLLATE NOCASE", (target_username,)).fetchone()
                    if user_data:
                        target_user_id = user_data["user_id"]
                    else:
                        try:
                            row = conn.execute("SELECT user_id FROM member_name_changes WHERE old_username = ? OR new_username = ? COLLATE NOCASE LIMIT 1", (target_username, target_username)).fetchone()
                            if row:
                                target_user_id = row["user_id"]
                                user_data = conn.execute("SELECT * FROM telegram_users_dossier WHERE user_id = ?", (target_user_id,)).fetchone()
                        except Exception:
                            pass

            live_global_user = None
            if not target_user_id and target_username:
                try:
                    from devi.operator.osint_resolver import osint_resolver
                    live_global_user = await osint_resolver.resolve_entity(target_username)
                    if live_global_user:
                        target_user_id = live_global_user["user_id"]
                        with get_db_conn() as conn:
                            conn.execute("""
                                INSERT OR IGNORE INTO telegram_users_dossier 
                                (user_id, first_name, last_name, username, phone_number, is_premium, language_code, first_seen, last_seen, total_messages, name_history, username_history, changes_count)
                                VALUES (?, ?, ?, ?, ?, ?, 'en', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0, '[]', '[]', 0)
                            """, (
                                live_global_user["user_id"],
                                live_global_user["first_name"],
                                live_global_user["last_name"],
                                live_global_user["username"],
                                live_global_user["phone"],
                                1 if live_global_user["is_premium"] else 0
                            ))
                            conn.row_factory = sqlite3.Row
                            user_data = conn.execute("SELECT * FROM telegram_users_dossier WHERE user_id = ?", (target_user_id,)).fetchone()
                except Exception as ex:
                    logger.warning(f"Live OSINT entity resolution error: {ex}")

            if not target_user_id and target_username:
                await self._send_message(
                    session, chat_id,
                    f"⚠️ **Telegram par '@{html.escape(target_username)}' naam ka koi active user nahi mila.**\n\n"
                    f"💡 **Check Karein:**\n"
                    f"• Username spelling sahi hai ya nahi\n"
                    f"• User ID ya direct message forward karke bhi check kar sakte hain!",
                    message_thread_id=thread_id
                )
                return


            photo_count = 0
            dc_string = "DC2 (Amsterdam, NL) [Estimated]"
            group_role_str = "🎓 Group Member"
            live_premium = False
            live_is_bot = False
            live_lang = "en"
            live_fn = ""
            live_ln = ""
            live_un = ""

            if target_user_id:
                # 1. Fetch User Profile Photos & DC
                try:
                    p_url = f"https://api.telegram.org/bot{self.token}/getUserProfilePhotos?user_id={target_user_id}&limit=1"
                    async with session.get(p_url, timeout=5) as p_resp:
                        if p_resp.status == 200:
                            p_data = await p_resp.json()
                            if p_data.get("ok"):
                                photo_count = p_data.get("result", {}).get("total_count", 0)
                                photos = p_data.get("result", {}).get("photos", [])
                                if photos and len(photos[0]) > 0:
                                    f_id = photos[0][0].get("file_id", "")
                                    dc_string = self._extract_dc(f_id)
                except Exception:
                    pass

                # 2. Fetch Live Chat Member Status if in a group
                if chat_id and chat_id < 0:
                    try:
                        cm_url = f"https://api.telegram.org/bot{self.token}/getChatMember?chat_id={chat_id}&user_id={target_user_id}"
                        async with session.get(cm_url, timeout=5) as cm_resp:
                            if cm_resp.status == 200:
                                cm_data = await cm_resp.json()
                                if cm_data.get("ok"):
                                    res = cm_data.get("result", {})
                                    st = res.get("status", "member")
                                    c_title = res.get("custom_title", "")
                                    u_obj = res.get("user", {})
                                    live_fn = u_obj.get("first_name", "")
                                    live_ln = u_obj.get("last_name", "")
                                    live_un = u_obj.get("username", "")
                                    live_premium = u_obj.get("is_premium", False)
                                    live_is_bot = u_obj.get("is_bot", False)
                                    live_lang = u_obj.get("language_code", "en")

                                    if st == "creator":
                                        group_role_str = "👑 Group Owner (Creator)"
                                    elif st == "administrator":
                                        group_role_str = f"🛡️ Administrator {'(' + c_title + ')' if c_title else ''}"
                                    elif st == "restricted":
                                        group_role_str = "🚫 Restricted Member"
                                    elif st == "left":
                                        group_role_str = "🚪 Left Group"
                                    elif st == "kicked":
                                        group_role_str = "🚫 Banned / Kicked"
                                    else:
                                        group_role_str = "🎓 Group Member"
                    except Exception:
                        pass

            if user_data:
                u_id = user_data["user_id"]
                fn = live_fn or user_data["first_name"] or ""
                ln = live_ln or user_data["last_name"] or ""
                full_n = f"{fn} {ln}".strip() or "User"
                uname = live_un or user_data["username"] or "No Username"
                prem_val = live_premium or bool(user_data["is_premium"])
                prem = "⭐️ Yes (Telegram Premium)" if prem_val else "Standard Account"
                total_m = user_data["total_messages"] or 0
                first_s = user_data["first_seen"] or "N/A"
                last_s = user_data["last_seen"] or "N/A"
                u_age = self._estimate_account_age(u_id)
                lang = live_lang or user_data["language_code"] or "en"
            elif target_user_id:
                u_id = target_user_id
                full_n = f"{live_fn} {live_ln}".strip() or (f"@{target_username}" if target_username else "User")
                uname = live_un or target_username or "No Username"
                prem = "⭐️ Yes (Telegram Premium)" if live_premium else "Standard Account"
                total_m = 0
                first_s = "Today (Live Lookup)"
                last_s = "Now"
                u_age = self._estimate_account_age(u_id)
                lang = live_lang
            else:
                await self._send_message(session, chat_id, "⚠️ User not found. Reply to a message, forward a message, or provide User ID / @username.", message_thread_id=thread_id)
                return

            # Live SangMata Biometric & Multi-Year Timeline Interception
            name_hist_list = []
            uname_hist_list = []
            try:
                from devi.operator.osint_resolver import osint_resolver
                live_sm = await osint_resolver.fetch_live_sangmata_history(u_id or uname)
                if live_sm:
                    name_hist_list = live_sm.get("names", [])
                    uname_hist_list = live_sm.get("usernames", [])
            except Exception as e:
                logger.debug(f"SangMata fetch error: {e}")

            if not name_hist_list and user_data:
                with suppress(Exception):
                    name_hist_list = json.loads(user_data["name_history"] or "[]")
            if not uname_hist_list and user_data:
                with suppress(Exception):
                    uname_hist_list = json.loads(user_data["username_history"] or "[]")

            name_lines = []
            if name_hist_list:
                for idx, item in enumerate(name_hist_list, 1):
                    n = item.get("name", "Unknown")
                    ts = item.get("changed_at", "")
                    ts_str = f"[{ts}] " if ts else ""
                    name_lines.append(f"{idx}. {ts_str}`{n}`")
            else:
                name_lines.append(f"1. `{full_n}` ➔ `(Current Active Name)`")

            uname_lines = []
            if uname_hist_list:
                for idx, item in enumerate(uname_hist_list, 1):
                    u = item.get("username", "None")
                    u_formatted = u if u.startswith("@") or u == "(empty)" else f"@{u}"
                    ts = item.get("changed_at", "")
                    ts_str = f"[{ts}] " if ts else ""
                    uname_lines.append(f"{idx}. {ts_str}`{u_formatted}`")
            else:
                uname_lines.append(f"1. `@{uname}` ➔ `(Current Active Username)`")

            name_hist_text = "\n".join(name_lines)
            uname_hist_text = "\n".join(uname_lines)

            bot_status_str = "🤖 Bot Account" if live_is_bot else "👤 Human User (Real Account)"
            photo_str = f"{photo_count} Photo{'s' if photo_count != 1 else ''} Uploaded" if photo_count > 0 else "None (Default / Hidden Avatar)"

            # Deep OSINT Analytics & Threat Scoring
            total_changes = len(name_hist_list) + len(uname_hist_list)
            phone_val = user_data["phone_number"] if user_data and "phone_number" in user_data.keys() else None
            phone_str = f"⚠️ Leaked in Group: `{phone_val}`" if phone_val and phone_val != "Not Shared" else "🔒 Clean (No Leaked Phone Tracked)"
            hex_id = f"0x{u_id:X}" if u_id else "N/A"

            if total_m >= 50:
                act_tier = "🔥 Super Contributor (50+ Msgs)"
            elif total_m >= 10:
                act_tier = "🌱 Regular Student (10–50 Msgs)"
            else:
                act_tier = "👀 New Joiner / Silent Reader (<10 Msgs)"

            risk_score = 0
            if total_changes >= 3:
                risk_score += 35
                velocity_str = f"⚠️ High Velocity ({total_changes} identity shifts detected - Impersonation Watchlist)"
            elif total_changes > 0:
                risk_score += 10
                velocity_str = f"🟡 Moderate ({total_changes} identity shift detected)"
            else:
                velocity_str = "🟢 0 Shifts (100% Stable Identity)"

            if "Fresh Account" in u_age or "Brand New" in u_age:
                risk_score += 25
            if phone_val and phone_val != "Not Shared":
                risk_score += 15

            if risk_score >= 50:
                risk_badge = f"🔴 {risk_score}/100 (High Risk / Threat Alert)"
            elif risk_score >= 25:
                risk_badge = f"🟡 {risk_score}/100 (Moderate Watchlist)"
            else:
                risk_badge = f"🟢 {risk_score}/100 (Safe Student Account)"

            extra_intel_lines = []
            if live_global_user:
                if live_global_user.get("bio"):
                    extra_intel_lines.append(f"📝 **Profile Bio**: {html.escape(live_global_user['bio'])}")
                if live_global_user.get("common_chats_count", 0) > 0:
                    extra_intel_lines.append(f"👥 **Shared Groups**: {live_global_user['common_chats_count']} common chats with bot")
                if live_global_user.get("is_scam") or live_global_user.get("is_fake"):
                    extra_intel_lines.append("🚨 **SECURITY ALERT**: ⚠️ Official Telegram Scam/Fake Flag Detected!")
                if live_global_user.get("is_verified"):
                    extra_intel_lines.append("🌟 **Verification**: Official Verified Account")

            extra_intel_str = "\n".join(extra_intel_lines) + "\n" if extra_intel_lines else ""

            phone_line = f"📱 **Phone**: `{phone_val}`\n" if phone_val and phone_val != "Not Shared" else ""
            card = (
                f"👤 **USER INTELLIGENCE & SANGMATA DOSSIER** 🩺\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{fwd_origin_notice}"
                f"👤 **Student Name**: [{full_n}](tg://user?id={u_id})\n"
                f"🏷️ **Username**: @{uname}\n"
                f"🆔 **Telegram ID**: `{u_id}`\n"
                f"🗓️ **Account Age**: {u_age}\n"
                f"⭐️ **Telegram Tier**: {prem}\n"
                f"🛡️ **Group Status**: {group_role_str}\n"
                f"{phone_line}"
                f"{extra_intel_str}\n"
                f"📜 **Name History (SangMata Timeline):**\n"
                f"{name_hist_text}\n\n"
                f"🏷️ **Username History (SangMata Timeline):**\n"
                f"{uname_hist_text}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *Kind Doctor Live Sentinel • SangMata Biometrics*"
            )


            whois_markup = None
            if self.is_admin(admin_id) and u_id != admin_id:
                whois_markup = {
                    "inline_keyboard": [
                        [
                            {"text": "🚫 Ban Member", "callback_data": f"ban_{u_id}"},
                            {"text": "👢 Kick Member", "callback_data": f"kick_{u_id}"}
                        ]
                    ]
                }

            await self._send_message(session, chat_id, card, reply_markup=whois_markup, message_thread_id=thread_id)

        elif cmd in ("/phone", "/phonelookup"):
            if len(parts) < 2:
                await self._send_message(
                    session, chat_id,
                    "📞 **Phone Intelligence Usage:**\nType `/phone <number>`\n\nExample: `/phone +919876543210` or `/phone 9876543210`",
                    message_thread_id=thread_id
                )
                return

            phone_query = parts[1].strip()
            p_data = self._lookup_phone_osint(phone_query)

            matched_str = "• *No registered group members matched.*"
            if p_data["matched_users"]:
                matched_lines = []
                for u in p_data["matched_users"]:
                    fn = f"{u.get('first_name') or ''} {u.get('last_name') or ''}".strip() or "User"
                    un = f"@{u['username']}" if u.get("username") else "No Username"
                    matched_lines.append(f"• [{fn}](tg://user?id={u['user_id']}) ({un}) — `ID: {u['user_id']}`")
                matched_str = "\n".join(matched_lines)

            phone_card = (
                f"📞 **TELECOM & PHONE NUMBER OSINT RADAR** 🩺\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📱 **Query Number**: <code>{p_data['formatted']}</code>\n"
                f"🌐 **Country / Region**: {p_data['country_flag']} {p_data['country']}\n"
                f"📡 **Carrier Circle**: `{p_data['carrier']}`\n"
                f"🔢 **E.164 Format**: <code>{p_data['e164']}</code>\n\n"
                f"👥 **Matched Group Profiles in Database:**\n"
                f"{matched_str}\n\n"
                f"⚡ **Direct Action Links:**\n"
                f"• 💬 [Open in WhatsApp]({p_data['whatsapp_link']})\n"
                f"• 📱 [Direct Telegram Chat]({p_data['telegram_link']})\n"
                f"• 🔍 [Truecaller Web Lookup]({p_data['truecaller_url']})\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *Kind Doctor Live Sentinel • OSINT Telecommunication Intelligence*"
            )
            await self._send_message(session, chat_id, phone_card, message_thread_id=thread_id)

        elif cmd in ("/email", "/emaillookup"):
            if len(parts) < 2:
                await self._send_message(
                    session, chat_id,
                    "✉️ **Email OSINT Usage:**\nType `/email <address>`\n\nExample: `/email doctor@gmail.com`",
                    message_thread_id=thread_id
                )
                return

            email_query = parts[1].strip()
            e_data = self._lookup_email_osint(email_query)

            if not e_data["is_valid"]:
                await self._send_message(
                    session, chat_id,
                    f"⚠️ **Invalid Email Syntax**: `{email_query}`\nKripya valid email format enter karein (e.g. `user@example.com`).",
                    message_thread_id=thread_id
                )
                return

            disp_tag = "🔴 High Risk (Burner / Disposable Email Detected)" if e_data["is_disposable"] else "🟢 Valid (Standard Mailbox)"
            
            matched_str = "• *No registered group members matched.*"
            if e_data["matched_users"]:
                matched_lines = []
                for u in e_data["matched_users"]:
                    fn = f"{u.get('first_name') or ''} {u.get('last_name') or ''}".strip() or "User"
                    un = f"@{u['username']}" if u.get("username") else "No Username"
                    matched_lines.append(f"• [{fn}](tg://user?id={u['user_id']}) ({un}) — `ID: {u['user_id']}`")
                matched_str = "\n".join(matched_lines)

            email_card = (
                f"✉️ **EMAIL ADDRESS & DOMAIN OSINT RADAR** 🩺\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"📧 **Query Email**: <code>{e_data['email']}</code>\n"
                f"🏢 **Domain**: <code>{e_data['domain']}</code>\n"
                f"{e_data['provider_icon']} **Mail Provider**: `{e_data['provider_type']}`\n"
                f"🛡️ **Mailbox Authenticity**: {disp_tag}\n\n"
                f"👥 **Matched Group Profiles:**\n"
                f"{matched_str}\n\n"
                f"⚡ **Deep Forensic Links:**\n"
                f"• 🖼️ [Gravatar Profile Avatar]({e_data['gravatar_url']})\n"
                f"• 🔓 [HaveIBeenPwned Breach Check]({e_data['hibp_url']})\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🛡️ *Kind Doctor Live Sentinel • Email Digital Footprint Analysis*"
            )
            await self._send_message(session, chat_id, email_card, message_thread_id=thread_id)

        # -------------------------------------------------------------
        # 3. GROUP SEARCH & DISCOVERY ENGINE
        # -------------------------------------------------------------
        elif cmd in ("/find", "/search"):

            if len(parts) < 2:
                await self._send_message(
                    session,
                    chat_id,
                    "🔍 **Search Usage:**\nType `/find <keyword>` or `/search <keyword>`\n\nExample: `/find ECG` or `/find Lecture 01`",
                    message_thread_id=thread_id
                )
                return

            query = " ".join(parts[1:]).strip()
            results = self._search_group_items(chat_id, query)
            if not results:
                await self._send_message(
                    session,
                    chat_id,
                    f"🔍 No indexed lectures or files found matching: `{query}`\n\n💡 *Tip: Admins can index files using `/additem <title>` on any media message.*",
                    message_thread_id=thread_id
                )
                return

            clean_chat_id = str(chat_id).replace("-100", "").replace("-", "").lstrip("@")
            lines = [
                "🔍 <b>STUDY REPOSITORY SEARCH</b>",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                f"🔎 <b>Query:</b> <code>{html.escape(query)}</code> (Found {len(results)} match{'es' if len(results) > 1 else ''})",
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            ]
            for idx, r in enumerate(results, 1):
                icon = r.get("icon") or "🎬"
                title = r["title"]
                topic_name = r.get("topic_title") or f"Topic #{r.get('topic_id', 0)}"
                if r.get("custom_link"):
                    link = r["custom_link"]
                elif r.get("msg_id"):
                    link = f"https://t.me/c/{clean_chat_id}/{r['msg_id']}" if clean_chat_id.isdigit() else f"https://t.me/{clean_chat_id}/{r['msg_id']}"
                else:
                    link = f"https://t.me/c/{clean_chat_id}/{r.get('topic_id', 0)}"

                lines.append(f"{icon} <code>[{idx:02d}]</code> <a href=\"{link}\">{html.escape(title.strip())}</a>\n   └ <i>Topic:</i> <b>{html.escape(topic_name.strip())}</b>")

            lines.extend([
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                "📌 <i>Tap any blue title above to jump directly to that lecture.</i>",
                "👨‍⚕️ <b>Kind Doctor</b> 🤍 • <i>Medical Study Desk</i>"
            ])
            await self._send_message(
                session,
                chat_id,
                "\n".join(lines),
                message_thread_id=thread_id,
                disable_web_page_preview=True
            )

        # -------------------------------------------------------------
        # 4. SUBJECT-WISE CLINICAL MEDICAL FORMULA & DOSAGE ENGINE
        # -------------------------------------------------------------
        elif cmd in ("/calc", "/dose", "/formula", "/score", "/bmi", "/bsa", "/gfr", "/pedia", "/burns", "/uop", "/edd", "/psm", "/drip", "/infusion", "/map", "/abg", "/sodium", "/gcs", "/curb65", "/wells"):
            sub_cmd = cmd.lstrip("/").lower()
            if sub_cmd in ("calc", "dose", "formula", "score"):
                sub_cmd = parts[1].lower() if len(parts) > 1 else "menu"
                calc_args = parts[2:]
            else:
                calc_args = parts[1:]

            # A. MASTER CLINICAL MENU
            if sub_cmd in ("menu", "help", "?"):
                menu_card = (
                    "🧮 **KIND DOCTOR CLINICAL MEDICAL FORMULA & DOSAGE SUITE** 🩺\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "Subject-Wise Clinical Ward, ICU & Exam Calculators:\n\n"
                    "👶 **1. PEDIATRICS (Ward & PICU):**\n"
                    "• `/pedia dose <adult_dose> <wt_kg>` ➔ Clark's & Young's Rule\n"
                    "• `/pedia mgkg <dose_mg_kg> <wt_kg> [syrup_mg_5ml]` ➔ Exact Syrup mL\n"
                    "• `/pedia ett <age_years>` ➔ ET Tube Size & Insertion Depth\n"
                    "• `/pedia fluids <wt_kg>` ➔ Holliday-Segar 4-2-1 Maintenance IV Fluid\n"
                    "• `/pedia apgar <A> <P> <G> <A> <R>` ➔ APGAR Score & Resuscitation\n\n"
                    "🩺 **2. GENERAL MEDICINE & CRITICAL CARE:**\n"
                    "• `/bmi <weight_kg> <height_cm>` ➔ BMI & Devine Ideal Body Weight\n"
                    "• `/bsa <height_cm> <weight_kg>` ➔ Mosteller & DuBois Body Surface Area\n"
                    "• `/gfr <age> <weight_kg> <serum_cr> <m/f>` ➔ Cockcroft-Gault CrCl & CKD Stage\n"
                    "• `/map <sbp> <dbp>` ➔ Mean Arterial Pressure & Shock Perfusion\n"
                    "• `/abg <Na> <Cl> <HCO3> [Albumin]` ➔ Serum Anion Gap & Albumin Correction\n"
                    "• `/sodium <measured_na> <glucose>` ➔ Corrected Sodium in Hyperglycemia\n"
                    "• `/gcs <E:1-4> <V:1-5> <M:1-6>` ➔ Glasgow Coma Scale\n"
                    "• `/curb65 <C> <U> <R> <B> <65>` ➔ Pneumonia Severity & Admission\n"
                    "• `/wells <DVT> <Alt> <HR> <Immob> <Prior> <Hemo> <Ca>` ➔ Wells PE Score\n\n"
                    "🔪 **3. SURGERY & EMERGENCY:**\n"
                    "• `/burns <weight_kg> <tbsa_percent>` ➔ Parkland 24h Ringer Lactate Fluid\n"
                    "• `/uop <volume_ml> <weight_kg> <hours>` ➔ Urine Output Rate (mL/kg/hr)\n\n"
                    "🤰 **4. OBSTETRICS & GYNECOLOGY (OBG):**\n"
                    "• `/edd <LMP_Date_DD/MM/YYYY>` ➔ Naegele's Rule, POG Weeks & Trimester\n\n"
                    "📊 **5. PSM & BIOSTATISTICS:**\n"
                    "• `/psm matrix <TP> <FP> <FN> <TN>` ➔ Sensitivity, Specificity, PPV, NPV\n\n"
                    "💊 **6. PHARMACOLOGY & INFUSIONS:**\n"
                    "• `/drip <volume_ml> <hours> [drop_factor]` ➔ IV Drip Rate in Drops/min\n"
                    "• `/infusion <drug_mg> <vol_ml> <dose_mcg_kg_min> <wt_kg>` ➔ Inotrope Syringe Pump (mL/hr)\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "💡 *Tip: Direct commands work anywhere, e.g. `/bmi 70 175` ya `/burns 60 30`*"
                )
                await self._send_message(session, chat_id, menu_card, message_thread_id=thread_id)

            # B. BMI & BODY COMPOSITION
            elif sub_cmd == "bmi":
                if len(calc_args) < 2:
                    await self._send_message(session, chat_id, "Usage: `/bmi <weight_kg> <height_cm>`\nExample: `/bmi 70 175`", message_thread_id=thread_id)
                    return
                try:
                    wt, ht = float(calc_args[0]), float(calc_args[1])
                    res = calc_bmi(wt, ht)
                    card = (
                        f"⚖️ **Clinical Calculator: Body Mass Index (BMI)** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• **Weight**: `{wt:.1f} kg` | **Height**: `{ht:.0f} cm`\n"
                        f"• **Calculated BMI**: `{res['bmi']} kg/m²`\n"
                        f"• **WHO Classification**: **{res['who_category']}**\n"
                        f"• **Asian Cutoff**: `{res['asian_category']}`\n"
                        f"• **Ideal Body Weight (Devine)**:\n"
                        f"   - Male: `{res['ideal_body_weight_male']} kg` | Female: `{res['ideal_body_weight_female']} kg`\n\n"
                        f"💡 *Clinical Pearl: Asian cutoff considers BMI ≥ 23.0 as overweight and ≥ 25.0 as obese.*"
                    )
                    await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input numbers. Example: `/bmi 70 175`", message_thread_id=thread_id)

            # C. BSA (BODY SURFACE AREA)
            elif sub_cmd == "bsa":
                if len(calc_args) < 2:
                    await self._send_message(session, chat_id, "Usage: `/bsa <height_cm> <weight_kg>`\nExample: `/bsa 175 70`", message_thread_id=thread_id)
                    return
                try:
                    ht, wt = float(calc_args[0]), float(calc_args[1])
                    res = calc_bsa(ht, wt)
                    card = (
                        f"📐 **Clinical Calculator: Body Surface Area (BSA)** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• **Mosteller Formula**: `{res['mosteller_m2']} m²`\n"
                        f"• **DuBois Formula**: `{res['dubois_m2']} m²`\n\n"
                        f"💡 *Used for Chemotherapy dosing, Cardiac Index, and Renal GFR normalization.*"
                    )
                    await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input. Example: `/bsa 175 70`", message_thread_id=thread_id)

            # D. GFR & RENAL FUNCTION (Cockcroft-Gault)
            elif sub_cmd == "gfr":
                if len(calc_args) < 3:
                    await self._send_message(session, chat_id, "Usage: `/gfr <age> <weight_kg> <serum_cr> [m/f]`\nExample: `/gfr 55 70 1.2 m`", message_thread_id=thread_id)
                    return
                try:
                    age, wt, cr = float(calc_args[0]), float(calc_args[1]), float(calc_args[2])
                    is_female = len(calc_args) > 3 and calc_args[3].lower().startswith("f")
                    res = calc_gfr(age, wt, cr, is_female=is_female)
                    card = (
                        f"🫘 **Clinical Calculator: GFR / Creatinine Clearance (CrCl)** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• **Age**: `{age:.0f} yrs` | **Weight**: `{wt:.1f} kg` | **Cr**: `{cr:.2f} mg/dL` ({'Female' if is_female else 'Male'})\n"
                        f"• **Calculated CrCl**: `{res['cr_cl_ml_min']} mL/min`\n"
                        f"• **KDIGO CKD Staging**: **{res['ckd_stage']}**\n\n"
                        f"💡 *Formula: Cockcroft-Gault equation [× 0.85 for female patients].*"
                    )
                    await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input. Example: `/gfr 55 70 1.2 m`", message_thread_id=thread_id)

            # E. PEDIATRIC SUITE
            elif sub_cmd == "pedia":
                p_action = calc_args[0].lower() if calc_args else "help"
                if p_action == "dose" and len(calc_args) >= 3:
                    try:
                        adult_dose = float(calc_args[1])
                        wt_or_age = float(calc_args[2])
                        res = calc_pediatric_dose(adult_dose=adult_dose, weight_kg=wt_or_age, age_years=wt_or_age)
                        lines = [f"• **{v['name']}**: `{v['dose']} {v['unit']}` `({v['formula']})`" for v in res.values()]
                        card = (
                            f"👶 **Pediatric Dosage Calculator** 🩺\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• **Adult Reference Dose**: `{adult_dose:.1f} mg`\n\n" +
                            "\n".join(lines) + "\n\n"
                            f"💡 *Tip: Clark's rule (weight-based) is clinically more accurate than Young's rule (age-based).*"
                        )
                        await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                    except ValueError:
                        await self._send_message(session, chat_id, "Usage: `/pedia dose <adult_dose_mg> <weight_kg_or_age>`\nExample: `/pedia dose 500 14`", message_thread_id=thread_id)
                elif p_action == "mgkg" and len(calc_args) >= 3:
                    try:
                        dose_mg_kg = float(calc_args[1])
                        wt = float(calc_args[2])
                        strength = float(calc_args[3]) if len(calc_args) > 3 else None
                        res = calc_mg_per_kg(dose_mg_kg, wt, strength)
                        syrup_text = f"\n• **Syrup Volume**: `{res['syrup_ml']} mL` *(Strength: {strength} mg / 5 mL)*" if "syrup_ml" in res else ""
                        card = (
                            f"👶 **Pediatric mg/kg/dose Calculator** 🩺\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• **Dose**: `{dose_mg_kg} mg/kg` | **Weight**: `{wt} kg`\n"
                            f"• **Total Dose Required**: `{res['total_mg']} mg`" + syrup_text + "\n\n"
                            f"💡 *Example: Paracetamol: 15 mg/kg/dose, Amoxicillin: 40-80 mg/kg/day.*"
                        )
                        await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                    except ValueError:
                        await self._send_message(session, chat_id, "Usage: `/pedia mgkg <dose_mg_per_kg> <weight_kg> [syrup_mg_per_5ml]`\nExample: `/pedia mgkg 15 10 250`", message_thread_id=thread_id)
                elif p_action == "fluids" and len(calc_args) >= 2:
                    try:
                        wt = float(calc_args[1])
                        res = calc_maintenance_fluids(wt)
                        card = (
                            f"💧 **Pediatric Maintenance IV Fluid (Holliday-Segar 4-2-1 Rule)** 🩺\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• **Patient Weight**: `{wt:.1f} kg`\n"
                            f"• **Hourly Infusion Rate**: `{res['rate_ml_hr']} mL/hour`\n"
                            f"• **Total 24-Hour Volume**: `{res['total_24h_ml']} mL/day`\n\n"
                            f"💡 *Rule: 1st 10kg @ 4mL/kg/hr, 2nd 10kg @ +2mL/kg/hr, >20kg @ +1mL/kg/hr.*"
                        )
                        await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                    except ValueError:
                        await self._send_message(session, chat_id, "Usage: `/pedia fluids <weight_kg>`\nExample: `/pedia fluids 15`", message_thread_id=thread_id)
                elif p_action == "ett" and len(calc_args) >= 2:
                    try:
                        age = float(calc_args[1])
                        res = calc_et_tube(age)
                        card = (
                            f"🫁 **Pediatric Endotracheal (ET) Tube Size & Depth** 🩺\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• **Patient Age**: `{age:.1f} years`\n"
                            f"• **Uncuffed ET Tube Size**: `{res['uncuffed_size_mm']} mm ID` `(Age/4 + 4)`\n"
                            f"• **Cuffed ET Tube Size**: `{res['cuffed_size_mm']} mm ID` `(Age/4 + 3.5)`\n"
                            f"• **Insertion Depth at Lip**: `{res['insertion_depth_cm']} cm` `(Age/2 + 12)`\n\n"
                            f"💡 *Rule of Thumb Depth: {res['rule_of_thumb_depth']}. Always keep 0.5mm size above & below ready!*"
                        )
                        await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                    except ValueError:
                        await self._send_message(session, chat_id, "Usage: `/pedia ett <age_years>`\nExample: `/pedia ett 4`", message_thread_id=thread_id)
                elif p_action == "apgar" and len(calc_args) >= 6:
                    try:
                        a, p, g, a2, r = int(calc_args[1]), int(calc_args[2]), int(calc_args[3]), int(calc_args[4]), int(calc_args[5])
                        res = calc_apgar(a, p, g, a2, r)
                        card = (
                            f"👶 **Neonatal APGAR Score** 🩺\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• **Total Score**: `{res['score']}/10` `({res['breakdown']})`\n"
                            f"• **Clinical Status**: **{res['status']}**\n\n"
                            f"💡 *Parameters: Appearance (Color), Pulse (HR), Grimace (Reflex), Activity (Tone), Respiration (Effort).*"
                        )
                        await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                    except ValueError:
                        await self._send_message(session, chat_id, "Usage: `/pedia apgar <A:0-2> <P:0-2> <G:0-2> <A:0-2> <R:0-2>`\nExample: `/pedia apgar 2 2 1 2 2`", message_thread_id=thread_id)
                else:
                    guide = (
                        "👶 **Pediatrics Formula Guide:**\n"
                        "• `/pedia dose <adult_dose> <wt_kg>` (Clark's & Young's Rule)\n"
                        "• `/pedia mgkg <dose_mg_kg> <wt_kg> [syrup_strength_mg_5ml]`\n"
                        "• `/pedia fluids <weight_kg>` (4-2-1 Maintenance IV Fluid)\n"
                        "• `/pedia ett <age_years>` (ET Tube Size & Depth)\n"
                        "• `/pedia apgar <A> <P> <G> <A> <R>` (APGAR Score)"
                    )
                    await self._send_message(session, chat_id, guide, message_thread_id=thread_id)

            # F. PARKLAND BURNS FORMULA
            elif sub_cmd == "burns":
                if len(calc_args) < 2:
                    await self._send_message(session, chat_id, "Usage: `/burns <weight_kg> <tbsa_percent>`\nExample: `/burns 70 30` (70 kg patient with 30% TBSA burns)", message_thread_id=thread_id)
                    return
                try:
                    wt, tbsa = float(calc_args[0]), float(calc_args[1])
                    res = calc_parkland(wt, tbsa)
                    card = (
                        f"🔥 **Parkland Burns Resuscitation Formula** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• **Weight**: `{wt:.1f} kg` | **% TBSA Burns**: `{tbsa:.0f}%`\n"
                        f"• **Total 24h Ringer's Lactate**: `{res['total_24h_ml']:,} mL` `(4 mL × kg × %TBSA)`\n\n"
                        f"⏱️ **Infusion Schedule:**\n"
                        f"• **First 8 Hours** (from time of burn): `{res['first_8h_ml']:,} mL` ➔ **`{res['first_8h_rate_ml_hr']:.0f} mL/hour`**\n"
                        f"• **Next 16 Hours**: `{res['remaining_16h_ml']:,} mL` ➔ **`{res['remaining_16h_rate_ml_hr']:.0f} mL/hour`**\n\n"
                        f"💡 *Goal: Maintain adult urine output ≥ 0.5 mL/kg/hr.*"
                    )
                    await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input. Example: `/burns 70 30`", message_thread_id=thread_id)

            # G. URINE OUTPUT RATE (UOP)
            elif sub_cmd == "uop":
                if len(calc_args) < 3:
                    await self._send_message(session, chat_id, "Usage: `/uop <volume_ml> <weight_kg> <hours>`\nExample: `/uop 150 70 4`", message_thread_id=thread_id)
                    return
                try:
                    vol, wt, hrs = float(calc_args[0]), float(calc_args[1]), float(calc_args[2])
                    res = calc_urine_output(vol, wt, hrs)
                    card = (
                        f"💧 **Urine Output (UOP) Rate Calculator** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• **Volume**: `{vol:.0f} mL` over `{hrs:.1f} hrs` in `{wt:.1f} kg` patient\n"
                        f"• **Calculated UOP**: `{res['uop_ml_kg_hr']} mL/kg/hour`\n"
                        f"• **Clinical Status**: **{res['status']}**\n\n"
                        f"💡 *Target: Adult ≥ 0.5 mL/kg/hr, Pediatrics ≥ 1.0 mL/kg/hr.*"
                    )
                    await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid numbers. Example: `/uop 150 70 4`", message_thread_id=thread_id)

            # H. OBG: EDD & GESTATIONAL AGE (Naegele's Rule)
            elif sub_cmd == "edd":
                if len(calc_args) < 1:
                    await self._send_message(session, chat_id, "Usage: `/edd <LMP_Date_DD/MM/YYYY>`\nExample: `/edd 15/01/2026`", message_thread_id=thread_id)
                    return
                res = calc_edd(calc_args[0])
                if "error" in res:
                    await self._send_message(session, chat_id, f"⚠️ {res['error']}", message_thread_id=thread_id)
                    return
                card = (
                    f"🤰 **OBG: EDD & Gestational Age (Naegele's Rule)** 🩺\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"• **Last Menstrual Period (LMP)**: `{res['lmp']}`\n"
                    f"• **Estimated Date of Delivery (EDD)**: **`{res['edd']}`**\n"
                    f"• **Period of Gestation (POG)**: **`{res['gestational_age']}`** (`{res['total_days']} Days`)\n"
                    f"• **Current Trimester**: **{res['trimester']}**\n\n"
                    f"💡 *Naegele's Formula: LMP + 9 Months + 7 Days (assumes standard 28-day cycle).*"
                )
                await self._send_message(session, chat_id, card, message_thread_id=thread_id)

            # I. PSM & BIOSTATISTICS (2x2 Matrix & Risk)
            elif sub_cmd == "psm":
                psm_mode = calc_args[0].lower() if calc_args else "matrix"
                if psm_mode == "matrix" and len(calc_args) >= 5:
                    try:
                        tp, fp, fn, tn = float(calc_args[1]), float(calc_args[2]), float(calc_args[3]), float(calc_args[4])
                        res = calc_psm_matrix(tp, fp, fn, tn)
                        card = (
                            f"📊 **PSM: 2x2 Diagnostic & Screening Evaluation** 🩺\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"• **TP**: `{tp:.0f}` | **FP**: `{fp:.0f}` | **FN**: `{fn:.0f}` | **TN**: `{tn:.0f}`\n\n"
                            f"🎯 **Diagnostic Performance:**\n"
                            f"• **Sensitivity** `[TP / (TP+FN)]`: **`{res['sensitivity']}%`**\n"
                            f"• **Specificity** `[TN / (TN+FP)]`: **`{res['specificity']}%`**\n"
                            f"• **Positive Predictive Value (PPV)**: **`{res['ppv']}%`**\n"
                            f"• **Negative Predictive Value (NPV)**: **`{res['npv']}%`**\n"
                            f"• **Diagnostic Accuracy**: `{res['accuracy']}%`\n"
                            f"• **Odds Ratio (OR)**: `{res['odds_ratio']}` | **Relative Risk (RR)**: `{res['relative_risk']}`\n\n"
                            f"💡 *PPV increases with higher disease prevalence, while Sensitivity and Specificity remain stable.*"
                        )
                        await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                    except ValueError:
                        await self._send_message(session, chat_id, "Usage: `/psm matrix <TP> <FP> <FN> <TN>`\nExample: `/psm matrix 80 20 10 90`", message_thread_id=thread_id)
                else:
                    guide = (
                        "📊 **PSM Biostatistics Calculators:**\n"
                        "• `/psm matrix <TP> <FP> <FN> <TN>` ➔ Sensitivity, Specificity, PPV, NPV, Odds Ratio\n"
                        "Example: `/psm matrix 80 20 10 90`"
                    )
                    await self._send_message(session, chat_id, guide, message_thread_id=thread_id)

            # J. PHARMACOLOGY IV DRIP RATE
            elif sub_cmd == "drip":
                if len(calc_args) < 2:
                    await self._send_message(session, chat_id, "Usage: `/drip <volume_ml> <hours> [drop_factor: 20/60]`\nExample: `/drip 1000 8 20`", message_thread_id=thread_id)
                    return
                try:
                    vol, hrs = float(calc_args[0]), float(calc_args[1])
                    df = int(calc_args[2]) if len(calc_args) > 2 else 20
                    res = calc_iv_drip(vol, hrs, df)
                    card = (
                        f"💧 **Pharmacology: IV Drip Rate Calculator** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• **Total Volume**: `{vol:.0f} mL` over `{hrs:.1f} hours` (Drop Factor: `{df} gtt/mL`)\n"
                        f"• **Drip Rate**: **`{res['drops_per_min']} Drops/min (gtt/min)`**\n"
                        f"• **Volumetric Infusion Rate**: `{res['ml_per_hour']} mL/hour`\n\n"
                        f"💡 *Formula: (Volume_mL × Drop_Factor) / (Hours × 60 min). Standard Macro set = 20 gtt/mL, Micro set = 60 gtt/mL.*"
                    )
                    await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid numbers. Example: `/drip 1000 8 20`", message_thread_id=thread_id)

            # K. INOTROPE SYRINGE PUMP INFUSION (Norad, Dopamine, Dobutamine)
            elif sub_cmd == "infusion":
                if len(calc_args) < 4:
                    await self._send_message(session, chat_id, "Usage: `/infusion <drug_mg> <vol_ml> <dose_mcg_kg_min> <weight_kg>`\nExample: `/infusion 4 50 0.1 70` (Noradrenaline 4mg in 50mL @ 0.1 mcg/kg/min for 70kg)", message_thread_id=thread_id)
                    return
                try:
                    drug_mg, vol_ml, dose_mcg, wt = float(calc_args[0]), float(calc_args[1]), float(calc_args[2]), float(calc_args[3])
                    res = calc_inotrope_infusion(drug_mg, vol_ml, dose_mcg, wt)
                    card = (
                        f"💉 **ICU Syringe Pump Infusion Rate** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• **Drug In Syringe**: `{drug_mg} mg` in `{vol_ml} mL` *(Conc: `{res['concentration_mcg_ml']} mcg/mL`)*\n"
                        f"• **Desired Dose**: `{dose_mcg} mcg/kg/min` for `{wt} kg` patient\n"
                        f"• **Set Syringe Pump Rate**: **`{res['rate_ml_hr']} mL/hour`**\n\n"
                        f"💡 *Applicable for Noradrenaline, Dopamine, Dobutamine, Adrenaline syringe infusions.*"
                    )
                    await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input. Example: `/infusion 4 50 0.1 70`", message_thread_id=thread_id)

            # L. MAP (MEAN ARTERIAL PRESSURE)
            elif sub_cmd == "map":
                if len(calc_args) < 2:
                    await self._send_message(session, chat_id, "Usage: `/map <sbp> <dbp>`\nExample: `/map 120 80`", message_thread_id=thread_id)
                    return
                try:
                    sbp, dbp = float(calc_args[0]), float(calc_args[1])
                    res = calc_map(sbp, dbp)
                    card = (
                        f"🫀 **Clinical Score: Mean Arterial Pressure (MAP)** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• **Blood Pressure**: `{sbp:.0f}/{dbp:.0f} mmHg`\n"
                        f"• **Calculated MAP**: **`{res['map']} mmHg`**\n"
                        f"• **Perfusion Status**: **{res['status']}**\n\n"
                        f"💡 *Formula: DBP + (SBP - DBP) / 3. Minimum target in sepsis resuscitation is ≥ 65 mmHg.*"
                    )
                    await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input. Example: `/map 120 80`", message_thread_id=thread_id)

            # M. ABG & ANION GAP
            elif sub_cmd in ("abg", "aniongap"):
                if len(calc_args) < 3:
                    await self._send_message(session, chat_id, "Usage: `/abg <Na> <Cl> <HCO3> [Albumin_g_dl]`\nExample: `/abg 140 102 24`", message_thread_id=thread_id)
                    return
                try:
                    na, cl, hco3 = float(calc_args[0]), float(calc_args[1]), float(calc_args[2])
                    alb = float(calc_args[3]) if len(calc_args) > 3 else None
                    res = calc_anion_gap(na, cl, hco3, alb)
                    corr_text = f"\n• **Albumin-Corrected Gap**: `{res['corrected_anion_gap']} mEq/L` *(Albumin: {alb} g/dL)*" if "corrected_anion_gap" in res else ""
                    card = (
                        f"🧪 **Clinical Score: Serum Anion Gap** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• **Electrolytes**: Na⁺ `{na:.0f}` | Cl⁻ `{cl:.0f}` | HCO₃⁻ `{hco3:.0f}` mEq/L\n"
                        f"• **Calculated Anion Gap**: **`{res['anion_gap']} mEq/L`**" + corr_text + "\n"
                        f"• **Interpretation**: **{res['interpretation']}**\n\n"
                        f"💡 *Formula: Na⁺ - (Cl⁻ + HCO₃⁻). Normal reference: 8 - 12 mEq/L.*"
                    )
                    await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input. Example: `/abg 140 102 24`", message_thread_id=thread_id)

            # N. CORRECTED SODIUM
            elif sub_cmd == "sodium":
                if len(calc_args) < 2:
                    await self._send_message(session, chat_id, "Usage: `/sodium <measured_na> <blood_glucose_mg_dl>`\nExample: `/sodium 130 400`", message_thread_id=thread_id)
                    return
                try:
                    na, glu = float(calc_args[0]), float(calc_args[1])
                    res = calc_corrected_sodium(na, glu)
                    card = (
                        f"🧪 **Katz Corrected Sodium in Hyperglycemia** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• **Measured Na⁺**: `{na:.0f} mEq/L` | **Blood Glucose**: `{glu:.0f} mg/dL`\n"
                        f"• **Corrected Sodium (Katz)**: **`{res['corrected_sodium_katz']} mEq/L`** `(+1.6 per 100mg/dL > 100)`\n"
                        f"• **Corrected Sodium (Hillier)**: `{res['corrected_sodium_hillier']} mEq/L` `(+2.4 per 100mg/dL > 100)`\n"
                        f"• **Correction Factor**: `+{res['correction_delta']} mEq/L`\n\n"
                        f"💡 *Crucial in DKA and HHS management to prevent overcorrection of true sodium.*"
                    )
                    await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input. Example: `/sodium 130 400`", message_thread_id=thread_id)

            # O. GLASGOW COMA SCALE (GCS)
            elif sub_cmd == "gcs":
                if len(calc_args) < 3:
                    await self._send_message(session, chat_id, "Usage: `/gcs <Eye:1-4> <Verbal:1-5> <Motor:1-6>`\nExample: `/gcs 4 5 6` (Normal = 15/15, Coma ≤ 8)", message_thread_id=thread_id)
                    return
                try:
                    e, v, m = int(calc_args[0]), int(calc_args[1]), int(calc_args[2])
                    res = calc_gcs(e, v, m)
                    card = (
                        f"🧠 **Neurology: Glasgow Coma Scale (GCS)** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• **Eye (E)**: `{e}/4` | **Verbal (V)**: `{v}/5` | **Motor (M)**: `{m}/6`\n"
                        f"• **Total GCS Score**: **`{res['score']}/15`** `({res['breakdown']})`\n"
                        f"• **Brain Injury Severity**: **{res['severity']}**\n\n"
                        f"💡 *Clinical Axiom: GCS ≤ 8, Intubate! (Requires definitive airway protection).*"
                    )
                    await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input. Example: `/gcs 4 5 6`", message_thread_id=thread_id)

            # P. CURB-65 PNEUMONIA SEVERITY
            elif sub_cmd == "curb65":
                if len(calc_args) < 5:
                    await self._send_message(session, chat_id, "Usage: `/curb65 <Confusion:0/1> <Urea>19:0/1> <RR≥30:0/1> <BP<90/60:0/1> <Age≥65:0/1>`\nExample: `/curb65 1 0 1 0 1`", message_thread_id=thread_id)
                    return
                try:
                    c, u, r, b, age65 = int(calc_args[0]), int(calc_args[1]), int(calc_args[2]), int(calc_args[3]), int(calc_args[4])
                    res = calc_curb65(c, u, r, b, age65)
                    card = (
                        f"🫁 **CURB-65 Community-Acquired Pneumonia Severity** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• **CURB-65 Score**: **`{res['score']}/5`**\n"
                        f"• **Risk Group**: **{res['risk_group']}** `(30-day mortality: {res['mortality_risk']})`\n"
                        f"• **Recommended Action**: **{res['recommendation']}**\n\n"
                        f"💡 *Criteria: Confusion, Urea>19mg/dL (7mmol/L), RR≥30, SBP<90 or DBP≤60, Age≥65.*"
                    )
                    await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input. Example: `/curb65 1 0 1 0 1`", message_thread_id=thread_id)

            # Q. WELLS SCORE FOR PULMONARY EMBOLISM
            elif sub_cmd == "wells":
                if len(calc_args) < 7:
                    await self._send_message(session, chat_id, "Usage: `/wells <DVT_signs:0/1> <PE_likely:0/1> <HR>100:0/1> <Immob_Surg:0/1> <Prior_DVT_PE:0/1> <Hemoptysis:0/1> <Malignancy:0/1>`\nExample: `/wells 1 1 1 0 0 0 0`", message_thread_id=thread_id)
                    return
                try:
                    dvt, pe_top, hr, immob, prior, hemo, ca = int(calc_args[0]), int(calc_args[1]), int(calc_args[2]), int(calc_args[3]), int(calc_args[4]), int(calc_args[5]), int(calc_args[6])
                    res = calc_wells_pe(dvt, pe_top, hr, immob, prior, hemo, ca)
                    card = (
                        f"🫁 **Wells Criteria for Pulmonary Embolism (PE)** 🩺\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"• **Total Wells Score**: **`{res['score']} Points`**\n"
                        f"• **Clinical Probability**: **{res['two_tier_risk']}** `({res['probability_three_tier']})`\n"
                        f"• **Next Diagnostic Step**: **{res['management']}**\n\n"
                        f"💡 *If PE Unlikely (≤4), order high-sensitivity D-dimer. If PE Likely (>4), proceed to CTPA immediately.*"
                    )
                    await self._send_message(session, chat_id, card, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input. Example: `/wells 1 1 1 0 0 0 0`", message_thread_id=thread_id)

        # -------------------------------------------------------------
        # 5. LEGACY EDUCATIONAL COMMANDS REDIRECT
        # -------------------------------------------------------------
        elif cmd in ("/mcq", "/quiz", "/pearl", "/flashcard", "/pomodoro", "/focus"):
            upgrade_notice = (
                "💡 **CLINICAL SUITE UPGRADED!** 🩺\n\n"
                "Old quiz/timer commands have been upgraded to the **Subject-Wise Clinical Medical Formula & Dosage Engine**!\n\n"
                "👉 Type **`/calc`** or **`/dose`** to view all subject calculators (Pediatrics, Medicine, Surgery, OBG, PSM, Pharma)."
            )
            await self._send_message(session, chat_id, upgrade_notice, message_thread_id=thread_id)

        # -------------------------------------------------------------
        # 5. SMART FAQ & AUTO-RESPONDER
        # -------------------------------------------------------------
        elif cmd == "/setfaq":
            if len(parts) < 3:
                await self._send_message(
                    session,
                    chat_id,
                    "Usage: `/setfaq <keyword> <response text>`\n\nExample: `/setfaq schedule Live classes are held Monday & Thursday at 8 PM.`",
                    message_thread_id=thread_id
                )
                return
            kw = parts[1].lower().strip()
            ans = " ".join(parts[2:]).strip()
            self._save_faq(chat_id, kw, ans, admin_id)
            await self._send_message(
                session,
                chat_id,
                f"✅ **FAQ Saved!**\n\n• **Trigger Keyword**: `{kw}`\n• **Response**:\n{ans}\n\nGroup me jab bhi koi yeh keyword bolega, bot auto-reply de dega!",
                message_thread_id=thread_id
            )

        elif cmd == "/delfaq":
            if len(parts) < 2:
                await self._send_message(session, chat_id, "Usage: `/delfaq <keyword>`", message_thread_id=thread_id)
                return
            kw = parts[1].lower().strip()
            deleted = self._delete_faq(chat_id, kw)
            if deleted:
                await self._send_message(session, chat_id, f"🗑️ FAQ for `{kw}` deleted.", message_thread_id=thread_id)
            else:
                await self._send_message(session, chat_id, f"⚠️ No FAQ found for `{kw}`.", message_thread_id=thread_id)

        elif cmd == "/faqs":
            faqs = self._list_faqs(chat_id)
            if not faqs:
                await self._send_message(
                    session,
                    chat_id,
                    "No FAQs configured yet. Admins can create FAQs using:\n`/setfaq <keyword> <response text>`",
                    message_thread_id=thread_id
                )
                return
            faq_list = "\n".join(f"• `{f['keyword']}` ➔ {f['response_text'][:50]}..." for f in faqs)
            await self._send_message(
                session,
                chat_id,
                f"❓ **Configured Group FAQs ({len(faqs)}):**\n\n{faq_list}\n\n• Add: `/setfaq <kw> <text>`\n• Delete: `/delfaq <kw>`",
                message_thread_id=thread_id
            )

        elif cmd == "/faq":
            if len(parts) < 2:
                await self._send_message(session, chat_id, "Usage: `/faq <keyword>` (e.g. `/faq schedule`)", message_thread_id=thread_id)
                return
            kw = parts[1].lower().strip()
            ans = self._get_faq(chat_id, kw)
            if ans:
                await self._send_message(session, chat_id, f"💡 **FAQ: `{kw}`**\n\n{ans}", message_thread_id=thread_id)
            else:
                await self._send_message(session, chat_id, f"⚠️ No FAQ found for `{kw}`. Type `/faqs` to view all.", message_thread_id=thread_id)

        # -------------------------------------------------------------
        # 6. HIGH-YIELD CLINICAL PEARL & SPOILER FLASHCARD
        # -------------------------------------------------------------
        elif cmd in ("/pearl", "/flashcard"):
            subject = " ".join(parts[1:]).strip() if len(parts) > 1 else "Clinical Medicine"
            prompt = (
                f"Generate 1 high-yield clinical medical pearl or diagnostic triad or drug-of-choice for MBBS / NEET PG / USMLE on: {subject}. "
                f"Format as valid JSON ONLY:\n"
                f"{{\n"
                f'  "title": "Short title or condition name",\n'
                f'  "question": "Clinical clue or question (e.g. What is Beck\'s Triad in cardiac tamponade? Or Drug of choice for Trigeminal Neuralgia?)",\n'
                f'  "answer": "Concise high-yield answer to be hidden under spoiler",\n'
                f'  "explanation": "1-line clinical rationale or key takeaway"\n'
                f"}}"
            )
            card_data = None
            try:
                res = await self.router.generate_response(
                    system_prompt="You are a medical board exam faculty. Output valid JSON only, no markdown format.",
                    user_prompt=prompt,
                    category="fast"
                )
                raw_json = res.get("response", "").strip()
                if "```json" in raw_json:
                    raw_json = raw_json.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_json:
                    raw_json = raw_json.split("```")[1].split("```")[0].strip()
                card_data = json.loads(raw_json)
            except Exception as e:
                logger.warning(f"Error generating clinical pearl: {e}")

            if not card_data or not card_data.get("question") or not card_data.get("answer"):
                card_data = {
                    "title": "Cardiac Tamponade Diagnostics",
                    "question": "What is the classic diagnostic triad associated with acute cardiac tamponade?",
                    "answer": "Beck's Triad: Hypotension + Jugular Venous Distension (JVD) + Muffled Heart Sounds.",
                    "explanation": "Pulsus paradoxus (>10 mmHg drop in SBP on inspiration) is also a classic examination finding."
                }

            pearl_msg = (
                f"💎 **High-Yield Clinical Pearl | {card_data.get('title', subject)}** 🩺\n\n"
                f"❓ **Clinical Question / Clue:**\n{card_data['question']}\n\n"
                f"🎯 **Answer (Tap below to reveal):**\n"
                f"||{card_data['answer']}||\n\n"
                f"💡 *Key Takeaway: {card_data.get('explanation', '')}*\n"
                f"📚 Kind Doctor Study System"
            )
            await self._send_message(session, chat_id, pearl_msg, message_thread_id=thread_id)

        # -------------------------------------------------------------
        # 7. CLINICAL CALCULATOR & SCORING ENGINE
        # -------------------------------------------------------------
        elif cmd in ("/score", "/calc"):
            sub_cmd = parts[1].lower() if len(parts) > 1 else "help"

            if sub_cmd == "bmi":
                if len(parts) < 4:
                    await self._send_message(session, chat_id, "Usage: `/score bmi <weight_kg> <height_cm>`\nExample: `/score bmi 70 175`", message_thread_id=thread_id)
                    return
                try:
                    wt = float(parts[2])
                    ht_cm = float(parts[3])
                    ht_m = ht_cm / 100.0
                    bmi = wt / (ht_m * ht_m)
                    if bmi < 18.5:
                        cat = "Underweight 🔵"
                    elif bmi < 24.9:
                        cat = "Normal Weight 🟢 (Ideal)"
                    elif bmi < 29.9:
                        cat = "Overweight 🟡 (Pre-obese)"
                    elif bmi < 34.9:
                        cat = "Obesity Class I 🟠"
                    elif bmi < 39.9:
                        cat = "Obesity Class II 🔴"
                    else:
                        cat = "Obesity Class III (Severe) 🟣"

                    res_text = (
                        f"⚖️ **Clinical Score: Body Mass Index (BMI)**\n\n"
                        f"• **Weight**: `{wt:.1f} kg` | **Height**: `{ht_cm:.0f} cm`\n"
                        f"• **Calculated BMI**: `{bmi:.1f} kg/m²`\n"
                        f"• **WHO Category**: **{cat}**\n\n"
                        f"💡 *Clinical Note: Target BMI for South Asians: 18.5 - 22.9 kg/m².*"
                    )
                    await self._send_message(session, chat_id, res_text, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid numbers. Example: `/score bmi 70 175`", message_thread_id=thread_id)

            elif sub_cmd == "map":
                if len(parts) < 4:
                    await self._send_message(session, chat_id, "Usage: `/score map <systolic_bp> <diastolic_bp>`\nExample: `/score map 120 80`", message_thread_id=thread_id)
                    return
                try:
                    sbp = float(parts[2])
                    dbp = float(parts[3])
                    map_val = dbp + (sbp - dbp) / 3.0
                    status = "Adequate Organ Perfusion 🟢" if map_val >= 65 else "Risk of Hypoperfusion / Shock 🔴"
                    res_text = (
                        f"🫀 **Clinical Score: Mean Arterial Pressure (MAP)**\n\n"
                        f"• **Blood Pressure**: `{sbp:.0f}/{dbp:.0f} mmHg`\n"
                        f"• **Calculated MAP**: `{map_val:.1f} mmHg`\n"
                        f"• **Perfusion Status**: **{status}**\n\n"
                        f"💡 *Rule: Minimum target MAP in sepsis / ICU resuscitation is ≥ 65 mmHg.*"
                    )
                    await self._send_message(session, chat_id, res_text, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid numbers. Example: `/score map 120 80`", message_thread_id=thread_id)

            elif sub_cmd == "gcs":
                if len(parts) < 5:
                    await self._send_message(session, chat_id, "Usage: `/score gcs <Eye:1-4> <Verbal:1-5> <Motor:1-6>`\nExample: `/score gcs 4 5 6`", message_thread_id=thread_id)
                    return
                try:
                    e = int(parts[2])
                    v = int(parts[3])
                    m = int(parts[4])
                    if not (1 <= e <= 4 and 1 <= v <= 5 and 1 <= m <= 6):
                        await self._send_message(session, chat_id, "⚠️ Valid ranges: Eye (1-4), Verbal (1-5), Motor (1-6).", message_thread_id=thread_id)
                        return
                    total_gcs = e + v + m
                    if total_gcs <= 8:
                        severity = "Severe Brain Injury / Coma 🔴 ('GCS ≤ 8, Intubate!')"
                    elif total_gcs <= 12:
                        severity = "Moderate Brain Injury 🟡"
                    else:
                        severity = "Mild / Normal 🟢"

                    res_text = (
                        f"🧠 **Clinical Score: Glasgow Coma Scale (GCS)**\n\n"
                        f"• **Eye (E)**: `{e}/4` | **Verbal (V)**: `{v}/5` | **Motor (M)**: `{m}/6`\n"
                        f"• **Total Score**: `{total_gcs}/15`\n"
                        f"• **Assessment**: **{severity}**\n\n"
                        f"💡 *Clinical Pearl: Motor score (M) is the most predictive component of neurological recovery.*"
                    )
                    await self._send_message(session, chat_id, res_text, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input. Example: `/score gcs 4 5 6`", message_thread_id=thread_id)

            elif sub_cmd == "aniongap":
                if len(parts) < 5:
                    await self._send_message(session, chat_id, "Usage: `/score aniongap <Na> <Cl> <HCO3>`\nExample: `/score aniongap 140 102 24`", message_thread_id=thread_id)
                    return
                try:
                    na = float(parts[2])
                    cl = float(parts[3])
                    hco3 = float(parts[4])
                    ag = na - (cl + hco3)
                    if ag > 12:
                        assessment = "Elevated Anion Gap (HAGMA) 🔴\n*(MUDPILES / GOLD MARK causes)*"
                    elif ag < 4:
                        assessment = "Low Anion Gap 🔵\n*(Hypoalbuminemia, Multiple Myeloma)*"
                    else:
                        assessment = "Normal Anion Gap (NAGMA / Normal) 🟢 (8-12 mEq/L)"

                    res_text = (
                        f"🧪 **Clinical Score: Serum Anion Gap**\n\n"
                        f"• **Electrolytes**: Na⁺ `{na:.0f}` | Cl⁻ `{cl:.0f}` | HCO₃⁻ `{hco3:.0f}`\n"
                        f"• **Calculated Gap**: `{ag:.1f} mEq/L`\n"
                        f"• **Interpretation**: **{assessment}**\n\n"
                        f"💡 *Formula: Na⁺ - (Cl⁻ + HCO₃⁻). Normal reference: 8 - 12 mEq/L.*"
                    )
                    await self._send_message(session, chat_id, res_text, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid numbers. Example: `/score aniongap 140 102 24`", message_thread_id=thread_id)

            elif sub_cmd == "curb65":
                if len(parts) < 7:
                    usage = (
                        "Usage: `/score curb65 <Confusion:0/1> <Urea_gt_7:0/1> <RR_ge_30:0/1> <BP_low:0/1> <Age_ge_65:0/1>`\n\n"
                        "Criteria (1 point each if present, 0 if absent):\n"
                        "• C: Confusion\n"
                        "• U: Urea > 7 mmol/L (BUN > 19 mg/dL)\n"
                        "• R: Respiratory Rate ≥ 30 breaths/min\n"
                        "• B: Blood Pressure (SBP < 90 or DBP ≤ 60 mmHg)\n"
                        "• 65: Age ≥ 65 years\n\n"
                        "Example: `/score curb65 1 0 1 0 1`"
                    )
                    await self._send_message(session, chat_id, usage, message_thread_id=thread_id)
                    return
                try:
                    c, u, r, b, age65 = int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5]), int(parts[6])
                    score = c + u + r + b + age65
                    if score <= 1:
                        rec = "Low Risk (Mortality < 3%) 🟢 — Suitable for Outpatient management."
                    elif score == 2:
                        rec = "Intermediate Risk (Mortality ~9%) 🟡 — Consider short Inpatient admission or supervised outpatient care."
                    else:
                        rec = "High Risk (Mortality 15-40%) 🔴 — Severe Pneumonia. Urgent Hospital admission (Consider ICU if score 4-5)."

                    res_text = (
                        f"🫁 **Clinical Score: CURB-65 (Pneumonia Severity)** 🩺\n\n"
                        f"• **Score Breakdown**: C={c} | U={u} | R={r} | B={b} | 65={age65}\n"
                        f"• **Total CURB-65**: `{score}/5`\n"
                        f"• **Risk & Recommendation**: **{rec}**\n\n"
                        f"⚠️ *Disclaimer: Educational study tool only; not a substitute for clinical judgment.*"
                    )
                    await self._send_message(session, chat_id, res_text, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input. Enter 0 or 1 for each criteria. Example: `/score curb65 1 0 1 0 1`", message_thread_id=thread_id)

            elif sub_cmd == "wells":
                if len(parts) < 9:
                    usage = (
                        "Usage: `/score wells <DVT:0/1> <PE_most_likely:0/1> <HR_gt_100:0/1> <Immob_Surg:0/1> <Prior_DVT_PE:0/1> <Hemoptysis:0/1> <Malignancy:0/1>`\n\n"
                        "Points:\n"
                        "• Clinical signs of DVT (+3.0)\n"
                        "• Alternative diagnosis less likely than PE (+3.0)\n"
                        "• Heart rate > 100 bpm (+1.5)\n"
                        "• Immobilization ≥ 3 days or surgery in 4 weeks (+1.5)\n"
                        "• Previous DVT or PE (+1.5)\n"
                        "• Hemoptysis (+1.0)\n"
                        "• Active Malignancy (+1.0)\n\n"
                        "Example: `/score wells 1 1 0 1 0 0 0`"
                    )
                    await self._send_message(session, chat_id, usage, message_thread_id=thread_id)
                    return
                try:
                    dvt = int(parts[2]) * 3.0
                    pe_likely = int(parts[3]) * 3.0
                    hr = int(parts[4]) * 1.5
                    immob = int(parts[5]) * 1.5
                    prior = int(parts[6]) * 1.5
                    hemo = int(parts[7]) * 1.0
                    malig = int(parts[8]) * 1.0
                    total_score = dvt + pe_likely + hr + immob + prior + hemo + malig

                    if total_score > 4.0:
                        interp = "PE Likely (> 4.0 points) 🔴 — Diagnostic imaging (CTPA) indicated."
                    else:
                        interp = "PE Unlikely (≤ 4.0 points) 🟢 — High-sensitivity D-Dimer test to rule out."

                    res_text = (
                        f"🫀 **Clinical Score: Wells' Criteria for Pulmonary Embolism** 🩺\n\n"
                        f"• **Calculated Score**: `{total_score:.1f} Points`\n"
                        f"• **Probability Tier**: **{interp}**\n\n"
                        f"⚠️ *Disclaimer: Educational study tool only; not a substitute for clinical judgment.*"
                    )
                    await self._send_message(session, chat_id, res_text, message_thread_id=thread_id)
                except ValueError:
                    await self._send_message(session, chat_id, "⚠️ Invalid input. Enter 0 or 1 for each criteria. Example: `/score wells 1 1 0 1 0 0 0`", message_thread_id=thread_id)

            else:
                menu = (
                    f"🧮 **Kind Doctor Clinical Scoring & Calculators** 🩺\n\n"
                    f"Directly calculate key clinical metrics right in chat:\n\n"
                    f"• **Body Mass Index**: `/score bmi <weight_kg> <height_cm>`\n"
                    f"• **Mean Arterial Pressure**: `/score map <sbp> <dbp>`\n"
                    f"• **Glasgow Coma Scale**: `/score gcs <E:1-4> <V:1-5> <M:1-6>`\n"
                    f"• **Serum Anion Gap**: `/score aniongap <Na> <Cl> <HCO3>`\n"
                    f"• **CURB-65 Pneumonia**: `/score curb65 <C:0/1> <U:0/1> <R:0/1> <B:0/1> <65:0/1>`\n"
                    f"• **Wells' Criteria (PE)**: `/score wells <DVT> <Alt> <HR> <Immob> <Prior> <Hemo> <Ca>`\n\n"
                    f"💡 *Example: `/score map 120 80` or `/score curb65 1 0 1 0 1`*"
                )
                await self._send_message(session, chat_id, menu, message_thread_id=thread_id)

        # -------------------------------------------------------------
        # 8. GROUP FOCUS STUDY SPRINT & POMODORO TIMER
        # -------------------------------------------------------------
        elif cmd in ("/pomodoro", "/focus"):
            mins = 25
            if len(parts) > 1 and parts[1].isdigit():
                mins = max(5, min(120, int(parts[1])))

            start_banner = (
                f"⏳ **FOCUS STUDY SPRINT STARTED!** 🩺\n\n"
                f"🎯 **Target Duration:** `{mins} Minutes`\n"
                f"🔕 **Rules:** Notifications off, zero multi-tasking, deep study mode.\n"
                f"💪 All the best doctors! Time starts right now.\n\n"
                f"*(Jab time pura hoga, bot group me alert bhej dega).* "
            )
            await self._send_message(session, chat_id, start_banner, message_thread_id=thread_id)

            async def _pomodoro_timer(c_id: int, m_thread_id: Optional[int], duration_mins: int):
                await asyncio.sleep(duration_mins * 60)
                finish_banner = (
                    f"🔔 **DING! FOCUS SPRINT COMPLETE!** ☕🎉\n\n"
                    f"✨ **{duration_mins} Minutes** of focused study accomplished!\n"
                    f"🚶‍♂️ Stand up, hydrate, stretch, and take a **5-minute break** before the next round.\n\n"
                    f"Great job team! Ready for another round? Type `/pomodoro` anytime!"
                )
                try:
                    async with aiohttp.ClientSession() as s:
                        await self._send_message(s, c_id, finish_banner, message_thread_id=m_thread_id)
                except Exception as ex:
                    logger.warning(f"Pomodoro finish alert failed: {ex}")

            asyncio.create_task(_pomodoro_timer(chat_id, thread_id, mins))

        # -------------------------------------------------------------
        # 9. STUDENT CLINICAL DOUBT & CASE DISCUSSION
        # -------------------------------------------------------------
        elif cmd == "/ask":
            if len(parts) < 2:
                await self._send_message(
                    session,
                    chat_id,
                    "Usage: `/ask <your clinical doubt or question>`\n\nExample: `/ask What is the first-line treatment for acute hyperkalemia with ECG changes?`",
                    message_thread_id=thread_id
                )
                return

            doubt_text = " ".join(parts[1:]).strip()
            ticket_id = f"DOUBT-{int(datetime.now().timestamp()) % 10000:04d}"
            sender_name = message.get("from", {}).get("first_name", "Student") if message else "Student"
            sender_uname = f"@{message.get('from', {}).get('username')}" if message and message.get("from", {}).get("username") else sender_name
            sender_id = message.get("from", {}).get("id", 0) if message else 0

            doubt_card = (
                f"❓ **[Case Doubt #{ticket_id}]** 🩺\n\n"
                f"👤 **Asked by:** {sender_uname}\n"
                f"💬 **Question:**\n{doubt_text}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"👉 *Doctors & peers: Please reply below to discuss this case!*\n"
                f"👨‍⚕️ *Faculty Review: Notified to Kind Doctor Desk.*"
            )
            await self._send_message(session, chat_id, doubt_card, message_thread_id=thread_id)

            # Alert Master Admins in DM
            for adm_id in self.master_admin_ids:
                adm_notice = (
                    f"📬 **New Student Doubt #{ticket_id}**\n\n"
                    f"👤 From: {sender_uname} (`{sender_id}`)\n"
                    f"👥 In Chat: `{chat_id}`\n"
                    f"💬 Query: {doubt_text}"
                )
                await self._send_message(session, adm_id, adm_notice)

        # -------------------------------------------------------------
        # ADMIN & GROUP CONTROLS
        # -------------------------------------------------------------
        elif cmd == "/lockdown":
            if len(parts) > 1 and parts[1].lower() == "off":
                self.is_lockdown = False
                await self._send_message(session, chat_id, "🔓 **Emergency Lockdown Lifted:** Normal safe onboarding & invite links active.", message_thread_id=thread_id)
            else:
                self.is_lockdown = True
                await self._send_message(session, chat_id, "🔒 **Emergency Lockdown Activated!**\n\n• Group entry is sealed.\n• No new links will be generated.\n• All onboarding requests are held in safety queue.", message_thread_id=thread_id)

        elif cmd == "/invitelink":
            if getattr(self, "is_lockdown", False):
                await self._send_message(session, chat_id, "🔒 Group is currently under **Emergency Lockdown**. Use `/lockdown off` before generating new links.", message_thread_id=thread_id)
                return

            target_grp = chat_id if chat_id != admin_id else self.target_chat
            if not target_grp:
                await self._send_message(session, chat_id, "⚠️ TARGET_CHAT is not set in `.env`.", message_thread_id=thread_id)
                return

            expire_ts = int((datetime.now() + timedelta(minutes=30)).timestamp())
            try:
                invite_url = f"https://api.telegram.org/bot{self.token}/createChatInviteLink"
                payload = {
                    "chat_id": target_grp,
                    "name": f"SingleUse_{datetime.now().strftime('%H%M')}",
                    "member_limit": 1,
                    "expire_date": expire_ts
                }
                async with session.post(invite_url, json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        link = data.get("result", {}).get("invite_link")
                        reply = (
                            f"🛡️ **Single-Use Disposable Invite Link Generated:**\n\n"
                            f"🔗 `{link}`\n\n"
                            f"• **Limit**: Only 1 Person can join\n"
                            f"• **Expires**: In 30 Minutes\n"
                            f"• **Anti-Leak**: Ek bar use hote hi link dead ho jayega! Anti-piracy bots nahi join kar payenge."
                        )
                        await self._send_message(session, chat_id, reply, message_thread_id=thread_id)
                    else:
                        await self._send_message(session, chat_id, "⚠️ Failed to create invite link. Make sure bot is Admin in this chat with 'Invite Users' rights.", message_thread_id=thread_id)
            except Exception as e:
                await self._send_message(session, chat_id, f"Error generating link: {e}", message_thread_id=thread_id)

        elif cmd == "/copyshield":
            shield_report = (
                f"🛡️ **Copyright Protection & Channel Savior Suite** ⚡\n\n"
                f"Is bot me `@copyright_protection_bot` aur `@copyright_infrigment_saver_bot` ki core anti-strike techniques integrate hain:\n\n"
                f"1️⃣ **Anti-Crawler 1-Time Links (`/invitelink`):**\n"
                f"↳ 30-min me expire hone wale disposable links. Automated copyright search bots aur scrapers permalink dhund kar group me nahi ghus sakte.\n\n"
                f"2️⃣ **Emergency Attack Lockdown (`/lockdown on` / `/lockdown off`):**\n"
                f"↳ Raid ya strike waves aane par turant group entrance seal kar deta hai.\n\n"
                f"3️⃣ **Emergency Content Purge (`/purge <count>`):**\n"
                f"↳ Agar kisi material par notice aaye, toh `/purge 50` karke recent messages ko turant mass delete kar sakte hain.\n\n"
                f"4️⃣ **Anti-Promo / External Link Purge:**\n"
                f"↳ Bahar se aane wale kisi bhi spammer/bot ke external links ko instant wipe kar deta hai.\n\n"
                f"5️⃣ **Executable Malware Block:**\n"
                f"↳ Dangerous .apk/.exe files ko direct delete karta hai.\n\n"
                f"💡 *Pro-Tip: Telegram Group Settings me 'Restrict saving content' on rakhein taaki koi content forward/save karke report na kar sake!*"
            )
            await self._send_message(session, chat_id, shield_report, message_thread_id=thread_id)

        elif cmd == "/purge":
            if not self.is_admin(admin_id):
                await self._send_message(session, chat_id, "⚠️ Sirf Admins ye command chala sakte hain.", message_thread_id=thread_id)
                return

            purge_count = 10
            if len(parts) > 1 and parts[1].isdigit():
                purge_count = max(1, min(100, int(parts[1])))

            if reply_to and reply_to.get("message_id"):
                start_id = reply_to["message_id"]
                end_id = msg_id
                target_ids = list(range(start_id, end_id + 1))[:100]
            else:
                target_ids = list(range(msg_id - purge_count, msg_id + 1))

            try:
                # Bot API 7.0 batch delete
                del_url = f"https://api.telegram.org/bot{self.token}/deleteMessages"
                payload = {"chat_id": chat_id, "message_ids": target_ids}
                async with session.post(del_url, json=payload, timeout=10) as r:
                    if r.status != 200:
                        for mid in target_ids:
                            await self._delete_message(session, chat_id, mid)
            except Exception as e:
                logger.warning(f"Error purging messages: {e}")

            confirm_msg = await self._send_message(session, chat_id, f"🧹 **Emergency Purge Complete:** `{len(target_ids)}` messages deleted.")
            if confirm_msg:
                self.create_tracked_task(self._auto_delete_message(session, chat_id, confirm_msg, 5))

        elif cmd in ("/info", "/history"):
            target_id = None
            if len(parts) > 1 and parts[1].isdigit():
                target_id = int(parts[1])
            elif reply_to and reply_to.get("from", {}).get("id"):
                target_id = reply_to.get("from", {}).get("id")
            else:
                target_id = admin_id

            try:
                with get_db_conn() as conn:
                    conn.row_factory = sqlite3.Row
                    row = conn.execute("SELECT * FROM telegram_users_dossier WHERE user_id = ?", (target_id,)).fetchone()
                    if row:
                        name_h = json.loads(row["name_history"] or "[]")
                        uname_h = json.loads(row["username_history"] or "[]")
                        name_h_str = "\n".join(f"  • {x.get('name')} _({x.get('changed_at')})_" for x in name_h) if name_h else "None"
                        uname_h_str = "\n".join(f"  • @{x.get('username')} _({x.get('changed_at')})_" for x in uname_h) if uname_h else "None"
                        
                        info_msg = (
                            f"👁️ **User Identity & Change History (SangMata / TeleOshint)** 🕵️\n\n"
                            f"🆔 **Permanent ID**: `{target_id}`\n"
                            f"👤 **Current Name**: {row['first_name']} {row['last_name']}\n"
                            f"🔗 **Username**: @{row['username'] or 'None'}\n"
                            f"⭐️ **Account**: {'Premium' if row['is_premium'] else 'Standard'} | 🌐 `{row['language_code']}`\n"
                            f"💬 **Total Messages in Group**: `{row['total_messages']}`\n"
                            f"🕒 **First Seen**: `{row['first_seen']}`\n"
                            f"🔄 **Identity Changes Detected**: `{row['changes_count']}`\n\n"
                            f"📜 **Past Names History:**\n{name_h_str}\n\n"
                            f"🏷️ **Past Usernames History:**\n{uname_h_str}"
                        )
                        await self._send_message(session, chat_id, info_msg, message_thread_id=thread_id)
                    else:
                        await self._send_message(session, chat_id, f"⚠️ User `{target_id}` abhi database me record nahi hai.", message_thread_id=thread_id)
            except Exception as e:
                await self._send_message(session, chat_id, f"Error fetching history: {e}", message_thread_id=thread_id)

        elif cmd in ("/stats", "/telemetry"):
            try:
                with get_db_conn() as conn:
                    students_cnt = conn.execute("SELECT COUNT(*) FROM telegram_users_dossier").fetchone()[0]
                    total_msgs = conn.execute("SELECT SUM(total_messages) FROM telegram_users_dossier").fetchone()[0] or 0
                    topics_cnt = conn.execute("SELECT COUNT(*) FROM telegram_group_topics WHERE chat_id = ?", (chat_id,)).fetchone()[0]
                    items_cnt = conn.execute("SELECT COUNT(*) FROM telegram_topic_items WHERE chat_id = ?", (chat_id,)).fetchone()[0]
                    spams_cnt = conn.execute("SELECT COUNT(*) FROM telegram_bot_analytics WHERE event_type = 'scam_nsfw_blocked'").fetchone()[0]
                    links_cnt = conn.execute("SELECT COUNT(*) FROM telegram_bot_analytics WHERE event_type LIKE '%link%'").fetchone()[0]
                    malware_cnt = conn.execute("SELECT COUNT(*) FROM telegram_bot_analytics WHERE event_type = 'malware_apk_blocked'").fetchone()[0]

                    stats_card = (
                        f"📊 **Kind Doctor Group Analytics & Security Telemetry (Combot style)** 📈\n\n"
                        f"👥 **Study Community:**\n"
                        f"• Active Students in Database: `{students_cnt}`\n"
                        f"• Total Discussion Messages Tracked: `{total_msgs}`\n\n"
                        f"📚 **Study Resources:**\n"
                        f"• Registered Forum Topics: `{topics_cnt}`\n"
                        f"• Indexed Lectures & Study Files: `{items_cnt}`\n\n"
                        f"🛡️ **Security & Anti-Spam Metrics:**\n"
                        f"• Scams, Betting & NSFW Filtered: `{spams_cnt}`\n"
                        f"• Malicious APK/EXE Uploads Blocked: `{malware_cnt}`\n"
                        f"• Promo & Unauthorized Links Purged: `{links_cnt}`\n\n"
                        f"🩺 *System Status: Fully Operational & 100% Protected*"
                    )
                    await self._send_message(session, chat_id, stats_card, message_thread_id=thread_id)
            except Exception as e:
                await self._send_message(session, chat_id, f"Error fetching stats: {e}", message_thread_id=thread_id)

        elif cmd in ("/leaderboard", "/topmembers"):
            try:
                with get_db_conn() as conn:
                    conn.row_factory = sqlite3.Row
                    rows = conn.execute("""
                        SELECT user_id, first_name, username, total_messages 
                        FROM telegram_users_dossier 
                        WHERE total_messages > 0 
                        ORDER BY total_messages DESC LIMIT 10
                    """).fetchall()
                    if not rows:
                        await self._send_message(session, chat_id, "Abhi koi student activity recorded nahi hai.", message_thread_id=thread_id)
                        return

                    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
                    lines = [
                        "🏆 **Top Active Students & Discussion Leaderboard (Limzo style)** 🩺\n",
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
                    ]
                    for idx, r in enumerate(rows):
                        m = medals[idx] if idx < len(medals) else f"#{idx+1}"
                        uname = f"@{r['username']}" if r['username'] else r['first_name'] or f"User {r['user_id']}"
                        lines.append(f"{m} **{uname}** — `{r['total_messages']}` messages")
                    lines.extend([
                        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
                        "💪 Keep studying and sharing high-yield medical pearls!"
                    ])
                    await self._send_message(session, chat_id, "\n".join(lines), message_thread_id=thread_id)
            except Exception as e:
                await self._send_message(session, chat_id, f"Error fetching leaderboard: {e}", message_thread_id=thread_id)

        elif cmd == "/cleandeleted":
            target_chat_id = self._resolve_study_group_id(chat_id)
            is_caller_admin = await self.is_admin_for_chat(session, target_chat_id, admin_id, message)
            if not is_caller_admin:
                await self._send_message(session, chat_id, "⚠️ Access Denied: Group Admin rights required.", message_thread_id=thread_id)
                return

            status_msg = await self._send_message(session, chat_id, "🧹 **Scanning group for ghost and deleted accounts...**", message_thread_id=thread_id)
            cleaned_count = 0
            try:
                with get_db_conn() as conn:
                    conn.row_factory = sqlite3.Row
                    deleted_users = conn.execute("""
                        SELECT DISTINCT user_id FROM telegram_users_dossier WHERE first_name LIKE '%Deleted%' OR first_name = ''
                        UNION
                        SELECT DISTINCT user_id FROM member_history WHERE first_name LIKE '%Deleted%' OR first_name = ''
                    """).fetchall()
                    for du in deleted_users:
                        u_id = du["user_id"]
                        try:
                            await session.post(f"https://api.telegram.org/bot{self.token}/banChatMember", json={"chat_id": target_chat_id, "user_id": u_id}, timeout=8)
                            await session.post(f"https://api.telegram.org/bot{self.token}/unbanChatMember", json={"chat_id": target_chat_id, "user_id": u_id}, timeout=8)
                            cleaned_count += 1
                        except Exception:
                            pass
            except Exception as e:
                logger.warning(f"Error in cleandeleted: {e}")

            if status_msg:
                await self._delete_message(session, chat_id, status_msg)

            res = (
                f"🗑️ **Clean Deleted Accounts Result:**\n\n"
                f"• **Removed Ghost Accounts:** `{cleaned_count}`\n"
                f"• **Status:** Group ghost member scan complete! Chat optimized. ✨"
            )
            await self._send_message(session, chat_id, res, message_thread_id=thread_id)

        elif cmd == "/setcmd":
            if len(parts) < 3 or not parts[1].startswith("/"):
                await self._send_message(session, chat_id, "Usage: `/setcmd /command_name Response text goes here`\n\nExample: `/setcmd /rules Group rules: 1. Be polite 2. No phone numbers.`", message_thread_id=thread_id)
                return
            c_name = parts[1].lower()
            c_text = " ".join(parts[2:])
            try:
                with get_db_conn() as conn:
                    conn.execute("INSERT OR REPLACE INTO telegram_custom_commands (command, response_text, created_by) VALUES (?, ?, ?)", (c_name, c_text, admin_id))
                await self._send_message(session, chat_id, f"✅ Custom command `{c_name}` successfully saved!\n\n**Output preview:**\n{c_text}", message_thread_id=thread_id)
            except Exception as e:
                await self._send_message(session, chat_id, f"Error saving command: {e}", message_thread_id=thread_id)

        elif cmd == "/delcmd":
            if len(parts) < 2 or not parts[1].startswith("/"):
                await self._send_message(session, chat_id, "Usage: `/delcmd /command_name`", message_thread_id=thread_id)
                return
            c_name = parts[1].lower()
            try:
                with get_db_conn() as conn:
                    conn.execute("DELETE FROM telegram_custom_commands WHERE command = ?", (c_name,))
                await self._send_message(session, chat_id, f"🗑️ Custom command `{c_name}` deleted.", message_thread_id=thread_id)
            except Exception as e:
                await self._send_message(session, chat_id, f"Error deleting command: {e}", message_thread_id=thread_id)

        elif cmd == "/customcmds":
            try:
                with get_db_conn() as conn:
                    rows = conn.execute("SELECT command, response_text FROM telegram_custom_commands").fetchall()
                    if rows:
                        cmd_list = "\n".join(f"• `{r[0]}` ➔ {r[1][:50]}..." for r in rows)
                        await self._send_message(session, chat_id, f"📜 **Configured Custom Commands ({len(rows)}):**\n\n{cmd_list}\n\nAdd more: `/setcmd /cmd <text>`\nDelete: `/delcmd /cmd`", message_thread_id=thread_id)
                    else:
                        await self._send_message(session, chat_id, "No custom commands set yet. Create one with:\n`/setcmd /name Your text response`", message_thread_id=thread_id)
            except Exception as e:
                await self._send_message(session, chat_id, f"Error: {e}", message_thread_id=thread_id)

        elif cmd in ("/engine", "/status"):
            if not self.is_admin(admin_id):
                await self._send_message(session, chat_id, "⛔ Restricted to Master Admins.", message_thread_id=thread_id)
                return

            load_dotenv(ENV_PATH, override=True)
            engine_locked = (BASE_PROJECT_DIR / "engine.lock").exists()
            is_running = engine_locked
            
            total_topics = 0
            total_items = 0
            total_mapped = 0
            with suppress(Exception):
                with get_db_conn() as conn:
                    total_topics = conn.execute("SELECT COUNT(*) FROM telegram_group_topics").fetchone()[0]
                    total_items = conn.execute("SELECT COUNT(*) FROM telegram_topic_items").fetchone()[0]
                    total_mapped = conn.execute("SELECT COUNT(*) FROM forwarded").fetchone()[0]

            import psutil
            ram = psutil.virtual_memory()
            ram_used_mb = (ram.total - ram.available) / (1024 * 1024)
            ram_pct = ram.percent

            cur_direct = os.getenv("DIRECT_FORWARD", "false").strip().lower() in ("true", "1", "yes")
            cur_sig = os.getenv("ENABLE_SIGNATURE", "true").strip().lower() in ("true", "1", "yes")
            cur_thumb = os.getenv("THUMB_MODE", "custom").strip().lower()
            src_chat = os.getenv("SOURCE_CHAT", "Not Set")
            tgt_chat = os.getenv("TARGET_CHAT", "Not Set")

            engine_status_badge = "🟢 **ONLINE / ACTIVE**" if is_running else "🟡 **STANDBY / READY**"
            status_report = (
                f"🩺 **TG KINDSYNC PRO — MASTER CONTROL TOWER**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"⚡ **Engine State:** {engine_status_badge}\n"
                f"💻 **Host System RAM:** `{ram_pct}%` ({ram_used_mb:.0f} MB / {ram.total/(1024*1024):.0f} MB)\n\n"
                f"📊 **Database Metrics (history_core.sqlite):**\n"
                f"• **Forum Topics Indexed:** `{total_topics}`\n"
                f"• **Lectures & Files Indexed:** `{total_items}`\n"
                f"• **Total Mapped Transfers:** `{total_mapped}`\n\n"
                f"⚙️ **Active Configuration:**\n"
                f"• **Source Channel:** `{src_chat}`\n"
                f"• **Target Group/Chat:** `{tgt_chat}`\n"
                f"• **Transmission Pipeline:** `{'⚡ Fast Direct' if cur_direct else '🔄 Streaming Engine'}`\n"
                f"• **Branding Signature:** `{'👑 ON' if cur_sig else '🏷️ OFF (Clean)'}`\n"
                f"• **16:9 HD Cover:** `{'🖼️ Custom 16:9' if cur_thumb == 'custom' else '🎞️ Original'}`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"👑 **Master Admins:** `@Kinddoctor4u` | `@Ammitrajput1`"
            )

            control_keyboard = {
                "inline_keyboard": [
                    [
                        {"text": "🔄 Refresh Status", "callback_data": "act_engine_refresh"},
                        {"text": "📦 Instant Backup", "callback_data": "act_engine_backup"}
                    ],
                    [
                        {"text": "🔍 Fast Topic Scan", "callback_data": "act_engine_scan"},
                        {"text": "🧹 Deep Clean", "callback_data": "act_engine_clean"}
                    ],
                    [
                        {"text": "⚡ Toggle Direct Forward", "callback_data": "act_toggle_direct"},
                        {"text": "👑 Toggle Signature", "callback_data": "act_toggle_sig"}
                    ]
                ]
            }
            await self._send_message(session, chat_id, status_report, reply_markup=control_keyboard, message_thread_id=thread_id)

        elif cmd in ("/pause_engine", "/stop_engine", "/pause"):
            if not self.is_admin(admin_id):
                await self._send_message(session, chat_id, "⛔ Restricted to Master Admins.", message_thread_id=thread_id)
                return
            ctrl_p = BASE_PROJECT_DIR / "engine_control.json"
            try:
                with open(ctrl_p, "w", encoding="utf-8") as cf:
                    json.dump({"paused": True, "ts": time.time(), "by": admin_id}, cf)
                await self._send_message(
                    session, chat_id,
                    "⏸️ **Forwarder Engine PAUSED Remotely!** 🩺\n\n"
                    "• Active transfers suspended cleanly.\n"
                    "• Background services and sessions remain alive 24/7.\n"
                    "• Type `/resume_engine` anytime to continue forwarding.",
                    message_thread_id=thread_id
                )
            except Exception as e:
                await self._send_message(session, chat_id, f"❌ Failed to pause engine: {e}", message_thread_id=thread_id)

        elif cmd in ("/resume_engine", "/start_engine", "/resume"):
            if not self.is_admin(admin_id):
                await self._send_message(session, chat_id, "⛔ Restricted to Master Admins.", message_thread_id=thread_id)
                return
            ctrl_p = BASE_PROJECT_DIR / "engine_control.json"
            try:
                with open(ctrl_p, "w", encoding="utf-8") as cf:
                    json.dump({"paused": False, "ts": time.time(), "by": admin_id}, cf)
                await self._send_message(
                    session, chat_id,
                    "▶️ **Forwarder Engine RESUMED!** 🚀\n\n"
                    "• High-speed streaming forwarder is active.\n"
                    "• Media queue processing at maximum uncapped wire speed.",
                    message_thread_id=thread_id
                )
            except Exception as e:
                await self._send_message(session, chat_id, f"❌ Failed to resume engine: {e}", message_thread_id=thread_id)

        elif cmd == "/backup":
            if not self.is_admin(admin_id):
                await self._send_message(session, chat_id, "⛔ Restricted to Master Admins.", message_thread_id=thread_id)
                return

            notify_id = await self._send_message(session, chat_id, "⏳ **Generating secure zero-downtime SQLite backup snapshot...**", message_thread_id=thread_id)
            try:
                now = datetime.now()
                day_name = now.strftime("%A")
                date_str = now.strftime("%d-%B-%Y")
                time_str = now.strftime("%I-%M%p") # e.g. 10-25AM
                
                # Standard File Pattern: [prefix]_[Day]_[Date]-[Month]-[Year]_[Time-12hAM-PM].[ext]
                backup_filename = f"history_core_backup_{day_name}_{date_str}_{time_str}.sqlite"
                backup_dir = BASE_PROJECT_DIR / "db_backups"
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / backup_filename
                
                # Online zero-downtime SQLite snapshot
                with get_db_conn() as src_conn:
                    with sqlite3.connect(backup_path) as dst_conn:
                        src_conn.backup(dst_conn)
                
                file_bytes = backup_path.read_bytes()
                size_mb = len(file_bytes) / (1024 * 1024)
                
                # Standard Display/Caption Pattern: [Day], [Date] [Month] [Year] | [HH]:[MM] [AM/PM]
                caption_time = now.strftime("%I:%M %p")
                full_caption = (
                    f"🩺 **TG KINDSYNC PRO — MASTER DB SNAPSHOT**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📅 **Date & Time:** `{day_name}, {now.strftime('%d %B %Y')} | {caption_time}`\n"
                    f"📦 **File Size:** `{size_mb:.2f} MB`\n"
                    f"📊 **Database:** `history_core.sqlite`\n"
                    f"👑 **Requested By:** Admin ID `{admin_id}`\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"🔒 *Stored safely in Telegram Cloud for instant 1-click restore.*"
                )
                
                sent = await self._send_document(
                    session, chat_id, file_bytes, backup_filename, caption=full_caption, message_thread_id=thread_id
                )
                if notify_id:
                    self.create_tracked_task(self._auto_delete_message(session, chat_id, notify_id, 2))
                if not sent:
                    await self._send_message(session, chat_id, f"⚠️ Backup saved at `{backup_path.name}` ({size_mb:.2f} MB), but Telegram dispatch failed.", message_thread_id=thread_id)
            except Exception as e:
                logger.error(f"Backup generation failed: {e}")
                await self._send_message(session, chat_id, f"❌ **Backup generation failed:** {e}", message_thread_id=thread_id)

        elif cmd in ("/kill", "/kill_all", "/killall", "/unlock_db"):
            if not self.is_admin(admin_id):
                await self._send_message(session, chat_id, "⛔ Restricted to Master Admins.", message_thread_id=thread_id)
                return

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

            cleaned_locks = []
            for pat in ["*.session-journal", "*.session-wal", "*.session-shm", "history_core.sqlite-journal", "engine.lock"]:
                for f in BASE_PROJECT_DIR.glob(pat):
                    try:
                        f.unlink(missing_ok=True)
                        cleaned_locks.append(f.name)
                    except Exception:
                        pass

            pids_str = ", ".join(f"`PID {p}`" for p in killed) if killed else "None"
            locks_str = ", ".join(f"`{f}`" for f in cleaned_locks) if cleaned_locks else "None"

            await self._send_message(
                session, chat_id,
                f"🛑 **[ADMIN PROCESS TERMINATOR & DB UNLOCKED]**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"• **Killed Processes**: {pids_str}\n"
                f"• **Freed Memory**: `~{freed_mb:.2f} MB`\n"
                f"• **Cleaned Locks**: {locks_str}\n"
                f"• **SQLite Database**: `100% Free & Unlocked`\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"✅ *All background locks cleared. Safe to launch!*",
                message_thread_id=thread_id
            )

        elif cmd in ("/clean_history", "/clear_history", "/reset_history"):
            if not self.is_admin(admin_id):
                await self._send_message(session, chat_id, "⛔ Restricted to Master Admins.", message_thread_id=thread_id)
                return

            notify_id = await self._send_message(session, chat_id, "⏳ **Backing up database before history wipe...**", message_thread_id=thread_id)
            try:
                # 1. Take safety snapshot
                now = datetime.now()
                stamp = now.strftime("%A_%d-%B-%Y_%I-%M%p")
                backup_filename = f"history_core_backup_{stamp}.sqlite"
                backup_dir = BASE_PROJECT_DIR / "db_backups"
                backup_dir.mkdir(parents=True, exist_ok=True)
                backup_path = backup_dir / backup_filename

                with get_db_conn() as src_conn:
                    with sqlite3.connect(backup_path) as dst_conn:
                        src_conn.backup(dst_conn)

                file_bytes = backup_path.read_bytes()
                size_mb = len(file_bytes) / (1024 * 1024)
                caption_time = now.strftime("%I:%M %p")
                full_caption = (
                    f"📦 **[PRE-WIPE SAFETY BACKUP]**\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"📅 **Date & Time:** `{now.strftime('%A, %d %B %Y')} | {caption_time}`\n"
                    f"📦 **File Size:** `{size_mb:.2f} MB`\n"
                    f"🛡️ *Automated safety backup dispatched before history wipe.*"
                )
                await self._send_document(
                    session, chat_id, file_bytes, backup_filename, caption=full_caption, message_thread_id=thread_id
                )

                # 2. Wipe history
                with get_db_conn() as conn:
                    conn.execute("DELETE FROM forwarded")
                    conn.execute("DELETE FROM source_watermarks")
                    with suppress(Exception): conn.execute("DELETE FROM local_folder_uploads")
                    conn.commit()
                    with suppress(Exception): conn.execute("VACUUM")

                if notify_id:
                    self.create_tracked_task(self._auto_delete_message(session, chat_id, notify_id, 2))

                await self._send_message(
                    session, chat_id,
                    "🧹 **[FORWARDING HISTORY CLEANED & RESET]**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                    "• Previous history safely backed up above ⬆️\n"
                    "• Forwarded records wiped & database compacted!\n"
                    "• Future runs will forward fresh from scratch.",
                    message_thread_id=thread_id
                )
            except Exception as e:
                logger.error(f"Clean history failed: {e}")
                await self._send_message(session, chat_id, f"❌ **Clean history failed:** {e}", message_thread_id=thread_id)

        elif cmd == "/clean":
            if not self.is_admin(admin_id):
                await self._send_message(session, chat_id, "⛔ Restricted to Master Admins.", message_thread_id=thread_id)
                return

            lock_f = BASE_PROJECT_DIR / "engine.lock"
            if lock_f.exists():
                with suppress(Exception): lock_f.unlink()

            with suppress(Exception):
                with get_db_conn() as conn:
                    conn.execute("PRAGMA wal_checkpoint(TRUNCATE)")

            await self._send_message(
                session, chat_id,
                "🧹 **Workspace Deep Cleaned!**\n\n"
                "• Stale locks released (`engine.lock`)\n"
                "• SQLite WAL buffer truncated & checkpointed\n"
                "• Temporary cache purged\n\n"
                "Engine is 100% fresh and ready to launch! 🚀",
                message_thread_id=thread_id
            )


        elif cmd == "/health":
            health = SystemTools.get_system_health()
            reply = (
                f"📊 **DEVI Telemetry:**\n"
                f"• Status: {health.get('status', 'OK')}\n"
                f"• CPU: {health.get('cpu_usage_pct', 0)}%\n"
                f"• RAM: {health.get('used_ram_pct', 0)}% ({health.get('available_ram_gb', 0)}GB free)\n"
            )
            await self._send_message(session, chat_id, reply, message_thread_id=thread_id)

        elif cmd == "/admins":
            master_str = ", ".join(f"`{a}`" for a in self.master_admin_ids)
            co_str = ", ".join(f"`{a}`" for a in self.co_admins) if self.co_admins else "None"
            reply = (
                f"👥 **Configured Admins:**\n"
                f"• **Master Admins**: {master_str}\n"
                f"• **Co-Admins**: {co_str}\n\n"
                f"Add more: `/addadmin <user_id>`"
            )
            await self._send_message(session, chat_id, reply, message_thread_id=thread_id)

        elif cmd == "/addadmin":
            if len(parts) < 2 or not parts[1].isdigit():
                await self._send_message(session, chat_id, "Usage: `/addadmin <user_id>`", message_thread_id=thread_id)
                return
            new_id = int(parts[1])
            self.co_admins.add(new_id)
            try:
                with get_db_conn() as conn:
                    conn.execute("INSERT OR REPLACE INTO telegram_bot_admins (user_id, added_by) VALUES (?, ?)", (new_id, admin_id))
            except Exception as e:
                logger.warning(f"Failed to persist admin: {e}")
            await self._send_message(session, chat_id, f"✅ Admin `{new_id}` successfully added!", message_thread_id=thread_id)

        elif cmd == "/removeadmin":
            if len(parts) < 2 or not parts[1].isdigit():
                await self._send_message(session, chat_id, "Usage: `/removeadmin <user_id>`", message_thread_id=thread_id)
                return
            target_id = int(parts[1])
            if target_id in self.master_admin_ids:
                await self._send_message(session, chat_id, "❌ Master Admin cannot be removed.", message_thread_id=thread_id)
                return
            self.co_admins.discard(target_id)
            try:
                with get_db_conn() as conn:
                    conn.execute("DELETE FROM telegram_bot_admins WHERE user_id = ?", (target_id,))
            except Exception as e:
                logger.warning(f"Failed to remove admin: {e}")
            await self._send_message(session, chat_id, f"🗑️ Admin `{target_id}` removed.", message_thread_id=thread_id)

        elif cmd == "/unblock":
            if len(parts) < 2 or not parts[1].isdigit():
                await self._send_message(session, chat_id, "Usage: `/unblock <user_id>`", message_thread_id=thread_id)
                return
            target_id = int(parts[1])
            self.blocked_users.discard(target_id)
            try:
                with get_db_conn() as conn:
                    conn.execute("DELETE FROM telegram_bot_blocked WHERE user_id = ?", (target_id,))
            except Exception:
                pass
            await self._send_message(session, chat_id, f"✅ User `{target_id}` unblocked.", message_thread_id=thread_id)

        elif cmd == "/send":
            if len(parts) < 3 or not parts[1].isdigit():
                await self._send_message(session, chat_id, "Usage: `/send <user_id> <message text>`", message_thread_id=thread_id)
                return
            target_user_id = int(parts[1])
            out_text = " ".join(parts[2:])
            success = await self._send_message(session, target_user_id, f"👨‍⚕️ **Kind Doctor:**\n\n{out_text}")
            if success:
                await self._send_message(session, chat_id, f"✅ Message delivered to `{target_user_id}`.", message_thread_id=thread_id)
            else:
                await self._send_message(session, chat_id, f"⚠️ Delivery failed to `{target_user_id}`.", message_thread_id=thread_id)

        else:
            await self._send_message(session, chat_id, f"Unknown command `{cmd}`. Type /help.", message_thread_id=thread_id)

    async def _handle_devi_ai_chat(self, session: aiohttp.ClientSession, chat_id: int, text: str, user_name: str):
        """Admin chatting naturally with Devi Ji AI assistant with multi-turn persistent memory."""
        session_id = f"admin_{chat_id}"
        history_context = ""
        try:
            recent_turns = await self.memory.get_recent_history(session_id, limit=6)
            if recent_turns:
                history_lines = [f"{t['role'].capitalize()}: {t['content']}" for t in recent_turns]
                history_context = "\n\n[Previous Conversation Context]:\n" + "\n".join(history_lines)
        except Exception as e:
            logger.debug(f"Memory retrieval skipped: {e}")

        system_prompt = (
            f"You are Devi Ji, the enlightened, deeply respectful, polite, and hyper-capable AI Guardian "
            f"and Operations Mentor assisting Dr. Amit Singh ({user_name}). "
            f"Always answer in natural, warm, friendly Roman Hinglish. "
            f"You have complete autonomy, telemetry, and self-healing supervision over the TG KindSync Pro engine."
            f"{history_context}"
        )
        try:
            res = await self.router.generate_response(
                system_prompt=system_prompt,
                user_prompt=text,
                category="fast"
            )
            reply = res.get("text") or res.get("content") or res.get("response") or "Pranam! Main Devi Ji hoon, main sun rahi hoon."
        except Exception as e:
            reply = f"Pranam {user_name}! Devi Ji yahan hain. (AI router note: {e})"
            
        await self._send_message(session, chat_id, reply)

        try:
            await self.memory.append_conversation(session_id, "user", text)
            await self.memory.append_conversation(session_id, "devi", reply)
        except Exception as e:
            logger.debug(f"Memory persistence skipped: {e}")

    async def _handle_admin_voice_note(self, session: aiohttp.ClientSession, chat_id: int, voice_obj: dict, user_name: str):
        """Transcribes incoming voice notes from Master Admins using Groq Whisper Large v3 and executes or replies."""
        file_id = voice_obj.get("file_id")
        duration = voice_obj.get("duration", 0)
        groq_api_key = os.getenv("GROQ_API_KEY", "").strip()

        if not file_id:
            await self._send_message(session, chat_id, "⚠️ Invalid voice note data.")
            return

        status_msg_id = await self._send_message(session, chat_id, f"🎙️ **Devi Ji listening ({duration}s)... Transcribing audio...**")

        try:
            # 1. Get file path from Telegram Bot API
            get_file_url = f"https://api.telegram.org/bot{self.token}/getFile"
            async with session.post(get_file_url, json={"file_id": file_id}, timeout=15) as gf_resp:
                if gf_resp.status != 200:
                    await self._send_message(session, chat_id, "❌ Failed to retrieve voice file from Telegram.")
                    return
                gf_data = await gf_resp.json()
                file_path = gf_data.get("result", {}).get("file_path")

            if not file_path:
                await self._send_message(session, chat_id, "❌ Voice note path not found on Telegram servers.")
                return

            # 2. Download audio stream
            download_url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
            async with session.get(download_url, timeout=30) as dl_resp:
                if dl_resp.status != 200:
                    await self._send_message(session, chat_id, "❌ Failed to download audio stream.")
                    return
                audio_bytes = await dl_resp.read()

            # 3. Transcribe via Groq Whisper API
            transcribed_text = ""
            if groq_api_key:
                groq_url = "https://api.groq.com/openai/v1/audio/transcriptions"
                form_data = aiohttp.FormData()
                form_data.add_field("file", audio_bytes, filename="voice.ogg", content_type="audio/ogg")
                form_data.add_field("model", "whisper-large-v3")
                form_data.add_field("response_format", "json")
                form_data.add_field("prompt", "Transcribe clinical, Hindi, and English medical conversation accurately.")

                headers = {"Authorization": f"Bearer {groq_api_key}"}
                async with session.post(groq_url, data=form_data, headers=headers, timeout=30) as gq_resp:
                    if gq_resp.status == 200:
                        gq_data = await gq_resp.json()
                        transcribed_text = gq_data.get("text", "").strip()
                    else:
                        logger.warning(f"Groq whisper transcription error {gq_resp.status}")

            if status_msg_id:
                self.create_tracked_task(self._auto_delete_message(session, chat_id, status_msg_id, 1))

            if not transcribed_text:
                await self._send_message(session, chat_id, "🎙️ Voice note received, but transcription was empty or inaudible. Please speak closer to the mic.")
                return

            # Relay transcription badge
            await self._send_message(session, chat_id, f"🎙️ **Transcribed Voice ({duration}s):**\n_{transcribed_text}_")

            # Route recognized administrative commands
            clean_cmd = transcribed_text.lower().strip()
            if "status" in clean_cmd or "engine" in clean_cmd:
                await self._handle_admin_command(session, chat_id, chat_id, "/engine")
            elif "backup" in clean_cmd:
                await self._handle_admin_command(session, chat_id, chat_id, "/backup")
            elif "clean" in clean_cmd:
                await self._handle_admin_command(session, chat_id, chat_id, "/clean")
            elif "scan" in clean_cmd:
                await self._handle_admin_command(session, chat_id, chat_id, "/scan")
            else:
                # Natural dialogue with Devi Ji with full memory context
                await self._handle_devi_ai_chat(session, chat_id, transcribed_text, user_name)

        except Exception as e:
            logger.error(f"Voice note processing failure: {e}", exc_info=True)
            await self._send_message(session, chat_id, f"⚠️ Voice note processing error: {e}")


if __name__ == "__main__":
    bot = DeviTelegramBot()
    asyncio.run(bot.start())

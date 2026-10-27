#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Universal Strip Words & Clean Rules Synchronization Bridge
Provides atomic, case-insensitive, deduplicated management of strip_words.txt,
Friend_Edition/strip_words.txt, and SQLite database storage with automatic
timestamped micro-backups and zero-downtime hot-reloading.
"""

import os
import re
import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict, Optional, Any
from contextlib import suppress

BASE_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_STRIP_FILE = BASE_PROJECT_DIR / "strip_words.txt"
STRIP_FILE = ROOT_STRIP_FILE
FRIEND_STRIP_FILE = BASE_PROJECT_DIR / "Friend_Edition" / "strip_words.txt"
BACKUP_DIR = BASE_PROJECT_DIR / "archives" / "strip_words_backups"
DB_PATH = BASE_PROJECT_DIR / "history_core.sqlite"

_RULES_CACHE = {
    "mtime": 0.0,
    "strip_words": [],
    "replace_words": {}
}

def init_strip_rules_db():
    """Initializes persistent strip rules table in SQLite."""
    try:
        with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS telegram_strip_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT NOT NULL,
                    replacement TEXT DEFAULT '',
                    is_active INTEGER DEFAULT 1,
                    added_by INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_strip_pattern_norm ON telegram_strip_rules(LOWER(TRIM(pattern)));")
            conn.commit()
    except Exception:
        pass

init_strip_rules_db()

def _create_timestamped_backup() -> Optional[Path]:
    """Creates a timestamped backup before any destructive mutation."""
    if not ROOT_STRIP_FILE.exists():
        return None
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        now = datetime.now()
        day_str = now.strftime("%A")
        date_str = now.strftime("%d-%B-%Y")
        time_str = now.strftime("%I-%M%p")
        backup_name = f"strip_words_backup_{day_str}_{date_str}_{time_str}.txt"
        backup_path = BACKUP_DIR / backup_name
        shutil.copy2(ROOT_STRIP_FILE, backup_path)
        return backup_path
    except Exception:
        return None

def _sync_to_files(lines: List[str]):
    """Atomically writes clean lines to both root and Friend_Edition strip_words.txt."""
    content = "\n".join(lines).strip() + "\n"
    
    # 1. Root file
    temp_root = ROOT_STRIP_FILE.with_suffix(".tmp")
    temp_root.write_text(content, encoding="utf-8")
    temp_root.replace(ROOT_STRIP_FILE)
    
    # 2. Friend edition file
    if FRIEND_STRIP_FILE.parent.exists():
        with suppress(Exception):
            FRIEND_STRIP_FILE.parent.mkdir(parents=True, exist_ok=True)
            temp_friend = FRIEND_STRIP_FILE.with_suffix(".tmp")
            temp_friend.write_text(content, encoding="utf-8")
            temp_friend.replace(FRIEND_STRIP_FILE)

def get_all_raw_rules() -> List[str]:
    """Reads all non-comment active rules from root strip_words.txt."""
    if not ROOT_STRIP_FILE.exists():
        return []
    rules = []
    try:
        for line in ROOT_STRIP_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith(r"\#"):
                line = line[1:]
            elif line.startswith("#"):
                rem = line.lstrip("#").strip()
                if not rem or line.startswith("##") or rem.startswith("---") or rem.startswith("===") or rem.startswith("📝") or rem.startswith("🛡️") or rem.startswith("1.") or rem.startswith("2.") or rem.startswith("3.") or " " in line[:4]:
                    continue
            rules.append(line)
    except Exception:
        pass
    return rules

def get_parsed_rules_cached() -> Tuple[List[str], Dict[str, str]]:
    """Cached accessor for strip words and replacement mappings."""
    global _RULES_CACHE
    if not ROOT_STRIP_FILE.exists():
        return [], {}
    
    mtime = ROOT_STRIP_FILE.stat().st_mtime
    if mtime == _RULES_CACHE["mtime"] and (_RULES_CACHE["strip_words"] or _RULES_CACHE["replace_words"]):
        return _RULES_CACHE["strip_words"], _RULES_CACHE["replace_words"]

    strip_words = []
    replace_words = {}
    for line in get_all_raw_rules():
        if "=>" in line:
            ow, nw = line.split("=>", 1)
            if ow.strip(): replace_words[ow.strip()] = nw.strip()
        elif ":" in line and not line.startswith("http"):
            ow, nw = line.split(":", 1)
            if ow.strip(): replace_words[ow.strip()] = nw.strip()
        else:
            strip_words.append(line)

    _RULES_CACHE = {
        "mtime": mtime,
        "strip_words": strip_words,
        "replace_words": replace_words
    }
    return strip_words, replace_words

def sync_strip_words_file_to_db() -> int:
    """Synchronizes existing strip_words.txt file into SQLite telegram_strip_rules table."""
    raw_rules = get_all_raw_rules()
    if not raw_rules:
        return 0
    synced = 0
    with suppress(Exception):
        with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
            for item in raw_rules:
                pat = item
                repl = ""
                if "=>" in item:
                    pat, repl = item.split("=>", 1)
                    pat, repl = pat.strip(), repl.strip()
                elif ":" in item and not item.startswith("http"):
                    pat, repl = item.split(":", 1)
                    pat, repl = pat.strip(), repl.strip()
                conn.execute(
                    "INSERT OR IGNORE INTO telegram_strip_rules (pattern, replacement, is_active) VALUES (?, ?, 1)",
                    (pat, repl)
                )
                synced += 1
            conn.commit()
    return synced

def search_strip_rule(query: str) -> List[str]:
    """Case-insensitive search returning all matching rules."""
    clean_q = str(query).strip().lower()
    if not clean_q:
        return []
    matches = []
    for rule in get_all_raw_rules():
        if clean_q in rule.lower():
            matches.append(rule)
    return matches

def add_strip_rules(raw_input: Any, added_by: int = 0, user_id: int = 0) -> int:
    """
    Parses, deduplicates case-insensitively, and adds new strip rules.
    Accepts string, list of strings, or newline/comma-separated tokens.
    Returns: count of successfully added rules.
    """
    effective_user_id = added_by or user_id
    if not raw_input:
        return 0

    if isinstance(raw_input, (list, tuple, set)):
        to_process = [str(t).strip() for t in raw_input if str(t).strip()]
    else:
        tokens = re.split(r'[,\|\n]+', str(raw_input))
        to_process = [t.strip() for t in tokens if t.strip()]

    if not to_process:
        return 0

    _create_timestamped_backup()

    raw_lines = ROOT_STRIP_FILE.read_text(encoding="utf-8", errors="ignore").splitlines() if ROOT_STRIP_FILE.exists() else []
    existing_lower = set(l.strip().lower() for l in raw_lines if l.strip())

    added = []

    with suppress(Exception):
        with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
            for item in to_process:
                norm = item.lower()
                if norm in existing_lower:
                    continue
                
                # Check replacement pair
                repl = ""
                pat = item
                if "=>" in item:
                    pat, repl = item.split("=>", 1)
                    pat, repl = pat.strip(), repl.strip()
                elif ":" in item and not item.startswith("http"):
                    pat, repl = item.split(":", 1)
                    pat, repl = pat.strip(), repl.strip()

                conn.execute(
                    "INSERT OR REPLACE INTO telegram_strip_rules (pattern, replacement, is_active, added_by) VALUES (?, ?, 1, ?)",
                    (pat, repl, effective_user_id)
                )
                raw_lines.append(item)
                existing_lower.add(norm)
                added.append(item)
            conn.commit()

    if added:
        _sync_to_files(raw_lines)

    return len(added)

def delete_strip_rule(target: str, user_id: int = 0, deleted_by: int = 0) -> bool:
    """Case-insensitive safe deletion with automatic snapshot backup."""
    effective_user_id = deleted_by or user_id
    clean_target = str(target).strip().lower()
    if not clean_target or not ROOT_STRIP_FILE.exists():
        return False

    raw_lines = ROOT_STRIP_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
    new_lines = []
    found = False

    for line in raw_lines:
        line_clean = line.strip().lower()
        if not found and (line_clean == clean_target or clean_target in line_clean):
            found = True
            continue
        new_lines.append(line)

    if not found:
        return False

    _create_timestamped_backup()
    _sync_to_files(new_lines)

    with suppress(Exception):
        with sqlite3.connect(DB_PATH, timeout=20.0) as conn:
            conn.execute("UPDATE telegram_strip_rules SET is_active = 0 WHERE LOWER(TRIM(pattern)) = ?", (clean_target,))
            conn.commit()

    return True

def deduplicate_and_clean() -> int:
    """Removes blank lines and duplicates while preserving rule order."""
    if not ROOT_STRIP_FILE.exists():
        return 0

    _create_timestamped_backup()
    raw_lines = ROOT_STRIP_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
    seen = set()
    cleaned = []

    for line in raw_lines:
        stripped = line.strip()
        if not stripped:
            continue
        norm = stripped.lower()
        if norm.startswith("#") and not norm.startswith("#the"):
            # Preserve comment headers
            cleaned.append(stripped)
            continue
        if norm in seen:
            continue
        seen.add(norm)
        cleaned.append(stripped)

    _sync_to_files(cleaned)
    return len(cleaned)

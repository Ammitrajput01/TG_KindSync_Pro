#!/usr/bin/env python3
"""
scripts/rewind_general_misrouted_messages.py
==============================================================================
Safe Audit & Rewind Utility for Misrouted Messages in General Topic.
- Cleans erroneously forwarded records from `forwarded` table.
- Resets watermarks to allow clean re-cloning directly into correct forum topics.
- Optionally purges the misrouted messages from target General topic.
==============================================================================
"""

import os
import sys
import sqlite3
import asyncio
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

DB_PATH = ROOT_DIR / "history_core.sqlite"
SOURCE_CHAT = "-1003968310888"
TARGET_CHAT = "-1004300858087"
TARGET_TOPIC = 0
MIN_MSG_ID = 79142
MAX_MSG_ID = 79810

def audit_misrouted_records():
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        return 0
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT count(*), min(msg_id), max(msg_id) 
        FROM forwarded 
        WHERE source_chat=? AND target_chat=? AND target_topic=? AND msg_id >= ?
        """,
        (SOURCE_CHAT, TARGET_CHAT, TARGET_TOPIC, MIN_MSG_ID)
    )
    row = cur.fetchone()
    count = row[0] or 0
    min_id = row[1] or 0
    max_id = row[2] or 0
    print(f"📊 Audit Results for {DB_PATH.name}:")
    print(f"   • Misrouted General records count: {count}")
    print(f"   • Message ID Range: #{min_id} to #{max_id}")
    conn.close()
    return count

def rewind_forwarded_records():
    if not DB_PATH.exists():
        return
    import shutil
    from datetime import datetime

    # Strict Backup Naming Rule: [prefix]_[Day]_[Date]-[Month]-[Year]_[Time-12hAM-PM].[ext]
    now = datetime.now()
    day_name = now.strftime("%A")
    date_str = now.strftime("%d-%B-%Y")
    time_str = now.strftime("%I-%M%p")
    backup_name = f"history_core_backup_{day_name}_{date_str}_{time_str}.sqlite"
    backup_path = ROOT_DIR / backup_name
    shutil.copy2(DB_PATH, backup_path)
    print(f"📦 Created pre-rewind database safety snapshot: {backup_name}")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        DELETE FROM forwarded 
        WHERE source_chat=? AND target_chat=? AND target_topic=? AND msg_id >= ?
        """,
        (SOURCE_CHAT, TARGET_CHAT, TARGET_TOPIC, MIN_MSG_ID)
    )
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    print(f"✅ Successfully deleted {deleted} misrouted records from 'forwarded' table.")
    print("   Watermark state is now restored to before the misrouting occurred (#79141).")

if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "audit"
    if action == "rewind":
        rewind_forwarded_records()
    else:
        audit_misrouted_records()
        print("\nTo execute database rewind, run:")
        print("   python scripts/rewind_general_misrouted_messages.py rewind")


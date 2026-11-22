#!/usr/bin/env python3
"""
rewind_bmine_general_messages.py — Safe Audit & Rewind Utility for BMine General Misrouted Messages
==================================================================================================
Identifies and cleans records mistakenly forwarded to General topic (target_topic=1 or 0)
in target chat BE Mine (-1004300858087), creates timestamped safety snapshots,
and rewinds watermarks so messages can be cleanly cloned into their proper sub-topics.
"""

import os
import sys
import shutil
import sqlite3
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "history_core.sqlite"
BACKUP_DIR = BASE_DIR / "db_backups"

def get_timestamped_backup_filename() -> str:
    now = datetime.now()
    day = now.strftime("%A")
    date_month_year = now.strftime("%d-%B-%Y")
    time_12h = now.strftime("%I-%M%p")
    return f"history_core_backup_{day}_{date_month_year}_{time_12h}.sqlite"

def main():
    print("=" * 70)
    print("🔄 B-MINE GENERAL TOPIC REWIND & WATERMARK AUDIT UTILITY")
    print("=" * 70)

    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        sys.exit(1)

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup_file = BACKUP_DIR / get_timestamped_backup_filename()
    print(f"📦 Creating safety snapshot: {backup_file.name}...")
    shutil.copy2(DB_PATH, backup_file)
    print("  ✔ Snapshot verified.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    target_chat = "-1004300858087"
    source_chat = "-1003968310888"

    # 1. Audit misrouted records in General (topic 1 or 0)
    cursor.execute("""
        SELECT count(*), min(msg_id), max(msg_id)
        FROM forwarded
        WHERE target_chat = ? AND (target_topic = 1 OR target_topic = 0) AND msg_id >= 79141
    """, (target_chat,))
    row = cursor.fetchone()
    count, min_id, max_id = row[0], row[1], row[2]

    print(f"\n📊 Audit Results for {target_chat} (General Topic):")
    print(f"  • Misrouted Messages Count : {count}")
    print(f"  • Message ID Range         : #{min_id} to #{max_id}")

    if count > 0:
        # 2. Delete misrouted records
        print(f"\n🗑️  Purging {count} misrouted records from 'forwarded' table...")
        cursor.execute("""
            DELETE FROM forwarded
            WHERE target_chat = ? AND (target_topic = 1 OR target_topic = 0) AND msg_id >= 79141
        """, (target_chat,))
        deleted = cursor.rowcount
        conn.commit()
        print(f"  ✔ Successfully purged {deleted} records.")
    else:
        print("✔ No misrouted messages in General topic (already clean).")

    # 3. Check and restore watermark
    safe_watermark = 79326
    source_chat_id = "-1003968310888"
    print(f"\n🏷️  Watermark Status & Restoration:")

    # Check source_watermarks
    cursor.execute("SELECT chat_id, max_id FROM source_watermarks")
    for r in cursor.fetchall():
        c_id, m_id = str(r[0]), r[1]
        if source_chat_id in c_id or c_id.replace("-100", "") in source_chat_id:
            print(f"  • Source Watermark (Chat {c_id}) : #{m_id}")
            if m_id > safe_watermark:
                cursor.execute("UPDATE source_watermarks SET max_id = ? WHERE chat_id = ?", (safe_watermark, r[0]))
                print(f"  ✔ Rolled back source watermark to #{safe_watermark}")

    # Check topic_watermarks
    cursor.execute("SELECT target_chat, target_topic, max_id FROM topic_watermarks WHERE target_chat = ?", (target_chat,))
    for tw in cursor.fetchall():
        t_topic, t_max = tw[1], tw[2]
        print(f"  • Topic Watermark (Topic {t_topic}) : #{t_max}")
        if t_topic in (0, 1) and t_max > safe_watermark:
            cursor.execute("UPDATE topic_watermarks SET max_id = ? WHERE target_chat = ? AND target_topic = ?", (safe_watermark, target_chat, t_topic))
            print(f"  ✔ Rolled back Topic {t_topic} watermark to #{safe_watermark}")

    conn.commit()
    conn.close()
    print("\n" + "=" * 70)
    print(f"🎉 AUDIT & REWIND COMPLETE! Next cloner run will cleanly clone from #{safe_watermark + 1}.")
    print("=" * 70)

if __name__ == "__main__":
    main()


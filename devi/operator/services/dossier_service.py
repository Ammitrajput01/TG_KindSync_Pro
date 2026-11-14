# -*- coding: utf-8 -*-
"""
Devi Operator Biometric Dossier & SangMata Intelligence Service
Tracks user identity shifts, username history, and telemetry dossiers.
Architect: Dr. Amit Singh (Kind Doctor) · @Kinddoctor4u
"""

import json
import sqlite3
import html
from datetime import datetime
from typing import Optional, Dict, Any

def track_user_dossier(conn_getter, sender: dict, detected_phone: Optional[str] = None) -> Dict[str, Any]:
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
        with conn_getter() as conn:
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

                conn.execute("""
                    UPDATE telegram_users_dossier 
                    SET first_name = ?, last_name = ?, username = ?, phone_number = ?, is_premium = ?, language_code = ?,
                        last_seen = CURRENT_TIMESTAMP, total_messages = total_messages + 1,
                        name_history = ?, username_history = ?, changes_count = ?
                    WHERE user_id = ?
                """, (current_fn, current_ln, current_username, active_phone, is_premium, lang_code,
                      json.dumps(name_hist), json.dumps(uname_hist), changes_count, user_id))

                result["name_history"] = name_hist
                result["username_history"] = uname_hist
                result["changes_count"] = changes_count
                result["changes_detected"] = changes_detected
                result["total_messages"] = (row["total_messages"] or 0) + 1
                result["first_seen"] = str(row["first_seen"])
                result["phone"] = active_phone or "Not Shared"
    except Exception as e:
        pass

    return result

def format_sangmata_dossier(dossier: Dict[str, Any], title_prefix: str = "SANGMATA DOSSIER INTELLIGENCE") -> str:
    """Formats clean, high-yield Sangmata intelligence & deep OSINT card in HTML."""
    uid = dossier.get("user_id")
    full_name = html.escape(dossier.get("full_name") or "Anonymous")
    username = html.escape(dossier.get("username") or "")
    username_display = f"@{username}" if username else "<i>No username configured</i>"
    user_tag = f'<a href="tg://user?id={uid}"><b>{full_name}</b></a>'
    
    first_seen = dossier.get("first_seen", "Just now")
    total_msgs = dossier.get("total_messages", 1)
    changes_count = dossier.get("changes_count", 0)
    phone = dossier.get("phone", "Not Shared")
    
    # 9-Item SangMata Radar Timeline
    card = [
        f"🕵️ <b>{html.escape(title_prefix)}</b>",
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        f"👤 <b>Subject:</b> {user_tag} (<code>{uid}</code>)",
        f"🏷️ <b>Username:</b> {username_display}",
        f"📱 <b>Phone Track:</b> <code>{html.escape(str(phone))}</code>",
        f"📅 <b>First Observed:</b> <code>{html.escape(str(first_seen)[:16])}</code>",
        f"💬 <b>Activity Footprint:</b> <code>{total_msgs} messages recorded</code>",
        f"🔄 <b>Total Identity Shifts:</b> <code>{changes_count}</code>\n"
    ]

    # Name Shift History
    name_hist = dossier.get("name_history", [])
    if name_hist:
        card.append("📜 <b>Historical Name Records:</b>")
        for idx, item in enumerate(name_hist[-5:], 1):
            nm = html.escape(item.get("name", "Unknown"))
            ts = html.escape(str(item.get("changed_at", ""))[:16])
            card.append(f"  {idx}. <code>{nm}</code> <i>({ts})</i>")
        card.append("")

    # Username Shift History
    uname_hist = dossier.get("username_history", [])
    if uname_hist:
        card.append("🏷️ <b>Historical Username Records:</b>")
        for idx, item in enumerate(uname_hist[-5:], 1):
            un = html.escape(item.get("username", "None"))
            ts = html.escape(str(item.get("changed_at", ""))[:16])
            card.append(f"  {idx}. <code>@{un}</code> <i>({ts})</i>")
        card.append("")

    # Active Changes Detected in this specific turn
    changes = dossier.get("changes_detected", [])
    if changes:
        card.append("⚠️ <b>Real-Time Shifts Detected Now:</b>")
        for c in changes:
            card.append(f"  • <code>{html.escape(c)}</code>")
        card.append("")

    card.append("🛡️ <i>DEVI SangMata Radar Engine · Continuous Live Protection</i>")
    return "\n".join(card)

#!/usr/bin/env python3
"""
Study Help Safe Member Auditor & Exclusion Engine
Exports all members of Study Help (-1003912970546), isolates the last 50 joined members,
and compiles the verified safe member list for migration into Study Help 2.0.
"""

import os
import sys
import json
import csv
import shutil
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

CHAT_ID = -1003912970546

async def run_audit():
    from telethon import TelegramClient
    from telethon.tl.types import ChannelParticipantAdmin, ChannelParticipantCreator

    api_id = int(os.getenv("API_ID", "36193727"))
    api_hash = os.getenv("API_HASH", "fef19b5b71dbce122855734bc1a72d3e")

    # Safe temp copy to prevent sqlite lock conflicts with running cloner
    base_session = "session_forwarder.session"
    temp_session = "temp_member_export.session"

    if os.path.exists(base_session):
        shutil.copy2(base_session, temp_session)
    elif os.path.exists("session_account_9403.session"):
        shutil.copy2("session_account_9403.session", temp_session)
    else:
        print("❌ ERROR: No session file found!")
        sys.exit(1)

    print(f"🔗 Connecting to Telegram MTProto...")
    client = TelegramClient("temp_member_export", api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        print("❌ ERROR: Client not authorized in temp session!")
        await client.disconnect()
        if os.path.exists(temp_session): os.remove(temp_session)
        sys.exit(1)

    me = await client.get_me()
    print(f"✔ Logged in as: {me.first_name} (@{me.username}) ID: {me.id}")

    print(f"🔍 Fetching chat entity for Study Help ({CHAT_ID})...")
    chat = await client.get_entity(CHAT_ID)
    print(f"✔ Found Chat: {chat.title} (ID: {chat.id})")

    print(f"👥 Fetching participants (this may take 1-2 minutes for ~2600 members)...")
    participants = []
    
    # iter_participants fetches in reverse chronological order (newest joined first)
    async for user in client.iter_participants(chat):
        # Extract join date if present on participant object
        join_date_iso = None
        role = "member"
        p_obj = getattr(user, "participant", None)
        if p_obj:
            if isinstance(p_obj, ChannelParticipantCreator):
                role = "creator"
            elif isinstance(p_obj, ChannelParticipantAdmin):
                role = "admin"
            if hasattr(p_obj, "date") and p_obj.date:
                join_date_iso = p_obj.date.isoformat()

        participants.append({
            "id": user.id,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "username": user.username or "",
            "phone": user.phone or "",
            "is_bot": bool(user.bot),
            "role": role,
            "join_date": join_date_iso
        })

    total_count = len(participants)
    print(f"✔ Total participants fetched: {total_count}")

    # Separate non-bot members
    human_members = [u for u in participants if not u["is_bot"]]
    bots = [u for u in participants if u["is_bot"]]

    # Top 50 newest members (the suspects/quarantine)
    quarantine_last50 = human_members[:50]
    safe_members = human_members[50:]

    now = datetime.now()
    timestamp_suffix = now.strftime("%A_%d-%B-%Y_%I-%M%p")
    display_timestamp = now.strftime("%A, %d %B %Y | %I:%M %p")

    os.makedirs("exports", exist_ok=True)

    quarantine_file = f"exports/study_help_blacklisted_last50_{timestamp_suffix}.json"
    safe_json_file = f"exports/study_help_safe_members_{timestamp_suffix}.json"
    safe_csv_file = f"exports/study_help_safe_members_{timestamp_suffix}.csv"

    # Write quarantine
    with open(quarantine_file, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": display_timestamp,
            "chat_title": chat.title,
            "chat_id": chat.id,
            "quarantine_count": len(quarantine_last50),
            "reason": "Exclusion list of last 50 joined members before copyright incident",
            "members": quarantine_last50
        }, f, indent=2, ensure_ascii=False)

    # Write safe members JSON
    with open(safe_json_file, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": display_timestamp,
            "chat_title": chat.title,
            "chat_id": chat.id,
            "total_participants": total_count,
            "safe_member_count": len(safe_members),
            "quarantined_count": len(quarantine_last50),
            "bot_count": len(bots),
            "members": safe_members
        }, f, indent=2, ensure_ascii=False)

    # Write safe members CSV
    with open(safe_csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["User ID", "Username", "First Name", "Last Name", "Phone", "Role", "Join Date"])
        for u in safe_members:
            writer.writerow([u["id"], u["username"], u["first_name"], u["last_name"], u["phone"], u["role"], u["join_date"]])

    print("=" * 60)
    print(f"🎉 AUDIT COMPLETE at {display_timestamp}")
    print(f"• Total Members in Study Help : {total_count}")
    print(f"• Quarantined / Excluded (Last 50) : {len(quarantine_last50)} -> {quarantine_file}")
    print(f"• Verified Safe Members : {len(safe_members)} -> {safe_json_file}")
    print(f"• Safe CSV Export : {safe_csv_file}")
    print("=" * 60)

    await client.disconnect()
    
    # Cleanup temp session files
    for ext in ["", "-journal", ".journal"]:
        f_tmp = f"{temp_session}{ext}"
        if os.path.exists(f_tmp):
            try: os.remove(f_tmp)
            except Exception: pass

if __name__ == "__main__":
    asyncio.run(run_audit())


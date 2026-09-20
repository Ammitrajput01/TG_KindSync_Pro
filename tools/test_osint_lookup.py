import asyncio
import os
import json
from pathlib import Path
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest

load_dotenv()

async def resolve_username(username: str):
    api_id = int(os.getenv("API_ID", "0"))
    api_hash = os.getenv("API_HASH", "")
    session_file = "session_scanner"
    
    client = TelegramClient(session_file, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        # try session_account_9081
        await client.disconnect()
        client = TelegramClient("session_account_9081", api_id, api_hash)
        await client.connect()
        
    try:
        user = await client.get_entity(username)
        full = await client(GetFullUserRequest(user))
        full_user = full.full_user
        
        data = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "phone": user.phone,
            "premium": getattr(user, "premium", False),
            "bot": getattr(user, "bot", False),
            "verified": getattr(user, "verified", False),
            "scam": getattr(user, "scam", False),
            "fake": getattr(user, "fake", False),
            "restricted": getattr(user, "restricted", False),
            "about": getattr(full_user, "about", None),
            "blocked": getattr(full_user, "blocked", False),
            "common_chats_count": getattr(full_user, "common_chats_count", 0),
        }
        print("RESULT_JSON:" + json.dumps(data))
    except Exception as e:
        print("ERROR:", e)
    finally:
        await client.disconnect()

if __name__ == "__main__":
    import sys
    uname = sys.argv[1] if len(sys.argv) > 1 else "@Doctorsahab2"
    asyncio.run(resolve_username(uname))

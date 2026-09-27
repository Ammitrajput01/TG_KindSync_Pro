import asyncio
import os
import shutil
from pathlib import Path
from telethon import TelegramClient

API_ID = int(os.getenv("API_ID", "36193727") or 36193727)
API_HASH = os.getenv("API_HASH", "fef19b9b1434a3e66b009fd31053200b")

async def main():
    for f in Path("/home/ubuntu").rglob("*.session"):
        if "temp" in f.name: continue
        try:
            stem_path = str(f.with_suffix(''))
            c = TelegramClient(stem_path, API_ID, API_HASH)
            await c.connect()
            auth = await c.is_user_authorized()
            if auth:
                me = await c.get_me()
                print(f"AUTH TRUE: {f} -> {me.first_name} (ID: {me.id}, is_bot: {getattr(me, 'bot', False)})")
            await c.disconnect()
        except Exception as e:
            try:
                temp_stem = f"/home/ubuntu/TG_KindSync_Pro/temp_check_{f.stem}"
                shutil.copy2(f, f"{temp_stem}.session")
                c = TelegramClient(temp_stem, API_ID, API_HASH)
                await c.connect()
                auth = await c.is_user_authorized()
                if auth:
                    me = await c.get_me()
                    print(f"AUTH TRUE (clone): {f} -> {me.first_name} (ID: {me.id}, is_bot: {getattr(me, 'bot', False)})")
                await c.disconnect()
                Path(f"{temp_stem}.session").unlink(missing_ok=True)
            except Exception:
                pass

if __name__ == "__main__":
    asyncio.run(main())

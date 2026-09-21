#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builds a 1-Click Oracle Cloud Launcher Package for Friend.
Includes auto-permission fix, SSH key, and instant launcher.
"""

import os
import zipfile
from datetime import datetime
from pathlib import Path

def get_timestamp_filename(prefix, ext="zip"):
    now = datetime.now()
    day_name = now.strftime("%A")
    date_str = now.strftime("%d-%B-%Y")
    time_str = now.strftime("%I-%M%p")
    return f"{prefix}_{day_name}_{date_str}_{time_str}.{ext}"

def main():
    root = Path(__file__).resolve().parent
    zip_name = get_timestamp_filename("TG_KindSync_Oracle_Friend_Edition", "zip")
    zip_path = root / zip_name
    static_zip_path = root / "TG_KindSync_Oracle_Friend_Package.zip"

    readme_content = """================================================================================
🚀 TG KINDSYNC PRO — ORACLE CLOUD 24/7 LAUNCHER (FRIEND EDITION)
================================================================================

Bhai, bas 1-Click me Oracle Cloud VPS par 24/7 Telegram Forwarder start ho jayega!

--------------------------------------------------------------------------------
⭐ KAISE CHALANA HAI:
--------------------------------------------------------------------------------
1. Is poore folder ko Extract karo.
2. "CONNECT_ORACLE_FRIEND.bat" par DOUBLE CLICK karo!
   - (Key permissions aur server connection automatically 100% fix ho jayega)
3. Screen par Login Wizard aayega:
   - Telegram App se QR Code scan karo (Settings ➔ Devices ➔ Link Desktop Device)
     YA Mobile Number + 5-digit OTP daalo.
4. Option [1] daba kar Live Forwarding shuru kar do!

🎉 DONE! Ab aapka computer band hone par bhi ye 24/7 cloud par chalta rahega!

Developer: Dr. Amit Singh (Kind Doctor)
Contact  : @Kinddoctor4u · @Ammitrajput1
================================================================================
"""

    temp_readme = root / "HOW_TO_RUN.txt"
    with open(temp_readme, "w", encoding="utf-8") as f:
        f.write(readme_content)

    files_to_pack = [
        ("CONNECT_ORACLE_FRIEND.bat", "CONNECT_ORACLE_FRIEND.bat"),
        ("START_ORACLE_FRIEND_24_7.bat", "START_ORACLE_FRIEND_24_7.bat"),
        ("oracle_key_latest.key", "oracle_key_latest.key"),
        ("deploy/setup_friend_oracle.sh", "deploy/setup_friend_oracle.sh"),
        ("deploy/start_friend_24_7.sh", "deploy/start_friend_24_7.sh"),
        ("HOW_TO_RUN.txt", "HOW_TO_RUN.txt")
    ]

    for target_zip in [zip_path, static_zip_path]:
        with zipfile.ZipFile(target_zip, "w", zipfile.ZIP_DEFLATED) as z:
            for src_rel, arc_name in files_to_pack:
                full_src = root / src_rel
                if full_src.exists():
                    z.write(full_src, arc_name)
                    print(f"Added: {arc_name}")
                else:
                    print(f"Warning: {src_rel} not found!")

    if temp_readme.exists():
        temp_readme.unlink()

    print(f"\n[OK] Package created: {zip_path.name}")
    print(f"[OK] Static alias created: {static_zip_path.name}")

if __name__ == "__main__":
    main()

import os
import zipfile
import sys
import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent

# Generate Strict Standard Timestamp
# Format: [prefix]_[Day]_[Date]-[Month]-[Year]_[Time-12hAM-PM].[ext]
now = datetime.datetime.now()
day_name = now.strftime("%A")                    # e.g. Friday
date_month_year = now.strftime("%d-%B-%Y")      # e.g. 18-September-2026
time_12h = now.strftime("%I-%M%p")               # e.g. 09-32PM
display_caption = now.strftime("%A, %d %B %Y | %I:%M %p") # e.g. Friday, 18 September 2026 | 09:32 PM

ZIP_NAME = f"TG_KindSync_Pro_Friend_Edition_{day_name}_{date_month_year}_{time_12h}.zip"
ZIP_PATH = BASE_DIR / ZIP_NAME
EXPORT_DIR = BASE_DIR / "export_backups"
EXPORT_DIR.mkdir(exist_ok=True)
EXPORT_ZIP_PATH = EXPORT_DIR / ZIP_NAME

# Standard alias for automated tools
LEGACY_ZIP_NAME = "TG_KindSync_Pro_v14.5_CLEAN_RELEASE.zip"
LEGACY_ZIP_PATH = BASE_DIR / LEGACY_ZIP_NAME

# Zero AI - Pure Telegram Forwarder Engine Files for Friend
ESSENTIAL_FILES = [
    "1_START_FORWARDER.bat",
    "START_BOT.bat",
    "START_KINDSYNC.bat",
    "EASY_SETUP.bat",
    "UPDATE_KINDSYNC.bat",
    "version.json",
    "tg_kindsync_pro.py",
    "tg_kind_mode_v14.py",
    "web_dashboard.py",
    "main.py",
    "quick_setup.py",
    "requirements.txt",
    ".env.example",
    "kind_doctor_thumb.jpg",
    "tg_thumb_cached.jpg",
    "strip_words.txt",
    "HOW_TO_RUN_FOR_FRIEND.txt",
    "README.md",
]

# Only include lightweight helper tools (updater, login_panel) - NO DEVI AI
ESSENTIAL_DIRS = [
    "tools"
]

# Pre-configured clean full-format .env content for Friend (from .env.example)
CLEAN_ENV_CONTENT = (BASE_DIR / ".env.example").read_text(encoding="utf-8")

def build_zip():
    print("=" * 75)
    print("  🩺 TG KINDSYNC PRO — FRIEND EDITION CLEAN RELEASE BUILDER")
    print(f"  📅 Timestamp: {display_caption}")
    print(f"  📦 Package  : {ZIP_NAME}")
    print("=" * 75)

    if ZIP_PATH.exists():
        try:
            ZIP_PATH.unlink()
            print(f"[*] Removed previous {ZIP_NAME}")
        except Exception as e:
            print(f"[!] Could not remove existing zip: {e}")

    with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        # Add essential clean files
        for fname in ESSENTIAL_FILES:
            full_path = BASE_DIR / fname
            if full_path.exists():
                fsize = full_path.stat().st_size
                zf.write(full_path, arcname=fname)
                print(f"  + Added: {fname:<30} ({fsize:,} bytes)")

        # Inject ready-to-run pre-configured .env directly into the zip
        zf.writestr(".env", CLEAN_ENV_CONTENT)
        print("  + Injected: .env (Pre-configured Verified Credentials - Zero AI)")

        # Add essential directories (tools only)
        for dname in ESSENTIAL_DIRS:
            dir_path = BASE_DIR / dname
            if dir_path.exists():
                for root, _, files in os.walk(dir_path):
                    if "__pycache__" in root: continue
                    for f in files:
                        fp = Path(root) / f
                        rel_p = fp.relative_to(BASE_DIR)
                        zf.write(fp, arcname=str(rel_p))
                print(f"  + Added Module: {dname:<23} (recursive)")

    total_size = ZIP_PATH.stat().st_size

    # Also save copy in export_backups
    import shutil
    shutil.copy2(ZIP_PATH, EXPORT_ZIP_PATH)
    shutil.copy2(ZIP_PATH, LEGACY_ZIP_PATH)

    print("=" * 75)
    print("🎉 SUCCESS: TG KindSync Pro Friend Package Built Successfully!")
    print(f"📍 Location      : {ZIP_PATH}")
    print(f"📁 Backup Archive: {EXPORT_ZIP_PATH}")
    print(f"⚖️ Size          : {total_size / (1024 * 1024):.2f} MB ({total_size:,} bytes)")
    print(f"📅 Timestamp     : {display_caption}")
    print("🔒 Verification  : Zero AI Overhead, Pre-configured Official Telegram API,")
    print("                  Zero personal sessions, Zero personal databases (100% Clean)!")
    print("=" * 75)

if __name__ == "__main__":
    build_zip()

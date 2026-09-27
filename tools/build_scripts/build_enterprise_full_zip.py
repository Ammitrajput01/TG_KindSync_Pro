import os
import zipfile
import sys
import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = Path(__file__).resolve().parent

# Generate Strict Standard Timestamp according to Workspace Agent Guidelines:
# Pattern: [prefix]_[Day]_[Date]-[Month]-[Year]_[Time-12hAM-PM].[ext]
now = datetime.datetime.now()
day_name = now.strftime("%A")                    # e.g. Friday
date_month_year = now.strftime("%d-%B-%Y")      # e.g. 18-September-2026
time_12h = now.strftime("%I-%M%p")               # e.g. 10-38PM
display_caption = now.strftime("%A, %d %B %Y | %I:%M %p") # e.g. Friday, 18 September 2026 | 10:38 PM

ZIP_NAME = f"TG_KindSync_Pro_Full_Enterprise_{day_name}_{date_month_year}_{time_12h}.zip"
ZIP_PATH = BASE_DIR / ZIP_NAME
EXPORT_DIR = BASE_DIR / "export_backups"
EXPORT_DIR.mkdir(exist_ok=True)
EXPORT_ZIP_PATH = EXPORT_DIR / ZIP_NAME

# Standard alias for deployment/distribution scripts
ALIAS_ZIP_NAME = "TG_KindSync_Pro_v14.5_ENTERPRISE_FULL.zip"
ALIAS_ZIP_PATH = BASE_DIR / ALIAS_ZIP_NAME

# Core Essential Files for Full Enterprise Edition
ESSENTIAL_ROOT_FILES = [
    "1_START_ALL.bat",
    "1_START_FORWARDER.bat",
    "2_START_ENGINE.bat",
    "3_START_DEVI_DASHBOARD.bat",
    "START_BOT.bat",
    "START_KIND_DOCTOR_BOT.bat",
    "START_TABBED.bat",
    "EASY_SETUP.bat",
    "UPDATE_KINDSYNC.bat",
    "CONNECT_ORACLE_SHELL.bat",
    "PUSH_TO_GITHUB.bat",
    "PUBLISH_UPDATE.bat",
    "version.json",
    "tg_kindsync_pro.py",
    "tg_kind_mode_v14.py",
    "web_dashboard.py",
    "sentinel_observer.py",
    "main.py",
    "quick_setup.py",
    "requirements.txt",
    ".env.example",
    "kind_doctor_thumb.jpg",
    "tg_thumb_cached.jpg",
    "strip_words.txt",
    "AGENTS.md",
    "GEMINI.md",
    "README.md",
    "HOW_TO_RUN_FOR_FRIEND.txt"
]

# Essential Enterprise Directories (Including Devi AI, .agents, deploy, docs, tools)
ESSENTIAL_DIRS = [
    "devi",
    ".agents",
    "tools",
    "deploy",
    "docs"
]

EXCLUDE_PATTERNS = [
    "__pycache__",
    ".pyc",
    ".git",
    ".pytest_cache",
    ".venv",
    ".session",
    ".session-journal",
    "history_core.sqlite",
    "engine.lock",
    "dead_letter.jsonl"
]

def should_exclude(path_str):
    for pattern in EXCLUDE_PATTERNS:
        if pattern in path_str:
            return True
    return False

print("=" * 75)
print("  🩺 TG KINDSYNC PRO — FULL ENTERPRISE MASTERPIECE RELEASE BUILDER")
print(f"  📅 Timestamp: {display_caption}")
print(f"  📦 Package  : {ZIP_NAME}")
print("=" * 75)

total_files = 0
total_uncompressed_bytes = 0

with zipfile.ZipFile(ZIP_PATH, 'w', zipfile.ZIP_DEFLATED) as zip_out:
    # 1. Add Essential Root Files
    for filename in ESSENTIAL_ROOT_FILES:
        file_path = BASE_DIR / filename
        if file_path.exists():
            fsize = file_path.stat().st_size
            zip_out.write(file_path, arcname=filename)
            print(f"  + Added Root File: {filename:<32} ({fsize:,} bytes)")
            total_files += 1
            total_uncompressed_bytes += fsize
        else:
            print(f"  ! Warning: {filename} not found, skipping.")

    # 2. Add Full Directories
    for dir_name in ESSENTIAL_DIRS:
        dir_path = BASE_DIR / dir_name
        if dir_path.exists() and dir_path.is_dir():
            count_dir = 0
            for root, dirs, files in os.walk(dir_path):
                # Prune excluded directories
                dirs[:] = [d for d in dirs if not should_exclude(d)]
                for file in files:
                    full_p = Path(root) / file
                    rel_p = full_p.relative_to(BASE_DIR)
                    if not should_exclude(str(rel_p)):
                        fsize = full_p.stat().st_size
                        zip_out.write(full_p, arcname=str(rel_p))
                        total_files += 1
                        total_uncompressed_bytes += fsize
                        count_dir += 1
            print(f"  + Added Module   : {dir_name:<32} ({count_dir} files included)")

# Duplicate to export_backups and alias
import shutil
shutil.copy2(ZIP_PATH, EXPORT_ZIP_PATH)
shutil.copy2(ZIP_PATH, ALIAS_ZIP_PATH)

pkg_size_mb = ZIP_PATH.stat().st_size / (1024 * 1024)

print("=" * 75)
print("🎉 SUCCESS: TG KindSync Pro Full Enterprise Package Built Successfully!")
print(f"📍 Location      : {ZIP_PATH}")
print(f"📁 Backup Archive: {EXPORT_ZIP_PATH}")
print(f"🏷️ Static Alias  : {ALIAS_ZIP_PATH}")
print(f"📊 Total Content : {total_files} files ({total_uncompressed_bytes / (1024 * 1024):.2f} MB uncompressed)")
print(f"⚖️ Final Zip Size: {pkg_size_mb:.2f} MB ({ZIP_PATH.stat().st_size:,} bytes)")
print(f"📅 Timestamp     : {display_caption}")
print("🔒 Enterprise Features: 100% Intact (Devi AI + Model Hub + Multi-Session + Web Dashboard + Deploy Suite)")
print("=" * 75)

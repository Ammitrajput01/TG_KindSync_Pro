import os
import sys
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent

# Names of the two distinct backup packages
FRIEND_ZIP_NAME = "TG_Forwarder_Pro_v14_FOR_FRIEND.zip"
OWNER_ZIP_NAME = "TG_Forwarder_Pro_v14_OWNER_FULL_BACKUP.zip"

FRIEND_ZIP_PATH = BASE_DIR / FRIEND_ZIP_NAME
OWNER_ZIP_PATH = BASE_DIR / OWNER_ZIP_NAME

# Files strictly required for friend (Standalone, Zero Clutter, Zero Private Leaks)
FRIEND_FILES = [
    "START_BOT.bat",
    "EASY_SETUP.bat",
    "tg_kind_mode_v14.py",
    "main.py",
    "quick_setup.py",
    "requirements.txt",
    ".env.example",
    "kind_doctor_thumb.jpg",
    "HOW_TO_RUN_FOR_FRIEND.txt",
    "README.md",
]

# Patterns/folders to exclude from Owner Full Backup
OWNER_EXCLUDE_DIRS = {
    ".venv",
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "scratch",
}

OWNER_EXCLUDE_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".tmp",
    ".log",
}

def make_friend_backup():
    print("=" * 80)
    print("📦 [1/2] CREATING FRIEND STANDALONE RELEASE PACKAGE")
    print(f"👉 Target File: {FRIEND_ZIP_NAME}")
    print("=" * 80)

    if FRIEND_ZIP_PATH.exists():
        try:
            FRIEND_ZIP_PATH.unlink()
        except Exception:
            pass

    missing = [f for f in FRIEND_FILES if not (BASE_DIR / f).exists()]
    if missing:
        print(f"[ERROR] Missing required files: {missing}")
        return False

    with zipfile.ZipFile(FRIEND_ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for fname in FRIEND_FILES:
            fpath = BASE_DIR / fname
            zf.write(fpath, arcname=fname)
            sz = fpath.stat().st_size
            print(f"  + Added: {fname:<30} ({sz:,} bytes)")

    total_sz = FRIEND_ZIP_PATH.stat().st_size
    print("-" * 80)
    print(f"✔ FRIEND BACKUP COMPLETE: {FRIEND_ZIP_NAME}")
    print(f"📁 Path: {FRIEND_ZIP_PATH}")
    print(f"⚖️ Size: {total_sz / (1024 * 1024):.2f} MB ({total_sz:,} bytes)")
    print("🛡️ Security: Zero personal .session files, Zero .sqlite history, Zero .venv clutter!")
    print("=" * 80)
    return True

def make_owner_backup():
    print("\n" + "=" * 80)
    print("👑 [2/2] CREATING DR. AMIT (OWNER) COMPLETE MASTER BACKUP")
    print(f"👉 Target File: {OWNER_ZIP_NAME}")
    print("=" * 80)

    if OWNER_ZIP_PATH.exists():
        try:
            OWNER_ZIP_PATH.unlink()
        except Exception:
            pass

    added_count = 0
    total_uncompressed_bytes = 0

    with zipfile.ZipFile(OWNER_ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for root, dirs, files in os.walk(BASE_DIR):
            # Prune excluded directories in-place so os.walk skips them
            dirs[:] = [d for d in dirs if d not in OWNER_EXCLUDE_DIRS and not d.endswith(".egg-info")]

            rel_dir = os.path.relpath(root, BASE_DIR)

            for f in files:
                # Do not include zip files into the backup (avoid recursion)
                if f.endswith(".zip"):
                    continue
                # Skip temporary extensions
                _, ext = os.path.splitext(f)
                if ext in OWNER_EXCLUDE_EXTENSIONS:
                    continue

                full_path = Path(root) / f
                if rel_dir == ".":
                    arcname = f
                else:
                    arcname = os.path.join(rel_dir, f)

                try:
                    sz = full_path.stat().st_size
                    zf.write(full_path, arcname=arcname)
                    added_count += 1
                    total_uncompressed_bytes += sz
                except Exception as ex:
                    print(f"  [!] Skipping {f}: {ex}")

    total_sz = OWNER_ZIP_PATH.stat().st_size
    print("-" * 80)
    print(f"✔ OWNER MASTER BACKUP COMPLETE: {OWNER_ZIP_NAME}")
    print(f"📁 Path: {OWNER_ZIP_PATH}")
    print(f"📦 Files Packaged: {added_count} files ({total_uncompressed_bytes / (1024 * 1024):.2f} MB uncompressed)")
    print(f"⚖️ Final Compressed Size: {total_sz / (1024 * 1024):.2f} MB ({total_sz:,} bytes)")
    print("💎 Includes: Active .env, history_core.sqlite, .session logins, devi, .agents AI hub, tests, web dashboard!")
    print("=" * 80)
    return True

def sync_backups():
    import shutil
    sync_targets = [
        Path(r"C:\TGForwarder_Backups"),
        Path(r"C:\Users\Ammit\Desktop")
    ]
    for target in sync_targets:
        if target.exists():
            try:
                shutil.copy2(FRIEND_ZIP_PATH, target / FRIEND_ZIP_NAME)
                shutil.copy2(OWNER_ZIP_PATH, target / OWNER_ZIP_NAME)
                print(f"  🚀 Synced both backups to: {target}")
            except Exception as e:
                print(f"  [!] Sync notice for {target}: {e}")

def main():
    ok1 = make_friend_backup()
    ok2 = make_owner_backup()

    if ok1 and ok2:
        print("\n🎉 BOTH BACKUPS WERE GENERATED SUCCESSFULLY!")
        print("🔄 Syncing to backup vaults...")
        sync_backups()
        print("\n✅ All backups are fully synced and ready to use!")

if __name__ == "__main__":
    main()

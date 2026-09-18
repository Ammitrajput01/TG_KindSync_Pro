"""
TG KindSync Pro — Auto-Updater & Code Sync Engine
Allows both developers and end-users (friends) to sync, update, and publish code with 1-click.
Safeguards user credentials (.env), Telethon sessions (*.session), and SQLite databases (*.sqlite).
"""

import os
import sys
import json
import zipfile
import shutil
import subprocess
import urllib.request
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
VERSION_FILE = BASE_DIR / "version.json"
UPDATE_PACK_FILE = BASE_DIR / "update_pack.zip"

PROTECTED_PATHS = {
    ".env",
    ".env.backup",
    "history_core.sqlite",
    "history_core.sqlite-wal",
    "history_core.sqlite-shm",
    "session_forwarder.session",
    "session_forwarder.session-journal",
    "member_backups",
    "data",
    "logs",
    "__pycache__"
}

def load_version_info() -> dict:
    if VERSION_FILE.exists():
        try:
            with open(VERSION_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"app_name": "TG KindSync Pro", "version": "14.5.0", "release_tag": "v14.5"}

def is_git_repository() -> bool:
    git_dir = BASE_DIR / ".git"
    if not git_dir.exists():
        return False
    try:
        res = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=BASE_DIR, capture_output=True, text=True)
        return res.returncode == 0
    except Exception:
        return False

def check_git_updates() -> bool:
    try:
        subprocess.run(["git", "fetch", "--quiet"], cwd=BASE_DIR, timeout=10)
        res = subprocess.run(["git", "status", "-uno"], cwd=BASE_DIR, capture_output=True, text=True)
        return "Your branch is behind" in res.stdout
    except Exception:
        return False

def perform_git_update() -> bool:
    print("[*] Performing one-click Git sync...")
    try:
        res = subprocess.run(["git", "pull", "--no-rebase"], cwd=BASE_DIR, capture_output=True, text=True)
        print(res.stdout)
        if res.returncode == 0:
            print("[✔] Git repository successfully updated to latest commit!")
            return True
        else:
            print(f"[!] Git pull warning: {res.stderr}")
            return False
    except Exception as e:
        print(f"[!] Error during git pull: {e}")
        return False

def apply_zip_update(zip_path: Path) -> bool:
    print(f"[*] Unpacking updates from {zip_path.name}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.namelist():
                # Prevent overwriting protected user credentials or databases
                first_part = member.split('/')[0].split('\\')[0]
                if first_part in PROTECTED_PATHS or member.endswith('.session') or member.endswith('.sqlite') or member == ".env":
                    continue
                target_path = BASE_DIR / member
                if member.endswith('/'):
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as source, open(target_path, "wb") as target:
                        shutil.copyfileobj(source, target)
        print("[✔] All code files, templates, and scripts updated safely!")
        return True
    except Exception as e:
        print(f"[!] Error extracting update package: {e}")
        return False

def install_dependencies():
    req_file = BASE_DIR / "requirements.txt"
    if req_file.exists():
        print("[*] Synchronizing Python dependencies...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file), "--quiet"], cwd=BASE_DIR, check=True)
            print("[✔] Dependencies verified and up-to-date.")
        except Exception as e:
            print(f"[!] Dependency check notice: {e}")

def run_update():
    v = load_version_info()
    print("=" * 65)
    print(f"🚀 TG KINDSYNC PRO — ONE-CLICK AUTO-UPDATER & CODE SYNC")
    print(f"Current Installed Version: {v.get('version')} ({v.get('release_tag')})")
    print("=" * 65)

    # Strategy 1: If using Git with remote
    if is_git_repository():
        print("[*] Detected local Git repository.")
        has_remote = False
        try:
            r = subprocess.run(["git", "remote"], cwd=BASE_DIR, capture_output=True, text=True)
            has_remote = bool(r.stdout.strip())
        except Exception:
            pass

        if has_remote:
            updated = perform_git_update()
            if updated:
                install_dependencies()
                v_new = load_version_info()
                print("\n" + "=" * 65)
                print(f"🎉 SUCCESS: TG KindSync Pro updated to {v_new.get('version')}!")
                print("=" * 65)
                return

    # Strategy 2: If offline update_pack.zip exists in directory
    if UPDATE_PACK_FILE.exists():
        print(f"[*] Found offline update package: {UPDATE_PACK_FILE.name}")
        applied = apply_zip_update(UPDATE_PACK_FILE)
        if applied:
            install_dependencies()
            try:
                UPDATE_PACK_FILE.unlink() # Clean up package after applying
            except Exception:
                pass
            v_new = load_version_info()
            print("\n" + "=" * 65)
            print(f"🎉 SUCCESS: TG KindSync Pro updated to {v_new.get('version')}!")
            print("=" * 65)
            return

    # Strategy 3: Check Remote Cloud URL if configured in .env
    custom_url = os.getenv("UPDATE_SOURCE_URL", "").strip()
    if custom_url:
        print(f"[*] Checking remote cloud server: {custom_url}...")
        try:
            dl_path = BASE_DIR / "temp_update.zip"
            urllib.request.urlretrieve(custom_url, str(dl_path))
            if dl_path.exists() and dl_path.stat().st_size > 1000:
                applied = apply_zip_update(dl_path)
                dl_path.unlink()
                if applied:
                    install_dependencies()
                    v_new = load_version_info()
                    print("\n" + "=" * 65)
                    print(f"🎉 SUCCESS: TG KindSync Pro updated to {v_new.get('version')}!")
                    print("=" * 65)
                    return
        except Exception as e:
            print(f"[!] Cloud check notice: {e}")

    print("\n[ℹ] Your TG KindSync Pro code is currently running the latest available build.")
    print("Protected user data (.env, sessions, and SQLite databases) were preserved.")
    print("=" * 65)

def publish_update():
    """Developer tool: Bundles updated code for friends or GitHub release."""
    v = load_version_info()
    current_ver = v.get("version", "14.5.0")
    print("=" * 65)
    print(f"📦 TG KINDSYNC PRO — DEVELOPER PUBLISH & RELEASE PACKAGER")
    print(f"Current Version: {current_ver}")
    print("=" * 65)
    
    new_ver = input(f"Enter new version number (Press Enter to keep [{current_ver}]): ").strip()
    if not new_ver:
        new_ver = current_ver

    tag_ver = f"v{new_ver[:4]}" if not new_ver.startswith("v") else new_ver

    # Update version.json
    v["version"] = new_ver
    v["release_tag"] = tag_ver
    from datetime import datetime
    v["release_date"] = datetime.now().strftime("%Y-%m-%d")
    with open(VERSION_FILE, "w", encoding="utf-8") as f:
        json.dump(v, f, indent=2)
    print(f"[✔] Updated version.json -> {new_ver} ({tag_ver})")

    # Build update_pack.zip
    print(f"[*] Packaging clean update bundle -> {UPDATE_PACK_FILE.name}...")
    essential_exts = {".py", ".bat", ".txt", ".json", ".md", ".ps1", ".jpg", ".png"}
    count = 0
    with zipfile.ZipFile(UPDATE_PACK_FILE, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for root, dirs, files in os.walk(BASE_DIR):
            # Ignore git, cache, virtualenvs, backups
            dirs[:] = [d for d in dirs if d not in {".git", ".venv", "venv", "__pycache__", "member_backups", "data", "logs"}]
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                rel_path = os.path.relpath(os.path.join(root, file), BASE_DIR)
                
                # Exclude protected and secrets
                first_comp = rel_path.split(os.sep)[0]
                if first_comp in PROTECTED_PATHS or file.endswith(".session") or file.endswith(".sqlite") or file == ".env" or file == UPDATE_PACK_FILE.name:
                    continue
                if ext in essential_exts or file == "Dockerfile":
                    zf.write(os.path.join(root, file), arcname=rel_path)
                    count += 1

    print(f"[✔] Packaged {count} files into {UPDATE_PACK_FILE.name} ({UPDATE_PACK_FILE.stat().st_size // 1024} KB).")
    print("\n💡 Friends can either:")
    print(" 1. Run UPDATE_KINDSYNC.bat with this update_pack.zip in their folder")
    print(" 2. Or pull from Git if you push to your GitHub repository.")
    print("=" * 65)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--publish", "-p", "publish"):
        publish_update()
    else:
        run_update()

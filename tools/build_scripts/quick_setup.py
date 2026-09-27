#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 Telegram Forwarder Pro - 1-Click Interactive Setup Wizard
Guides users through setting up Telegram credentials and launch.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Fix Windows console UTF-8 & cp1252 character map issues
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    from dotenv import load_dotenv, set_key
except ImportError:
    # If dotenv is not yet available, provide fallback
    load_dotenv = None
    set_key = None

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_header():
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{CYAN}{BOLD}=============================================================================={RESET}")
    print(f"{CYAN}{BOLD}      🚀 TELEGRAM FORWARDER PRO V14.0 — 1-CLICK EASY SETUP WIZARD             {RESET}")
    print(f"{CYAN}{BOLD}=============================================================================={RESET}")
    print(f"{YELLOW}Bhai bas 2 minute me setup complete ho jayega. Niche details fill karo:{RESET}\n")

def read_env_file(filepath=".env"):
    config = {}
    if not os.path.exists(filepath):
        return config
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    config[k.strip()] = v.strip().strip("'\"")
    except Exception:
        pass
    return config

def write_env_key(filepath, key, value):
    lines = []
    found = False
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#") and "=" in stripped:
                    k, _ = stripped.split("=", 1)
                    if k.strip() == key:
                        lines.append(f"{key}={value}\n")
                        found = True
                        continue
                lines.append(line)
    if not found:
        lines.append(f"{key}={value}\n")

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)

def prompt_value(prompt_text, current_val="", required=True):
    while True:
        display_current = f" [Current: {current_val}]" if current_val and current_val != "0" else ""
        user_input = input(f"{BOLD}{prompt_text}{display_current}: {RESET}").strip()
        
        if not user_input:
            if current_val and current_val != "0":
                return current_val
            if not required:
                return ""
            print(f"{RED}⚠️ Ye field compulsory hai! Please value daalo.{RESET}")
            continue
        return user_input

def main():
    print_header()

    env_path = Path(".env")
    env_example = Path(".env.example")

    # Step 1: Ensure .env exists
    if not env_path.exists():
        if env_example.exists():
            shutil.copy(str(env_example), str(env_path))
            print(f"{GREEN}✔ .env file automatically ban gayi (.env.example se copy kar li){RESET}")
        else:
            with open(env_path, "w", encoding="utf-8") as f:
                f.write("API_ID=36193727\nAPI_HASH=fef19b9b1434a3e66b009fd31053200b\nSOURCE_CHAT=0\nTARGET_CHAT=0\nSOURCE_TOPIC=0\nTARGET_TOPIC=0\n")
            print(f"{GREEN}✔ Fresh .env file create ho gayi!{RESET}")

    current_env = read_env_file(".env")

    # Step 2: Ask for API_ID & API_HASH
    print(f"\n{BOLD}[1/4] Telegram API Credentials Setup{RESET}")
    print(f"{YELLOW}👉 Telegram connect hone ke liye API_ID aur API_HASH zaroori hain.{RESET}")
    print(f"{CYAN}👉 Agar aapke paas nahi hain, toh https://my.telegram.org par phone login karke 'API development tools' se 1 min me free le sakte hain.{RESET}")
    
    def_id = current_env.get("API_ID", "").strip()
    def_hash = current_env.get("API_HASH", "").strip()

    api_id = prompt_value("👉 Apna API_ID enter karo (numbers only)", def_id)
    api_hash = prompt_value("👉 Apna API_HASH enter karo (32-character string)", def_hash)

    # Step 3: Ask for Source & Target Chat
    print(f"\n{BOLD}[2/4] Forwarding Routing Setup{RESET}")
    print(f"{YELLOW}👉 Channel link (https://t.me/...), username (@channel), ya ID (-100...) daal sakte ho.{RESET}")
    
    source_chat = prompt_value("👉 SOURCE CHAT (jahan se messages forward karne hain)", current_env.get("SOURCE_CHAT", "0"))
    target_chat = prompt_value("👉 TARGET CHAT (jahan messages bhejne hain)", current_env.get("TARGET_CHAT", "0"))

    # Step 4: Save to .env
    write_env_key(".env", "API_ID", api_id)
    write_env_key(".env", "API_HASH", api_hash)
    write_env_key(".env", "SOURCE_CHAT", source_chat)
    write_env_key(".env", "TARGET_CHAT", target_chat)
    print(f"\n{GREEN}{BOLD}✔ Saari settings `.env` file me successfully save ho gayi!{RESET}")

    # Step 5: Session Check (Fresh Account Login)
    session_files = list(Path(".").glob("*.session*"))
    if session_files:
        print(f"\n{BOLD}[3/4] Telegram Account Session Check{RESET}")
        print(f"{YELLOW}Folder me pehle ke session files detect hue hain.{RESET}")
        reset_choice = input(f"{BOLD}👉 Kya aap naye Telegram number se fresh login karna chahte hain? (y/n) [y]: {RESET}").strip().lower()
        if reset_choice in ("", "y", "yes"):
            removed_count = 0
            for sf in session_files:
                try:
                    sf.unlink()
                    removed_count += 1
                except Exception:
                    pass
            print(f"{GREEN}✔ {removed_count} puraane session files reset kar diye gaye. Ab fresh login hoga!{RESET}")
        else:
            print(f"{YELLOW}✔ Existing session maintain rakha gaya.{RESET}")

    # Step 6: Start Bot
    print(f"\n{BOLD}[4/4] Ready to Launch! 🚀{RESET}")
    start_choice = input(f"{BOLD}👉 Kya abhi Forwarder bot start karein? (y/n) [y]: {RESET}").strip().lower()
    if start_choice in ("", "y", "yes"):
        print(f"\n{GREEN}{BOLD}🚀 Starting Telegram Forwarder Engine...{RESET}")
        launcher = "START_BOT.bat" if os.path.exists("START_BOT.bat") else ("1_START_ALL.bat" if os.path.exists("1_START_ALL.bat") else None)
        if launcher and os.name == "nt":
            subprocess.Popen(["cmd.exe", "/c", launcher], creationflags=subprocess.CREATE_NEW_CONSOLE)
            print(f"{GREEN}✔ Forwarder Engine new window me start ho gaya hai!{RESET}")
        else:
            print(f"{CYAN}To run manually anytime, double-click 'START_BOT.bat'{RESET}")
    else:
        print(f"\n{CYAN}Koi baat nahi! Jab bhi start karna ho, folder me {BOLD}START_BOT.bat{RESET}{CYAN} par double click kar lena!{RESET}")

    print(f"\n{GREEN}=============================================================================={RESET}")
    print(f"{GREEN}{BOLD}            SETUP COMPLETE! MAJE KARO! 😉                                     {RESET}")
    print(f"{GREEN}=============================================================================={RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print(f"\n{YELLOW}Setup cancelled by user.{RESET}")

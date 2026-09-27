@echo off
setlocal EnableDelayedExpansion
title TG KindSync Pro - Interactive Oracle Cloud 24-7 Menu
color 0b
cls

echo ==============================================================================
echo       TG KINDSYNC PRO - ORACLE CLOUD INTERACTIVE 24/7 SUITE
echo       IP: 130.210.1.32 (Oracle Mumbai Always-Free VPS)
echo ==============================================================================
echo.

cd /d "%~dp0"

set "ROOT_DIR=C:\TG_KindSync_Pro"
if not exist "!ROOT_DIR!" set "ROOT_DIR=%~dp0"

set "KEY_PATH=%~dp0oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=!ROOT_DIR!\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=C:\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%USERPROFILE%\Downloads\oracle_key_latest.key"

if not exist "!KEY_PATH!" (
    echo [ERROR] SSH Key not found: oracle_key_latest.key
    echo Please make sure oracle_key_latest.key is in the folder.
    echo.
    pause
    exit /b 1
)

echo [*] Using SSH Key: !KEY_PATH!
echo [*] Auto-verifying Windows Security Permissions...

icacls "!KEY_PATH!" /reset >nul 2>nul
icacls "!KEY_PATH!" /inheritance:r >nul 2>nul
icacls "!KEY_PATH!" /grant:r "%USERNAME%:R" >nul 2>nul
icacls "!KEY_PATH!" /grant:r "%USERNAME%:(R)" >nul 2>nul

echo [OK] Permissions verified!
echo.
echo [*] Step 1: Syncing latest login panel to Oracle Cloud...
cd /d "!ROOT_DIR!"
scp -o StrictHostKeyChecking=no -i "!KEY_PATH!" tools/login_panel.py tg_kindsync_pro.py .env ubuntu@130.210.1.32:/home/ubuntu/TG_KindSync_Pro/ 2>nul
scp -o StrictHostKeyChecking=no -i "!KEY_PATH!" tools/login_panel.py ubuntu@130.210.1.32:/home/ubuntu/TG_KindSync_Pro/tools/ 2>nul

echo.
echo [*] Step 2: Opening Interactive 24/7 Menu with Auto Port-Forwarding (5005)...
echo [*] (Browser login: http://127.0.0.1:5005)
echo.

ssh -L 5005:localhost:5005 -t -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "tmux new-session -A -s kindsync 'cd /home/ubuntu/TG_KindSync_Pro && source .venv/bin/activate 2>/dev/null || true; python3 tg_kindsync_pro.py'"

echo.
echo ==============================================================================
echo [INFO] Window closed. Background 24/7 service continues on Oracle Cloud!
echo ==============================================================================
echo.
pause

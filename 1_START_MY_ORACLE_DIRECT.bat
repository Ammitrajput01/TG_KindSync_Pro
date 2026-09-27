@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title TG KindSync Pro - Direct Oracle Cloud Interactive Terminal (24/7)
color 0b
cd /d "%~dp0"

echo ==============================================================================
echo       TG KINDSYNC PRO -- DIRECT ORACLE CLOUD TERMINAL (24/7)
echo       IP: 130.210.1.32 (Oracle Mumbai Always-Free VPS)
echo       Developer ^& Owner: Dr. Amit Singh (Kind Doctor)
echo ==============================================================================
echo.

set "KEY_PATH=%~dp0oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=C:\TG_KindSync_Pro\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=C:\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%USERPROFILE%\Downloads\oracle_key_latest.key"

if not exist "!KEY_PATH!" (
    echo [ERROR] SSH Key not found: oracle_key_latest.key
    pause
    exit /b 1
)

:: Auto-fix Windows key permissions
icacls "!KEY_PATH!" /inheritance:r /grant:r "%USERNAME%:R" >nul 2>nul

echo [*] Connecting to your Oracle VPS...
echo [*] Freeing session locks on Oracle VPS...
ssh -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "sudo systemctl stop tg-forwarder 2>/dev/null || true"

echo [*] Launching 24/7 Persistent Terminal (tmux session)...
echo [*] Note: You can safely close your laptop anytime - cloning will continue 24/7 in cloud!
echo.

ssh -L 5005:localhost:5005 -t -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "tmux new-session -A -s kindsync 'cd /home/ubuntu/TG_KindSync_Pro && source .venv/bin/activate 2>/dev/null || true; python3 tg_kindsync_pro.py'"

echo.
echo ==============================================================================
echo Terminal detached. Background cloning continues running 24/7 on Oracle Cloud!
echo To re-view live progress anytime, simply double-click this file again.
echo ==============================================================================
pause

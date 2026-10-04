@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title TG KindSync Pro - 1-Click Oracle VPS Bot Updater
color 0a
cd /d "%~dp0"

echo ==============================================================================
echo       🚀 TG KINDSYNC PRO -- 1-CLICK ORACLE VPS BOT UPDATER
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
icacls "!KEY_PATH!" /reset >nul 2>nul
icacls "!KEY_PATH!" /inheritance:r >nul 2>nul
icacls "!KEY_PATH!" /grant:r "%USERNAME%:R" >nul 2>nul

echo [*] Connecting to Oracle VPS (130.210.1.32)...
echo [*] Pulling latest updates from GitHub (main branch)...
echo.

ssh -o StrictHostKeyChecking=no -o ConnectTimeout=15 -i "!KEY_PATH!" ubuntu@130.210.1.32 "cd /home/ubuntu/TG_KindSync_Pro && git pull origin main && sudo systemctl restart tg-kinddoc-bot && echo '============================================' && echo '✅ Oracle Bot Daemon Updated & Restarted Successfully!' && echo '============================================'"

if errorlevel 1 (
    echo.
    echo ⚠️ [ERROR] Could not connect to Oracle VPS. Please verify VPS is online.
) else (
    echo.
    echo 🎉 All bot & scanner updates are now LIVE on your Oracle VPS!
)

echo.
pause

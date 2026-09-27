@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title 🚀 TG KINDSYNC PRO V14.5 — 1-CLICK ALL SERVICES LAUNCHER
cls

echo ==============================================================================
echo       🩺 TG KINDSYNC PRO V14.5 + KIND DOCTOR BOT (ALL-IN-ONE MASTER)
echo ==============================================================================
echo.
echo [*] Cleaning any stale locks or background processes...
if exist "engine.lock" (
    del /f /q "engine.lock" >nul 2>nul
)

echo [*] Launching services in visible windows:
echo.
echo     [1/3] 🚀 TG KindSync Forwarder Engine...
start "Telegram Forwarder Engine" cmd /k "%~dp0START_BOT.bat"
ping 127.0.0.1 -n 3 >nul

echo     [2/3] 🩺 Kind Doctor Telegram Bot Daemon (@KindDoc_bot)...
start "Kind Doctor Bot Daemon" cmd /k "%~dp0START_KIND_DOCTOR_BOT.bat"
ping 127.0.0.1 -n 2 >nul

echo     [3/3] 🌐 DEVI Web Dashboard (http://localhost:8080)...
start "DEVI Web Dashboard" cmd /k "%~dp03_START_DEVI_DASHBOARD.bat"

echo.
echo ==============================================================================
echo [OK] All 3 services launched successfully!
echo.
echo      1. Telegram Forwarder Engine (Main Menu)
echo      2. Kind Doctor Bot Daemon
echo      3. DEVI Web Dashboard : http://localhost:8080
echo ==============================================================================
echo.
echo Closing launcher in 4 seconds...
ping 127.0.0.1 -n 5 >nul
exit /b 0

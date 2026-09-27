@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
title Kind Doctor Telegram Operator Bot 🩺 (Devi Daemon)
color 0a
cd /d "%~dp0"

echo ==============================================================================
echo       [+] KIND DOCTOR TELEGRAM OPERATOR BOT 🩺
echo       Active Bot: @KindDoc_bot / DEVI Sentinel Daemon
echo       Admins: @Kinddoctor4u (1553619403) ^& @Ammitrajput1 (759038032)
echo ==============================================================================
echo.

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo [*] Starting Kind Doctor Bot Daemon...
echo [*] Press Ctrl+C anytime to stop.
echo.
"%PYTHON_EXE%" -m devi.operator.telegram_bot

pause

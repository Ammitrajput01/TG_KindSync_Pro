@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title 🩺 KIND DOCTOR — LIVE RELAY & SENTINEL BOT DAEMON
cls
echo ==============================================================================
echo           KIND DOCTOR 🩺 — LIVE SUPPORT RELAY + STUDY SENTINEL
echo ==============================================================================
echo.

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

echo [*] Starting Kind Doctor Bot Daemon (@KindDoc_bot)...
python -m devi.operator.telegram_bot
pause

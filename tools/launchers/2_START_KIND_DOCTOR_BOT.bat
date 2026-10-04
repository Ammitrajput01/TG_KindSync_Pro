@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
title Kind Doctor Telegram Operator Bot 🩺 (Devi Daemon)
color 0a
cd /d "%~dp0\..\.."

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

echo [*] Starting Kind Doctor Bot Dedicated Auto-Supervisor...
echo [*] Auto-Restart on crash: ENABLED (Self-Healing)
echo [*] Press Ctrl+C anytime to terminate.
echo.

:SUPERVISOR_LOOP
"%PYTHON_EXE%" -m devi.operator.telegram_bot
set "EXIT_CODE=%ERRORLEVEL%"

if "%EXIT_CODE%"=="0" (
    echo.
    echo [*] Kind Doctor Bot stopped cleanly.
    pause
    exit /b 0
)

echo.
echo [!] Kind Doctor Bot terminated unexpectedly (Code: %EXIT_CODE%).
echo [*] Self-Healing Auto-Supervisor restarting daemon in 3 seconds...
timeout /t 3 /nobreak >nul
echo [*] Restarting Kind Doctor Bot Daemon...
echo.
goto SUPERVISOR_LOOP

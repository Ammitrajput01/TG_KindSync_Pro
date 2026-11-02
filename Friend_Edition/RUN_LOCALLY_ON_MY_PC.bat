@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title TG KINDSYNC PRO -- LOCAL STANDALONE PC EDITION
color 0b
cd /d "%~dp0"

echo ==============================================================================
echo        TG KINDSYNC PRO -- LOCAL STANDALONE PC EDITION
echo        High-Speed Telegram Cloner & Forwarder (100%% Local Execution)
echo        Powered by: Kind Doctor & Team (@Kinddoctor4u)
echo ==============================================================================
echo.

:: 1. Verify Python Installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your system PATH!
    echo.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo IMPORTANT: Make sure to check the box: "Add python.exe to PATH" during installation.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version') do set "PY_VER=%%v"
echo [*] Detected Python environment: !PY_VER!

:: 2. Auto-Install Required Packages
echo [*] Checking and installing required Python libraries...
python -m pip install --quiet --upgrade telethon rich python-dotenv cryptography aiohttp
if %errorlevel% neq 0 (
    echo [WARNING] Pip encountered a warning, continuing with existing installed packages...
)

:: 3. Launch Standalone TG KindSync Pro
echo.
echo ==============================================================================
echo [*] Starting TG KindSync Pro locally on your PC...
echo [*] Your login session and configuration will be saved strictly on this PC.
echo [*] No cloud server or VPS required!
echo ==============================================================================
echo.

python tg_kindsync_pro.py

echo.
echo [INFO] TG KindSync Pro process finished.
pause

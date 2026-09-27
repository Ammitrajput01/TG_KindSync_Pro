@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title 🚀 TG KINDSYNC PRO V14.5 — TELEGRAM FORWARDER
cls

echo ==============================================================================
echo        🩺 TG KINDSYNC PRO V14.5 — TELEGRAM FORWARDER (1-CLICK RUN)
echo        Owner & Developer: Dr. Amit Singh (Kind Doctor)
echo ==============================================================================
echo.

:: 1. Check Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    where py >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo [!] Python is not detected on your computer.
        echo [*] Auto-installing Python via Windows Package Manager [winget]...
        where winget >nul 2>nul
        if %ERRORLEVEL% equ 0 (
            winget install -e --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements
            set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
        )
        where python >nul 2>nul
        if %ERRORLEVEL% neq 0 (
            where py >nul 2>nul
            if %ERRORLEVEL% neq 0 (
                echo.
                echo [ERROR] Python not found. Please install Python from:
                echo         https://www.python.org/downloads/
                echo ⚠️ IMPORTANT: Tick "Add python.exe to PATH" during installation!
                echo.
                pause
                exit /b 1
            )
        )
    )
)

:: 2. Check Virtual Environment & Self-Heal
set NEED_SETUP=0
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python -c "import telethon, aiosqlite, dotenv, rich" >nul 2>nul
    if errorlevel 1 (
        echo [!] Virtual environment needs re-alignment for this machine...
        call .venv\Scripts\deactivate.bat >nul 2>nul
        rmdir /s /q .venv >nul 2>nul
        set NEED_SETUP=1
    )
) else (
    set NEED_SETUP=1
)

if %NEED_SETUP% equ 1 (
    echo [*] Creating clean virtual environment (.venv)...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [!] Could not create .venv, running with system Python...
    ) else (
        call .venv\Scripts\activate.bat
    )
    echo [*] Installing required libraries (one-time setup, please wait)...
    python -m pip install --upgrade pip --quiet
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [!] Fallback installing core libraries...
        pip install telethon aiosqlite python-dotenv Pillow rich psutil qrcode[pil]
    )
)

:: 3. Clean Stale Lock
if exist "engine.lock" (
    del /f /q "engine.lock" >nul 2>nul
)

:: 4. Ensure .env exists with pre-configured verified credentials
if not exist ".env" (
    if exist ".env.example" (
        copy /y ".env.example" ".env" >nul
        echo [*] Initialized .env configuration with verified Telegram MTProto credentials.
    )
)

:: 5. Launch Telegram Forwarder
echo.
echo [OK] Everything verified! Launching Telegram Forwarder...
echo ==============================================================================
echo.
python main.py %*

if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Forwarder stopped with code %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo Program ended. Press any key to exit.
echo ==============================================================================
pause

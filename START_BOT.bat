@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title ?? TG KINDSYNC PRO V14.5 ? ENTERPRISE ENGINE
cls

echo ==============================================================================
echo           TG KINDSYNC PRO V14.5 ? ENTERPRISE MASTER ENGINE
echo ==============================================================================
echo.

:: 1. Check Python
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    where py >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo [!] Python is not installed or not in PATH!
        echo [*] Attempting auto-installation via winget...
        where winget >nul 2>nul
        if %ERRORLEVEL% equ 0 (
            winget install -e --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements
            set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
        )
        where python >nul 2>nul
        if %ERRORLEVEL% neq 0 (
            where py >nul 2>nul
            if %ERRORLEVEL% neq 0 (
                echo [ERROR] Python not found. Please install Python from https://www.python.org/
                echo IMPORTANT: Tick the checkbox "Add python.exe to PATH" during setup!
                echo.
                pause
                exit /b 1
            )
        )
    )
)

:: 2. Check Virtual Environment & Self-Heal if from another PC
set NEED_SETUP=0
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python -c "import telethon, aiosqlite, dotenv, rich" >nul 2>nul
    if errorlevel 1 (
        echo [!] Existing virtual environment is invalid or copied from another PC.
        echo [*] Auto-rebuilding clean environment for this machine...
        call .venv\Scripts\deactivate.bat >nul 2>nul
        rmdir /s /q .venv >nul 2>nul
        set NEED_SETUP=1
    )
) else (
    set NEED_SETUP=1
)

if %NEED_SETUP% equ 1 (
    echo [*] Setting up clean virtual environment .venv...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [!] Could not create .venv, running with system Python...
    ) else (
        call .venv\Scripts\activate.bat
    )
    echo [*] Installing / verifying dependencies - one-time setup, please wait...
    python -m pip install --upgrade pip --quiet
    python -m pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [!] Fallback installing core libraries...
        pip install telethon aiosqlite python-dotenv Pillow rich psutil
    )
)

:: 3. Pillow binary self-heal check (fixes C-extension _imaging errors)
python -c "from PIL import Image" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [*] Re-aligning Pillow image binary for this Python installation...
    pip install --no-cache-dir --force-reinstall pillow >nul 2>nul
)

:: 4. Check .env exists
if not exist ".env" (
    if exist ".env.example" (
        copy /y ".env.example" ".env" >nul
        echo [*] Created fresh .env from template.
    )
)

:: 5. Launch Master Platform
echo.
echo [OK] All systems verified! Launching Telegram Forwarder Engine...
echo ==============================================================================
echo.
python main.py %*

if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Program stopped with exit code: %ERRORLEVEL%
)

echo.
echo ==============================================================================
echo Program ended. Press any key to exit.
echo ==============================================================================
pause

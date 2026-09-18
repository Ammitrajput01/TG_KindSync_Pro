@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title 🚀 TELEGRAM FORWARDER - 1-CLICK EASY SETUP & REPAIR WIZARD
cls

echo ==============================================================================
echo           TELEGRAM FORWARDER PRO - AUTOMATIC 1-CLICK SETUP WIZARD
echo ==============================================================================
echo.

:: 1. Check Python and Auto-Install if missing
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    where py >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo [!] Python detect nahi hua aapke computer par.
        echo [*] Auto-installing Python via Windows Package Manager [winget]...
        where winget >nul 2>nul
        if %ERRORLEVEL% equ 0 (
            winget install -e --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements
            echo.
            echo [*] Python installation attempt complete. Refreshing environment...
            set "PATH=%LOCALAPPDATA%\Programs\Python\Python311;%LOCALAPPDATA%\Programs\Python\Python311\Scripts;%PATH%"
        )
        where python >nul 2>nul
        if %ERRORLEVEL% neq 0 (
            where py >nul 2>nul
            if %ERRORLEVEL% neq 0 (
                echo [ERROR] Python install nahi mila.
                echo.
                echo Please follow these simple steps:
                echo 1. Download Python: https://www.python.org/downloads/
                echo 2. Setup run karte waqt 'Add python.exe to PATH' checkbox TICK zaroor karein!
                echo.
                pause
                exit /b 1
            )
        )
    )
)

:: 2. Check Virtual Environment & Self-Heal if from another PC
set NEED_SETUP=0
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -c "import telethon, aiosqlite, dotenv, rich" >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo [!] Existing virtual environment is invalid or copied from another PC.
        echo [*] Auto-rebuilding clean environment for this machine...
        rmdir /s /q .venv >nul 2>nul
        set NEED_SETUP=1
    ) else (
        call .venv\Scripts\activate.bat
    )
) else (
    set NEED_SETUP=1
)

if %NEED_SETUP% equ 1 (
    echo [1/3] Creating fresh virtual environment .venv...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [!] Virtual environment failed, using system Python...
    ) else (
        call .venv\Scripts\activate.bat
    )
)

:: 3. Install / Reinstall / Update all libraries
echo [2/3] Verifying and updating all dependencies...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --upgrade
if %ERRORLEVEL% neq 0 (
    echo [!] Fallback installing core libraries...
    pip install telethon aiosqlite python-dotenv Pillow rich psutil qrcode[pil]
)

:: 4. Check Pillow binary integrity (C-extension _imaging fix)
python -c "from PIL import Image" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [*] Re-aligning Pillow image binary for this machine...
    pip install --no-cache-dir --force-reinstall pillow >nul 2>nul
)

:: 5. Create .env from template if missing
if not exist ".env" (
    if exist ".env.example" (
        copy /y ".env.example" ".env" >nul
        echo [*] Created .env configuration template.
    )
)

:: 6. Run Interactive Setup Wizard
echo.
echo [3/3] Starting Interactive Setup Wizard...
echo ==============================================================================
echo.
python quick_setup.py

pause

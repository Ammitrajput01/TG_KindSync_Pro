@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title [5/5] INSTALL DEPENDENCIES
cls
echo ==============================================================================
echo                 INSTALL / REFRESH PYTHON DEPENDENCIES
echo ==============================================================================
echo.

if not exist .venv (
    echo Creating virtual environment .venv...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip --quiet

echo Installing project requirements...
python -m pip install -r requirements.txt

:: Check and ensure Pillow binary is clean
python -c "from PIL import Image" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [*] Re-aligning Pillow image binary for this machine...
    pip install --no-cache-dir --force-reinstall pillow >nul 2>nul
)

echo.
echo ==============================================================================
echo Dependencies successfully verified and installed!
echo ==============================================================================
pause

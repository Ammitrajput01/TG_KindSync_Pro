@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title 🚀 TG KINDSYNC PRO — 1-CLICK AUTO-UPDATER
cls

echo ==============================================================================
echo           TG KINDSYNC PRO — 1-CLICK CODE SYNC + AUTO-UPDATER
echo ==============================================================================
echo.
echo [*] Checking for latest updates and syncing code...
echo [*] Protecting your .env configuration, session logins, and databases...
echo.

python tools\updater.py

echo.
echo ==============================================================================
echo [*] Update process finished. Press any key to exit or launch.
pause

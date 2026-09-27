@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title TG KINDSYNC PRO V14.5 -- MASTER CONTROL CENTER
color 0b
cd /d "%~dp0"

:MAIN_MENU
cls
echo ==============================================================================
echo        TG KINDSYNC PRO V14.5 -- MASTER CONTROL CENTER (1-CLICK)
echo        Developer ^& Owner: Dr. Amit Singh (Kind Doctor)
echo        Branding: Kind Doctor ^& Team -- Telegram: @Kinddoctor4u
echo ==============================================================================
echo.
echo   [1] Launch Local Engine (Forwarder, Cloner, Indexer, Splitter)
echo   [2] Connect to Oracle Cloud VPS Terminal (Interactive Cloner Shell)
echo   [3] Sync Single Session to Oracle VPS ^& Restart 24/7 Autopilot
echo   [4] Open DEVI Sentinel Web Dashboard (Port 8080 Live Monitor)
echo   [5] Open Friend Edition Folder
echo   [6] Quick Setup ^& Virtual Environment Self-Heal
echo.
echo   [0] Exit
echo ==============================================================================
echo.
set /p "CHOICE=Enter your choice [1-6 or 0]: "

if "%CHOICE%"=="1" goto RUN_LOCAL
if "%CHOICE%"=="2" goto RUN_ORACLE_SHELL
if "%CHOICE%"=="3" goto RUN_ORACLE_SYNC
if "%CHOICE%"=="4" goto RUN_DASHBOARD
if "%CHOICE%"=="5" goto OPEN_FRIEND_FOLDER
if "%CHOICE%"=="6" goto RUN_SETUP
if "%CHOICE%"=="0" exit /b 0

echo [!] Invalid choice. Please select from 1 to 6 or 0.
timeout /t 2 >nul
goto MAIN_MENU

:RUN_LOCAL
cls
echo [*] Launching TG KindSync Pro Engine locally...
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    python main.py
) else (
    python main.py
)
pause
goto MAIN_MENU

:RUN_ORACLE_SHELL
cls
set "KEY_PATH=%~dp0oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=C:\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%USERPROFILE%\Downloads\oracle_key_latest.key"
echo [*] Connecting to Oracle Cloud VPS (130.210.1.32)...
ssh -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32
pause
goto MAIN_MENU

:RUN_ORACLE_SYNC
cls
echo ==============================================================================
echo       TG KINDSYNC PRO - CLEAN SINGLE SESSION SYNC TO ORACLE (24/7)
echo       IP: 130.210.1.32 (Oracle Mumbai Always-Free VPS)
echo ==============================================================================
set "KEY_PATH=%~dp0oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=C:\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%USERPROFILE%\Downloads\oracle_key_latest.key"

echo [*] Step 1/3: Cleaning up old dummy sessions on Oracle Cloud...
ssh -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "mkdir -p /home/ubuntu/TG_KindSync_Pro/logs /home/ubuntu/TG_KindSync_Pro/data && rm -f /home/ubuntu/TG_KindSync_Pro/session_account*.session /home/ubuntu/TG_KindSync_Pro/session_bot_scanner.session"

echo.
echo [*] Step 2/3: Uploading your 100%% logged-in session_forwarder.session ^& updated engine...
scp -o StrictHostKeyChecking=no -i "!KEY_PATH!" -r session_forwarder.session .env tg_kindsync_pro.py web_dashboard.py main.py requirements.txt tools ubuntu@130.210.1.32:/home/ubuntu/TG_KindSync_Pro/

echo.
echo [*] Step 3/3: Restarting 24/7 background services on Oracle VPS...
ssh -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "sudo systemctl daemon-reload && sudo systemctl restart tg-forwarder tg-kinddoc-bot tg-dashboard 2>/dev/null || sudo systemctl restart tg-forwarder; sudo systemctl status tg-forwarder --no-pager"

echo.
echo [SUCCESS] SYNC COMPLETE!
pause
goto MAIN_MENU

:RUN_DASHBOARD
cls
echo ==============================================================================
echo       TG KINDSYNC PRO - DEVI SENTINEL MISSION CONTROL WEB DASHBOARD
echo       Connecting Secure Tunnel to Oracle VPS (130.210.1.32)...
echo ==============================================================================
set "KEY_PATH=%~dp0oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=C:\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%USERPROFILE%\Downloads\oracle_key_latest.key"

echo [*] Opening Dashboard in default browser: http://127.0.0.1:8080
start http://127.0.0.1:8080
echo [*] Login Credentials: Amit / Amit@123
echo [*] Keep this window open while using the dashboard.
echo.
ssh -N -L 8080:127.0.0.1:8080 -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32
pause
goto MAIN_MENU

:OPEN_FRIEND_FOLDER
start "" "%~dp0Friend_Edition"
goto MAIN_MENU

:RUN_SETUP
cls
if exist "tools\launchers\EASY_SETUP.bat" (
    call "tools\launchers\EASY_SETUP.bat"
) else if exist "EASY_SETUP.bat" (
    call "EASY_SETUP.bat"
) else (
    echo [*] Installing required packages...
    python -m pip install -r requirements.txt
)
goto MAIN_MENU

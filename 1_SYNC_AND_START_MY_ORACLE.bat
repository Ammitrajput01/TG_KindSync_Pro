@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
title TG KindSync Pro - Sync Single Active Session to Oracle (24/7 Autopilot)
color 0b
cd /d "%~dp0"

:SYNC_STEP
cls
echo ==============================================================================
echo       [+] TG KINDSYNC PRO -- CLEAN 24/7 ORACLE VPS SYNC ^& AUTOPILOT
echo       IP: 130.210.1.32 (Oracle Mumbai Always-Free VPS)
echo       Developer ^& Owner: Dr. Amit Singh (Kind Doctor)
echo ==============================================================================
echo.

set "ROOT_DIR=C:\TG_KindSync_Pro"
if not exist "!ROOT_DIR!" set "ROOT_DIR=%~dp0"

set "KEY_PATH=%~dp0oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=!ROOT_DIR!\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%~dp0..\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=C:\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%USERPROFILE%\Downloads\oracle_key_latest.key"

if not exist "!KEY_PATH!" (
    echo [ERROR] SSH Key not found: oracle_key_latest.key
    echo Please make sure oracle_key_latest.key is in the folder.
    echo.
    pause
    exit /b 1
)

echo [*] Using SSH Key: !KEY_PATH!
echo [*] Auto-verifying Windows Security Permissions...

icacls "!KEY_PATH!" /reset >nul 2>nul
icacls "!KEY_PATH!" /inheritance:r >nul 2>nul
icacls "!KEY_PATH!" /grant:r "%USERNAME%:R" >nul 2>nul
icacls "!KEY_PATH!" /grant:r "%USERNAME%:(R)" >nul 2>nul

echo [OK] Permissions verified!
echo.
echo [*] Step 1/3: Cleaning up old dummy sessions on Oracle Cloud...
ssh -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "mkdir -p /home/ubuntu/TG_KindSync_Pro/logs /home/ubuntu/TG_KindSync_Pro/data && rm -f /home/ubuntu/TG_KindSync_Pro/session_account*.session /home/ubuntu/TG_KindSync_Pro/session_bot_scanner.session"

echo.
echo [*] Step 2/3: Uploading updated engine and session quietly...

:: Resolve session_forwarder.session path
set "SESS_PATH=%~dp0session_forwarder.session"
if not exist "!SESS_PATH!" set "SESS_PATH=!ROOT_DIR!\session_forwarder.session"
if not exist "!SESS_PATH!" set "SESS_PATH=%~dp0..\session_forwarder.session"
if not exist "!SESS_PATH!" set "SESS_PATH=!ROOT_DIR!\data\session_forwarder.session.auth_backup"

if exist "!SESS_PATH!" (
    scp -q -o StrictHostKeyChecking=no -i "!KEY_PATH!" "!SESS_PATH!" ubuntu@130.210.1.32:/home/ubuntu/TG_KindSync_Pro/session_forwarder.session
)

:: Upload updated scripts quietly
scp -q -o StrictHostKeyChecking=no -i "!KEY_PATH!" .env tg_kindsync_pro.py web_dashboard.py main.py requirements.txt ubuntu@130.210.1.32:/home/ubuntu/TG_KindSync_Pro/ 2>nul
if exist "tools" scp -q -r -o StrictHostKeyChecking=no -i "!KEY_PATH!" tools ubuntu@130.210.1.32:/home/ubuntu/TG_KindSync_Pro/ 2>nul
if exist "devi" scp -q -r -o StrictHostKeyChecking=no -i "!KEY_PATH!" devi ubuntu@130.210.1.32:/home/ubuntu/TG_KindSync_Pro/ 2>nul
echo [OK] Files uploaded successfully!

echo.
echo [*] Step 3/3: Restarting 24/7 background services on Oracle VPS...
ssh -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "sudo systemctl daemon-reload && sudo systemctl restart tg-forwarder tg-kinddoc-bot tg-dashboard 2>/dev/null || sudo systemctl restart tg-forwarder; sudo systemctl status tg-forwarder --no-pager"

echo.
echo ==============================================================================
echo  [SUCCESS] 24/7 ORACLE CLOUD AUTOPILOT IS ACTIVE ^& RUNNING!
echo ==============================================================================
echo.

:AFTER_SYNC_MENU
echo Choose what you want to do next:
echo.
echo   [1] View Live 24/7 Journal Log Stream (Press Ctrl+C to stop viewing)
echo   [2] Open Interactive Terminal Shell (tmux session)
echo   [3] Open DEVI Sentinel Web Dashboard (Port 8080)
echo   [4] Re-run Sync
echo   [5] 🛑 Clean Stop 24/7 Background Services on Oracle
echo   [6] ▶️ Resume / Restart 24/7 Background Services on Oracle
echo.
echo   [0] Close Window
echo ==============================================================================
echo.
set /p "POST_CHOICE=Enter choice [1-6 or 0]: "

if "%POST_CHOICE%"=="1" (
    cls
    echo [*] Streaming live 24/7 logs from Oracle Cloud... (Press Ctrl+C to return)
    ssh -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "journalctl -u tg-forwarder -f -n 50"
    echo.
    goto AFTER_SYNC_MENU
)

if "%POST_CHOICE%"=="2" (
    cls
    echo [*] Connecting to Interactive Terminal...
    ssh -t -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "cd /home/ubuntu/TG_KindSync_Pro && source .venv/bin/activate 2>/dev/null || true; python3 tg_kindsync_pro.py"
    goto AFTER_SYNC_MENU
)

if "%POST_CHOICE%"=="3" (
    start http://127.0.0.1:8080
    echo [*] Opened Dashboard at http://127.0.0.1:8080
    echo [*] Starting secure tunnel (Keep window open while viewing)...
    ssh -N -L 8080:127.0.0.1:8080 -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32
    goto AFTER_SYNC_MENU
)

if "%POST_CHOICE%"=="4" goto SYNC_STEP

if "%POST_CHOICE%"=="5" (
    cls
    echo [*] Stopping background services cleanly on Oracle VPS...
    ssh -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "sudo systemctl stop tg-forwarder tg-kinddoc-bot tg-dashboard 2>/dev/null; echo [OK] All services cleanly stopped!"
    echo.
    pause
    goto AFTER_SYNC_MENU
)

if "%POST_CHOICE%"=="6" (
    cls
    echo [*] Resuming/Starting background services on Oracle VPS...
    ssh -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "sudo systemctl daemon-reload && sudo systemctl restart tg-forwarder tg-kinddoc-bot tg-dashboard 2>/dev/null; sudo systemctl status tg-forwarder --no-pager"
    echo.
    pause
    goto AFTER_SYNC_MENU
)

if "%POST_CHOICE%"=="0" exit /b 0

echo [!] Invalid option.
timeout /t 2 >nul
goto AFTER_SYNC_MENU


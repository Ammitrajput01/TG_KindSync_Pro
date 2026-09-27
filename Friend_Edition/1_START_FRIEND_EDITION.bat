@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
title TG KINDSYNC PRO -- FRIEND EDITION MASTER CONTROL (24/7 ORACLE)
color 0a
cd /d "%~dp0"

:MAIN_MENU
cls
echo ==============================================================================
echo        TG KINDSYNC PRO -- FRIEND EDITION MASTER CONTROL
echo        Oracle Cloud Mumbai VPS (24/7 High-Speed Telegram Cloner)
echo        Powered by: Kind Doctor ^& Team (@Kinddoctor4u)
echo ==============================================================================
echo.
echo   [1] Connect to Oracle Terminal (Interactive Setup ^& Select Topics)
echo   [2] Start 24/7 Autopilot (Runs continuously in background even if PC is OFF)
echo   [3] View Quick How-To-Use Guide
echo   [4] Auto-Fix ^& Verify SSH Key Permissions
echo.
echo   [0] Exit
echo ==============================================================================
echo.
set /p "CHOICE=Enter your choice [1-4 or 0]: "

if "%CHOICE%"=="1" goto RUN_INTERACTIVE
if "%CHOICE%"=="2" goto RUN_AUTOPILOT
if "%CHOICE%"=="3" goto VIEW_GUIDE
if "%CHOICE%"=="4" goto FIX_PERMISSIONS
if "%CHOICE%"=="0" exit /b 0

echo [!] Invalid choice. Please select from 1 to 4 or 0.
timeout /t 2 >nul
goto MAIN_MENU

:RUN_INTERACTIVE
cls
if exist "tools\CONNECT_ORACLE_FRIEND.bat" (
    call "tools\CONNECT_ORACLE_FRIEND.bat"
) else if exist "CONNECT_ORACLE_FRIEND.bat" (
    call "CONNECT_ORACLE_FRIEND.bat"
) else (
    set "KEY_PATH=%~dp0oracle_key_latest.key"
    if not exist "!KEY_PATH!" set "KEY_PATH=%~dp0keys\oracle_key_latest.key"
    echo [*] Connecting to Oracle Cloud Terminal...
    ssh -L 5005:localhost:5005 -t -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "/home/ubuntu/setup_friend_oracle.sh"
)
pause
goto MAIN_MENU

:RUN_AUTOPILOT
cls
if exist "tools\START_ORACLE_FRIEND_24_7.bat" (
    call "tools\START_ORACLE_FRIEND_24_7.bat"
) else if exist "START_ORACLE_FRIEND_24_7.bat" (
    call "START_ORACLE_FRIEND_24_7.bat"
) else (
    set "KEY_PATH=%~dp0oracle_key_latest.key"
    if not exist "!KEY_PATH!" set "KEY_PATH=%~dp0keys\oracle_key_latest.key"
    echo [*] Starting 24/7 Autopilot on Oracle VPS...
    scp -o StrictHostKeyChecking=no -i "!KEY_PATH!" "%~dp0deploy\start_friend_24_7.sh" ubuntu@130.210.1.32:/home/ubuntu/start_friend_24_7.sh
    ssh -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "chmod +x /home/ubuntu/start_friend_24_7.sh && /home/ubuntu/start_friend_24_7.sh"
)
pause
goto MAIN_MENU

:VIEW_GUIDE
cls
if exist "docs\HOW_TO_RUN_FOR_FRIEND.txt" (
    type "docs\HOW_TO_RUN_FOR_FRIEND.txt"
) else if exist "HOW_TO_RUN_FOR_FRIEND.txt" (
    type "HOW_TO_RUN_FOR_FRIEND.txt"
) else (
    echo Guide file not found.
)
echo.
pause
goto MAIN_MENU

:FIX_PERMISSIONS
cls
echo [*] Auto-verifying Windows Security Permissions on SSH Key...
set "KEY_PATH=%~dp0oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%~dp0keys\oracle_key_latest.key"
if not exist "!KEY_PATH!" (
    echo [ERROR] SSH Key not found: oracle_key_latest.key
    pause
    goto MAIN_MENU
)
icacls "!KEY_PATH!" /reset >nul 2>nul
icacls "!KEY_PATH!" /inheritance:r >nul 2>nul
icacls "!KEY_PATH!" /grant:r "%USERNAME%:R" >nul 2>nul
icacls "!KEY_PATH!" /grant:r "%USERNAME%:(R)" >nul 2>nul
echo [OK] Permissions verified successfully!
pause
goto MAIN_MENU

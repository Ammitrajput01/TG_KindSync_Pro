@echo off
setlocal EnableDelayedExpansion
title TG KindSync Pro - Oracle Cloud Friend Instance (24/7 Tunnel)
color 0a
cls

echo ==============================================================================
echo       TG KINDSYNC PRO - ORACLE CLOUD FRIEND INSTANCE (24/7 ONLINE)
echo       IP: 130.210.1.32 (Oracle Mumbai Always-Free VPS)
echo ==============================================================================
echo.

cd /d "%~dp0"

set "KEY_PATH=%~dp0oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%~dp0..\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%~dp0oracle_key.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%~dp0..\oracle_key.key"
if not exist "!KEY_PATH!" set "KEY_PATH=C:\TG_KindSync_Pro\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=C:\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%USERPROFILE%\Downloads\oracle_key_latest.key"

if not exist "!KEY_PATH!" (
    echo [ERROR] SSH Key not found in folder!
    echo Looked for: !KEY_PATH!
    echo Please make sure oracle_key_latest.key is in the folder.
    echo.
    pause
    exit /b 1
)

echo [*] Found SSH Key: !KEY_PATH!
echo [*] Auto-fixing Windows Security Permissions on Key...

:: Fix Windows SSH Key Permissions
icacls "!KEY_PATH!" /reset >nul 2>nul
icacls "!KEY_PATH!" /inheritance:r >nul 2>nul
icacls "!KEY_PATH!" /grant:r "%USERNAME%:R" >nul 2>nul
icacls "!KEY_PATH!" /grant:r "%USERNAME%:(R)" >nul 2>nul

echo [OK] Security permissions verified successfully!
echo.
echo [*] Step 1: Syncing isolated workspace on Oracle Cloud...
set "SCRIPT_PATH=%~dp0deploy\setup_friend_oracle.sh"
if not exist "!SCRIPT_PATH!" set "SCRIPT_PATH=%~dp0..\deploy\setup_friend_oracle.sh"
scp -o StrictHostKeyChecking=no -i "!KEY_PATH!" "!SCRIPT_PATH!" ubuntu@130.210.1.32:/home/ubuntu/setup_friend_oracle.sh
ssh -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "chmod +x /home/ubuntu/setup_friend_oracle.sh"

echo.
echo [*] Step 2: Connecting to Oracle Cloud Terminal with Auto Port Forwarding (5005)...
echo [*] Note: Browser Login (http://127.0.0.1:5005) will work seamlessly!
echo.
ssh -L 5005:localhost:5005 -t -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "/home/ubuntu/setup_friend_oracle.sh"

echo.
echo ==============================================================================
echo Session closed. To re-connect anytime, double-click this file again!
echo ==============================================================================
pause

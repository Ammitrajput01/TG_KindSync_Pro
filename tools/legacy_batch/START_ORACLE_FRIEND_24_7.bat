@echo off
setlocal EnableDelayedExpansion
title TG KindSync Pro - Oracle Cloud 24/7 Autopilot Launcher
color 0b
cls

echo ==============================================================================
echo       TG KINDSYNC PRO - ORACLE CLOUD 24/7 LIVE AUTOPILOT LAUNCHER
echo       IP: 130.210.1.32 (Oracle Mumbai Always-Free VPS)
echo ==============================================================================
echo.

cd /d "%~dp0"

set "KEY_PATH=%~dp0oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%~dp0oracle_key.key"
if not exist "!KEY_PATH!" set "KEY_PATH=C:\TG_KindSync_Pro\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=C:\oracle_key_latest.key"
if not exist "!KEY_PATH!" set "KEY_PATH=%USERPROFILE%\Downloads\oracle_key_latest.key"

if not exist "!KEY_PATH!" (
    echo [ERROR] SSH Key not found!
    echo Please make sure oracle_key_latest.key is in the folder.
    echo.
    pause
    exit /b 1
)

echo [*] Using SSH Key: !KEY_PATH!
echo [*] Auto-fixing Windows Security Permissions on Key...

icacls "!KEY_PATH!" /reset >nul 2>nul
icacls "!KEY_PATH!" /inheritance:r >nul 2>nul
icacls "!KEY_PATH!" /grant:r "%USERNAME%:R" >nul 2>nul
icacls "!KEY_PATH!" /grant:r "%USERNAME%:(R)" >nul 2>nul

echo [OK] Security permissions verified!
echo.
echo [*] Step 1: Uploading 24/7 Autopilot Service Script to Oracle VPS...
scp -o StrictHostKeyChecking=no -i "!KEY_PATH!" "%~dp0deploy\start_friend_24_7.sh" ubuntu@130.210.1.32:/home/ubuntu/start_friend_24_7.sh
ssh -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "chmod +x /home/ubuntu/start_friend_24_7.sh"

echo.
echo [*] Step 2: Activating 24/7 Background Systemd Service on Oracle VPS...
echo.
ssh -o StrictHostKeyChecking=no -i "!KEY_PATH!" ubuntu@130.210.1.32 "/home/ubuntu/start_friend_24_7.sh"

echo.
echo ==============================================================================
echo [SUCCESS] Friend Forwarder is now running 24/7 on Oracle Cloud Autopilot!
echo You can safely close this window and TURN OFF your PC!
echo ==============================================================================
echo.
pause

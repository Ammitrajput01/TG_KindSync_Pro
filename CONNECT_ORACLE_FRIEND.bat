@echo off
title TG KindSync Pro - Oracle Cloud Friend Workspace Launcher
color 0a
echo ======================================================================
echo    CONNECTING TO FRIEND ISOLATED WORKSPACE ON ORACLE CLOUD
echo    IP: 130.210.1.32 (ap-mumbai-1)
echo ======================================================================
echo.

set KEY_PATH="C:\oracle_key_latest.key"
if not exist %KEY_PATH% set KEY_PATH="%~dp0oracle_key_latest.key"
if not exist %KEY_PATH% set KEY_PATH="C:\Users\%USERNAME%\Downloads\oracle_key_latest.key"
if not exist %KEY_PATH% set KEY_PATH="C:\Users\Ammit\Downloads\oracle_key_latest.key"

echo [*] Using Private Key: %KEY_PATH%
echo [*] Launching Friend Workspace directly...
echo.

ssh -t -o StrictHostKeyChecking=no -i %KEY_PATH% ubuntu@130.210.1.32 "./start_friend.sh"
pause

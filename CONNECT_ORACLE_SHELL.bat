@echo off
title TG KindSync Pro - Oracle Cloud Terminal SSH
color 0b
echo ======================================================================
echo    CONNECTING TO TG KINDSYNC PRO ORACLE CLOUD SERVER (24/7)
echo    IP: 130.210.1.32 (ap-mumbai-1)
echo ======================================================================
echo.

set KEY_PATH="C:\oracle_key_latest.key"
if not exist %KEY_PATH% set KEY_PATH="%~dp0oracle_key_latest.key"
if not exist %KEY_PATH% set KEY_PATH="C:\Users\%USERNAME%\Downloads\oracle_key_latest.key"
if not exist %KEY_PATH% set KEY_PATH="C:\Users\Ammit\Downloads\oracle_key_latest.key"

echo [*] Using Private Key: %KEY_PATH%
echo [*] Connecting to ubuntu@130.210.1.32...
echo.

ssh -o StrictHostKeyChecking=no -i %KEY_PATH% ubuntu@130.210.1.32
pause

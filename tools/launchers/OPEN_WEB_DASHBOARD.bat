@echo off
title TG KindSync Pro - Web Dashboard Tunnel
color 0a
cls
echo ==============================================================================
echo       TG KINDSYNC PRO - SENTINEL AI MISSION CONTROL WEB DASHBOARD
echo       Connecting Secure Tunnel to Oracle VPS (130.210.1.32)...
echo ==============================================================================
echo.

set "KEY_PATH=%~dp0oracle_key_latest.key"
if not exist "%KEY_PATH%" set "KEY_PATH=C:\oracle_key_latest.key"
if not exist "%KEY_PATH%" set "KEY_PATH=%USERPROFILE%\Downloads\oracle_key_latest.key"

echo [*] Opening Dashboard in your default browser...
start http://127.0.0.1:8080

echo [*] Secure SSH Tunnel is ACTIVE on http://127.0.0.1:8080
echo [*] Login Credentials: Amit / Amit@123
echo [*] Keep this window open while using the dashboard.
echo.
ssh -N -L 8080:127.0.0.1:8080 -o StrictHostKeyChecking=no -i "%KEY_PATH%" ubuntu@130.210.1.32
pause

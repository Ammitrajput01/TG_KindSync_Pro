@echo off
title TG KindSync Pro - Sentinel AI Web Dashboard (Port 8080)
color 0B
chcp 65001 >nul
cd /d "%~dp0"

echo ===============================================================================
echo   🌐 TG KINDSYNC PRO V14.5 - SENTINEL AI WEB DASHBOARD & MISSION CONTROL
echo ===============================================================================
echo.
echo [*] Starting Local Web Dashboard on http://localhost:8080 ...
echo [*] Local LAN Access: http://192.168.1.90:8080 (or your Wi-Fi IP)
echo.
python web_dashboard.py
pause

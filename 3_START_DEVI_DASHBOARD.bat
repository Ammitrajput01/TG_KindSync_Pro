@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title [3/5] DEVI WEB DASHBOARD + AI OPERATOR
cls
echo ==============================================================================
echo                 DEVI WEB DASHBOARD + AI OPERATOR
echo ==============================================================================
echo.

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

echo Starting Web Dashboard on http://localhost:8080 ...
python web_dashboard.py
pause

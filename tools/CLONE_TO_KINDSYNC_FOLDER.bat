@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title 📁 CLONE WORKSPACE TO C:\TG_KindSync_Pro
cls

echo ==============================================================================
echo       CLONE WORKSPACE TO C:\TG_KindSync_Pro
echo ==============================================================================
echo.
echo This will create a fresh, clean mirror of this project at:
echo   C:\TG_KindSync_Pro
echo.
pause

echo [*] Copying files to C:\TG_KindSync_Pro (excluding .venv and git)...
robocopy "%~dp0." "C:\TG_KindSync_Pro" /E /XD .venv .git __pycache__ .pytest_cache /XF *.pyc /R:1 /W:1
echo.
echo [OK] Workspace successfully mirrored to C:\TG_KindSync_Pro !
echo.
pause

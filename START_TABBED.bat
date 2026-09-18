@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title 🌐 TG KINDSYNC PRO — CHROME-STYLE TABBED LAUNCHER

:: Check wt.exe
where wt.exe >nul 2>nul
if %ERRORLEVEL% equ 0 (
    wt.exe -w 0 nt --title "🚀 TG KindSync Engine" -d "%~dp0." cmd /k "call START_BOT.bat --auto" ; nt --title "🩺 Kind Doctor Bot" -d "%~dp0." cmd /k "call START_KIND_DOCTOR_BOT.bat" ; nt --title "🌐 Web Dashboard" -d "%~dp0." cmd /k "call 3_START_DEVI_DASHBOARD.bat"
    exit /b 0
)

if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe" (
    "%LOCALAPPDATA%\Microsoft\WindowsApps\wt.exe" -w 0 nt --title "🚀 TG KindSync Engine" -d "%~dp0." cmd /k "call START_BOT.bat --auto" ; nt --title "🩺 Kind Doctor Bot" -d "%~dp0." cmd /k "call START_KIND_DOCTOR_BOT.bat" ; nt --title "🌐 Web Dashboard" -d "%~dp0." cmd /k "call 3_START_DEVI_DASHBOARD.bat"
    exit /b 0
)

echo [!] Windows Terminal (wt.exe) was not found. Launching minimized instead...
call "%~dp0START_MINIMIZED.bat"

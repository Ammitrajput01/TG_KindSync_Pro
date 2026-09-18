@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title 📦 TG KINDSYNC PRO — PUBLISH UPDATE PACKAGE
cls

echo ==============================================================================
echo           TG KINDSYNC PRO — DEVELOPER PUBLISH + BUNDLE PACKAGER
echo ==============================================================================
echo.
python tools\updater.py --publish
echo.
pause

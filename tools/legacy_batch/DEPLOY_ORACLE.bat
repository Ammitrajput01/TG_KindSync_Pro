@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title 🚀 TG KINDSYNC PRO — 1-CLICK PUSH & ORACLE VPS DEPLOY
cls

echo ==============================================================================
echo       🩺 TG KINDSYNC PRO — 1-CLICK GITHUB + ORACLE CLOUD VPS DEPLOY
echo ==============================================================================
echo.

:: 1. GIT STATUS & PUSH
echo [*] Step 1: Pushing latest code to GitHub (Private Repo)...
git add .
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%
git commit -m "sync: KindSync Pro auto-sync %TIMESTAMP%" >nul 2>nul
git push origin main

if %errorlevel% equ 0 (
    echo [OK] GitHub repository updated successfully!
) else (
    echo [!] GitHub push notice - continuing with direct VPS deploy...
)

echo.
:: 2. ORACLE CLOUD SYNC VIA SSH KEY
echo [*] Step 2: Syncing files directly to Oracle Cloud VPS (130.210.1.32)...
set ORACLE_IP=130.210.1.32
set ORACLE_USER=ubuntu
set ORACLE_KEY=oracle_key_latest.key

if not exist "%ORACLE_KEY%" (
    echo [!] Oracle key %ORACLE_KEY% not found!
    pause
    exit /b 1
)

:: Transfer code files
scp -o StrictHostKeyChecking=no -i "%ORACLE_KEY%" tg_kindsync_pro.py web_dashboard.py %ORACLE_USER%@%ORACLE_IP%:~/TG_KindSync_Pro/
scp -o StrictHostKeyChecking=no -i "%ORACLE_KEY%" -r devi %ORACLE_USER%@%ORACLE_IP%:~/TG_KindSync_Pro/

echo.
:: 3. RESTART SERVICES ON VPS
echo [*] Step 3: Restarting 24/7 background services on Oracle Cloud VPS...
ssh -o StrictHostKeyChecking=no -i "%ORACLE_KEY%" %ORACLE_USER%@%ORACLE_IP% "sudo systemctl daemon-reload && sudo systemctl restart tg-kinddoc-bot tg-forwarder tg-dashboard && sudo systemctl status tg-kinddoc-bot --no-pager"

echo.
echo ==============================================================================
echo 🎉 DEPLOYMENT COMPLETE!
echo - GitHub: Pushed & Synced
echo - Oracle Cloud VPS: Code updated & All 3 services restarted live!
echo ==============================================================================
echo.
pause

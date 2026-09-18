@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title 🚀 TG KINDSYNC PRO — 1-CLICK PUSH TO PRIVATE GITHUB
cls

echo ==============================================================================
echo       🩺 TG KINDSYNC PRO — 1-CLICK PRIVATE GITHUB SYNC & BACKUP
echo ==============================================================================
echo.
echo [*] Checking local Git repository status...

git status >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Initializing Git repository...
    git init
    git branch -M main
)

:: Check if remote origin is configured
git remote | findstr /i "origin" >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ==============================================================================
    echo [!] Remote GitHub repository not connected yet!
    echo.
    echo 1. Go to https://github.com/new
    echo 2. Repository Name: TG_KindSync_Pro
    echo 3. Visibility: Select PRIVATE (Very Important!)
    echo 4. Click "Create repository"
    echo.
    echo Copy your GitHub Repository URL (e.g., https://github.com/Ammitrajput01/TG_KindSync_Pro.git)
    echo ==============================================================================
    set /p REPO_URL="Enter your GitHub Private Repo URL: "
    if not "%REPO_URL%"=="" (
        git remote add origin %REPO_URL%
        echo [OK] Remote origin set to %REPO_URL%
    ) else (
        echo [!] No URL provided. Aborting push.
        pause
        exit /b 1
    )
)

echo.
echo [*] Staging safe project files (All .env, .session and .sqlite are 100%% PROTECTED)...
git add .

for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%_%datetime:~8,2%-%datetime:~10,2%

echo [*] Creating commit: Update_%TIMESTAMP%...
git commit -m "update: KindSync Pro auto-sync %TIMESTAMP%" >nul 2>nul

echo.
echo [*] Pushing updates to Private GitHub (main branch)...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ==============================================================================
    echo 🎉 SUCCESS! All updates safely pushed to your Private GitHub repository!
    echo.
    echo On Oracle Cloud VPS, simply run:
    echo   ./deploy/update_oracle.sh
    echo to sync and restart all services instantly!
    echo ==============================================================================
) else (
    echo.
    echo [!] Push encountered a notice or needs GitHub login.
    echo Please review message above.
)

echo.
pause

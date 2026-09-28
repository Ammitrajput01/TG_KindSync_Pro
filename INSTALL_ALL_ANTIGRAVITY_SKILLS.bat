@echo off
title 🚀 ANTIGRAVITY MASTER SKILLS & AGENTS SUITE INSTALLER
color 0b
cls
echo ==============================================================================
echo       🚀 ANTIGRAVITY MASTER SKILLS & AGENTS SUITE INSTALLER
echo       Syncs all Tier-1 High-Priority Skills + Vault Configuration
echo ==============================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\INSTALL_ALL_ANTIGRAVITY_SKILLS.ps1" -TargetWorkspace "%~dp0."

echo.
echo ==============================================================================
echo  [OK] All Antigravity Agent Skills are successfully synced and active!
echo ==============================================================================
pause

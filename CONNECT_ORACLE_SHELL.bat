@echo off
title TG KindSync Pro - Oracle Cloud Terminal SSH
color 0b
echo ======================================================================
echo    CONNECTING TO TG KINDSYNC PRO ORACLE CLOUD SERVER (24/7)
echo    IP: 130.210.1.32 (ap-mumbai-1)
echo ======================================================================
echo.
ssh -i "%~dp0oracle_key_latest.key" ubuntu@130.210.1.32
pause

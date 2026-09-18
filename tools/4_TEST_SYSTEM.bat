@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"
title [4/5] SYSTEM DIAGNOSTICS + FREE AI HUB TESTER
cls
echo ==============================================================================
echo                 SYSTEM DIAGNOSTICS + FREE AI HUB TESTER
echo ==============================================================================
echo.

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

set PYTHONPATH=.agents

echo [1] Checking Free AI Model Hub Status...
python -m free_ai_hub.cli status

echo.
echo ------------------------------------------------------------------------------
echo Diagnostics Menu:
echo   [1] Run Live Benchmark on all active Free AI Models
echo   [2] Ask AI Council a Question (Multi-LLM Debate)
echo   [3] Test Fast AI Query (Groq / OpenRouter / Mistral)
echo   [4] Check Database Integrity (history_core.sqlite)
echo   [5] Open Keys Config File (.agents\free_ai_keys.env)
echo   [6] Exit
echo ------------------------------------------------------------------------------
set /p choice="Select option (1-6): "

if "%choice%"=="1" (
    echo.
    python -m free_ai_hub.cli benchmark
    pause
    goto :eof
)
if "%choice%"=="2" (
    echo.
    set /p question="Enter question for AI Council: "
    python -m free_ai_hub.cli council "%question%"
    pause
    goto :eof
)
if "%choice%"=="3" (
    echo.
    set /p prompt="Enter prompt: "
    python -m free_ai_hub.cli query "%prompt%" --category fast
    pause
    goto :eof
)
if "%choice%"=="4" (
    echo.
    python -c "import sqlite3; con = sqlite3.connect('history_core.sqlite'); print('DB Integrity Check:', con.execute('PRAGMA integrity_check').fetchone()[0]); print('Total Forwarded Records:', con.execute('SELECT count(*) FROM forwarded').fetchone()[0]); con.close()"
    pause
    goto :eof
)
if "%choice%"=="5" (
    if exist .agents\free_ai_keys.env (
        notepad .agents\free_ai_keys.env
    ) else (
        notepad .env
    )
    goto :eof
)

echo Done!
pause

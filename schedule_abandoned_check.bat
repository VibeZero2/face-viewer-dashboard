@echo off
echo Setting up scheduled task for checking abandoned sessions...

REM Get the current directory
set SCRIPT_DIR=%~dp0
set PYTHON_SCRIPT=%SCRIPT_DIR%check_abandoned_sessions.py

REM Create a scheduled task to run every 2 hours
schtasks /create /tn "Face Viewer - Check Abandoned Sessions" /tr "python %PYTHON_SCRIPT%" /sc hourly /mo 2 /ru System

echo.
echo Task scheduled successfully. The abandoned session check will run every 2 hours.
echo You can view and modify this task in Windows Task Scheduler.
echo.
pause

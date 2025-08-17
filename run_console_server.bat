@echo off
echo ===============================================
echo Starting Simple Console Server
echo ===============================================
echo.
echo Server will be available at: http://localhost:5000
echo.
echo IMPORTANT: Watch for error messages below
echo.

cd /d %~dp0
python simple_console_server.py

pause

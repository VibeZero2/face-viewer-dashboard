@echo off
echo ===============================================
echo Starting Face Viewer Dashboard Test Server
echo ===============================================
echo.
echo Server will be available at: http://localhost:10000
echo.
echo Press Ctrl+C to stop the server
echo.

cd /d %~dp0
python simple_test.py

pause

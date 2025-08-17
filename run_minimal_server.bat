@echo off
echo ===============================================
echo Starting Face Viewer Dashboard Test Server
echo ===============================================
echo.
echo Server will be available at: http://localhost:8080
echo.
echo Press Ctrl+C to stop the server when done
echo.

cd /d %~dp0
python minimal_app.py

pause

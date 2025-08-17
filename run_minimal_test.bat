@echo off
echo ===============================================
echo Starting Minimal Test Server
echo ===============================================
echo.
echo Server will be available at: http://localhost:8080
echo.
echo Press Ctrl+C to stop the server when done
echo.

cd /d %~dp0
python test_minimal_server.py

pause

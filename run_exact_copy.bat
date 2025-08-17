@echo off
echo ===============================================
echo Starting Exact Copy of Working Server
echo ===============================================
echo.
echo Server will be available at: http://localhost:8080
echo.
echo Press Ctrl+C to stop the server when done
echo.

cd /d %~dp0
python exact_copy.py

pause

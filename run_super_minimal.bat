@echo off
echo ===============================================
echo Starting Super Minimal Flask Server
echo ===============================================
echo.
echo Server will be available at: http://127.0.0.1:5000
echo.
echo Press Ctrl+C to stop the server when done
echo.

cd /d %~dp0
python super_minimal.py

pause

@echo off
echo ===============================================
echo Starting Face Viewer Dashboard Application
echo ===============================================
echo.
echo Server will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server when done
echo.

cd /d %~dp0
python app.py

pause

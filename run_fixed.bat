@echo off
echo ===============================================
echo Starting Face Viewer Dashboard (Fixed)
echo ===============================================
echo.
echo Server will be available at: http://localhost:8080
echo.
echo Press Ctrl+C to stop the server when done
echo.

cd /d %~dp0
python fixed_app.py

pause

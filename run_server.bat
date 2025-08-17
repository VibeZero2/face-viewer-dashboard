@echo off
echo ===============================================
echo Starting Face Viewer Dashboard server on port 8080...
echo ===============================================
echo.
echo After server starts, access the dashboard at: http://localhost:8080
echo.
echo Press Ctrl+C to stop the server when done
echo.

cd /d %~dp0
python app.py
pause

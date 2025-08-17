@echo off
echo ===============================================
echo Running verbose Flask server test
echo ===============================================
echo.
echo This will test if the server can start on port 5000
echo Output will be displayed in this console window
echo.
echo Press Ctrl+C to stop the server when done
echo.

cd /d %~dp0
python verbose_test_server.py
echo.
echo Server test complete or interrupted
pause

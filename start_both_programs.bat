@echo off
echo ========================================
echo Starting Face Perception Study System
echo ========================================
echo.

echo Starting Dashboard on port 5000...
start "Dashboard" cmd /k "cd /d C:\Users\Chris\CascadeProjects\face-viewer-dashboard && python dashboard_app.py"

echo Waiting 3 seconds for dashboard to start...
timeout /t 3 /nobreak > nul

echo Starting Study Program on port 8080...
start "Study Program" cmd /k "cd /d C:\Users\Chris\CascadeProjects\facial-trust-study && python working_study_server.py"

echo Waiting 3 seconds for study program to start...
timeout /t 3 /nobreak > nul

echo.
echo ========================================
echo Both programs are starting...
echo ========================================
echo Dashboard: http://localhost:5000
echo Study Program: http://localhost:8080
echo.
echo Opening dashboard in browser...
start http://localhost:5000

echo Opening study program in browser...
start http://localhost:8080

echo.
echo Both programs should now be running!
echo Press any key to close this window...
pause > nul

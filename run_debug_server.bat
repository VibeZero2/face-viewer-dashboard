@echo off
echo ===============================================
echo Starting Face Viewer Dashboard Debug Server
echo ===============================================
echo.
echo This is a special debug server that will help troubleshoot connection issues.
echo.

cd /d %~dp0
python debug_server.py

pause

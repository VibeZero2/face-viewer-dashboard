@echo off
echo ===============================================
echo Starting Face Viewer Dashboard
echo ===============================================
echo.
echo Server will be available at: http://localhost:8080
echo.
echo Press Ctrl+C to stop the server when done
echo.

:: Set environment variables
set DASHBOARD_SECRET_KEY=dev_secret_key_for_testing
set FLASK_SECRET_KEY=dev_flask_key_for_testing
set FLASK_ENV=development
set PORT=8080
set FACE_VIEWER_DATA_DIR=%~dp0data

:: Create data directory if it doesn't exist
if not exist "%~dp0data" mkdir "%~dp0data"
if not exist "%~dp0data\responses" mkdir "%~dp0data\responses"

:: Run the app
cd /d %~dp0
python working_app.py

pause

@echo off
echo Setting up GitHub repository...

REM Initialize Git repository if not already initialized
git init

REM Add all files to staging
git add .

REM Commit changes
git commit -m "Fix dashboard menus and analytics functionality"

REM Add GitHub repository as remote origin
git remote add origin https://github.com/VibeZero2/face-viewer-dashboard.git
git remote set-url origin https://github.com/VibeZero2/face-viewer-dashboard.git

REM Push to GitHub (you'll be prompted for credentials)
git push -u origin main

REM If main branch fails, try master branch
if %errorlevel% neq 0 (
    echo Trying master branch instead...
    git push -u origin master
)

echo Done!
pause

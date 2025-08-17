@echo off
echo Pushing code to GitHub...

:: Initialize Git repository
git init

:: Add all files to staging
git add .

:: Commit changes
git commit -m "Fix dashboard menus and analytics functionality"

:: Add GitHub repository as remote origin
git remote add origin https://github.com/VibeZero2/face-viewer-dashboard.git
git remote set-url origin https://github.com/VibeZero2/face-viewer-dashboard.git

:: Push to GitHub
git push -u origin main

:: If main branch fails, try master branch
if %errorlevel% neq 0 (
    echo Trying master branch instead...
    git push -u origin master
)

echo Done!
pause

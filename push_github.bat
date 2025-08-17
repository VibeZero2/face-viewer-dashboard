@echo off
echo ===============================================
echo Pushing code to GitHub repository
echo ===============================================

:: Initialize Git repository if not already initialized
git init

:: Configure Git (if not already configured)
git config --global user.email "user@example.com"
git config --global user.name "User"

:: Add all files to staging
git add .

:: Commit changes
git commit -m "Fix dashboard menus and analytics functionality"

:: Add GitHub repository as remote origin (if not already added)
git remote add origin https://github.com/VibeZero2/face-viewer-dashboard.git
git remote set-url origin https://github.com/VibeZero2/face-viewer-dashboard.git

:: Push to GitHub
echo Pushing to GitHub...
git push -u origin main

:: If main branch fails, try master branch
if %errorlevel% neq 0 (
    echo Trying master branch instead...
    git push -u origin master
)

echo Done!
pause

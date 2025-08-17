@echo off
echo ===== GitHub Push Script =====

echo Initializing Git repository...
git init

echo Checking remote repositories...
git remote -v
echo Removing any existing origin...
git remote remove origin 2>nul

echo Adding GitHub repository as origin...
git remote add origin https://github.com/VibeZero2/face-viewer-dashboard.git
echo Remote repositories after adding:
git remote -v

echo Adding all files to staging...
git add .

echo Configuring Git user if not set...
git config --get user.email >nul 2>&1
if %errorlevel% neq 0 (
    echo Setting temporary Git user for this commit...
    git config user.email "temp@example.com"
    git config user.name "Temporary User"
)

echo Committing changes...
git commit -m "Fix dashboard menus and analytics functionality"

echo Pushing to GitHub...
git push -u origin master

if %errorlevel% neq 0 (
    echo Trying to push to main branch instead...
    git push -u origin main
)

echo Done!
pause

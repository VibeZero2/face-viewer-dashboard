@echo off
echo ===============================================
echo Pushing updated files to GitHub
echo ===============================================

:: Initialize Git repository if not already initialized
git init

:: Add all files to staging
git add .

:: Commit changes
git commit -m "Add GitHub templates and enhance documentation"

:: Add GitHub repository as remote origin (if not already added)
git remote add origin https://github.com/VibeZero2/face-viewer-dashboard.git
git remote set-url origin https://github.com/VibeZero2/face-viewer-dashboard.git

:: Push to GitHub
echo Pushing to GitHub...
git push -u origin master

:: If master branch fails, try main branch
if %errorlevel% neq 0 (
    echo Trying main branch instead...
    git push -u origin main
)

echo Done!
pause

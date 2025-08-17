@echo off
echo Initializing Git repository...
git init

echo Setting up remote origin...
git remote remove origin
git remote add origin https://github.com/VibeZero2/face-viewer-dashboard.git

echo Adding all files...
git add .

echo Committing changes...
git commit -m "Fix dashboard menus and analytics functionality"

echo Pushing to GitHub...
git push -u origin master

echo Done!
pause

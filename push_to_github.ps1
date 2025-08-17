# PowerShell script to push code to GitHub
Write-Host "Initializing Git repository..."
git init

Write-Host "Setting up remote origin..."
git remote remove origin
git remote add origin https://github.com/VibeZero2/face-viewer-dashboard.git

Write-Host "Adding all files..."
git add .

Write-Host "Committing changes..."
git commit -m "Fix dashboard menus and analytics functionality"

Write-Host "Pushing to GitHub..."
git push -u origin master

Write-Host "Done!"

# PowerShell script to push code to GitHub with detailed output
Write-Host "Starting GitHub push process..." -ForegroundColor Green

# Check if git is installed
try {
    $gitVersion = git --version
    Write-Host "Git detected: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "Git not found in PATH. Please install Git." -ForegroundColor Red
    exit 1
}

# Initialize Git repository
Write-Host "Initializing Git repository..." -ForegroundColor Yellow
git init
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to initialize Git repository." -ForegroundColor Red
} else {
    Write-Host "Git repository initialized successfully." -ForegroundColor Green
}

# Configure Git if needed
$userEmail = git config --global user.email
$userName = git config --global user.name

if ([string]::IsNullOrEmpty($userEmail)) {
    Write-Host "Setting default Git user email..." -ForegroundColor Yellow
    git config --global user.email "user@example.com"
}

if ([string]::IsNullOrEmpty($userName)) {
    Write-Host "Setting default Git user name..." -ForegroundColor Yellow
    git config --global user.name "User"
}

# Add all files to staging
Write-Host "Adding all files to staging..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to add files to staging." -ForegroundColor Red
} else {
    Write-Host "Files added to staging successfully." -ForegroundColor Green
}

# Commit changes
Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "Fix dashboard menus and analytics functionality"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to commit changes. This might be because there are no changes to commit." -ForegroundColor Red
} else {
    Write-Host "Changes committed successfully." -ForegroundColor Green
}

# Set up remote origin
Write-Host "Setting up remote origin..." -ForegroundColor Yellow
git remote remove origin
git remote add origin https://github.com/VibeZero2/face-viewer-dashboard.git
Write-Host "Remote origin set to https://github.com/VibeZero2/face-viewer-dashboard.git" -ForegroundColor Green

# Push to GitHub - main branch
Write-Host "Pushing to GitHub main branch..." -ForegroundColor Yellow
git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to push to main branch. Trying master branch..." -ForegroundColor Yellow
    
    # Try master branch instead
    git push -u origin master
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to push to master branch as well." -ForegroundColor Red
        Write-Host "You may need to enter your GitHub credentials manually." -ForegroundColor Yellow
    } else {
        Write-Host "Successfully pushed to master branch!" -ForegroundColor Green
    }
} else {
    Write-Host "Successfully pushed to main branch!" -ForegroundColor Green
}

Write-Host "GitHub push process completed." -ForegroundColor Green
pause

Write-Host "========================================" -ForegroundColor Green
Write-Host "Starting Face Perception Study System" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Start Dashboard
Write-Host "Starting Dashboard on port 5000..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Chris\CascadeProjects\face-viewer-dashboard'; python dashboard_app.py" -WindowStyle Normal

# Wait a moment
Start-Sleep -Seconds 3

# Start Study Program
Write-Host "Starting Study Program on port 8080..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd 'C:\Users\Chris\CascadeProjects\facial-trust-study'; python working_study_server.py" -WindowStyle Normal

# Wait a moment
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Both programs are starting..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Dashboard: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Study Program: http://localhost:8080" -ForegroundColor Cyan
Write-Host ""

# Open browsers
Write-Host "Opening dashboard in browser..." -ForegroundColor Yellow
Start-Process "http://localhost:5000"

Write-Host "Opening study program in browser..." -ForegroundColor Yellow
Start-Process "http://localhost:8080"

Write-Host ""
Write-Host "Both programs should now be running!" -ForegroundColor Green
Write-Host "Press any key to close this window..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "==============================================="
Write-Host "Flask Server Debug Script"
Write-Host "==============================================="
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..."
try {
    $pythonVersion = python --version
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found or not in PATH" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

# Check Flask installation
Write-Host ""
Write-Host "Checking Flask installation..."
try {
    $flaskCheck = python -c "import flask; print(f'Flask version: {flask.__version__}')"
    Write-Host $flaskCheck -ForegroundColor Green
} catch {
    Write-Host "Error: Flask not installed or not accessible" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host ""
    Write-Host "Try installing Flask with: pip install flask"
    exit 1
}

# Check port availability
Write-Host ""
Write-Host "Checking if port 8080 is available..."
$portCheck = netstat -ano | findstr :8080
if ($portCheck) {
    Write-Host "Warning: Port 8080 appears to be in use:" -ForegroundColor Yellow
    Write-Host $portCheck
    Write-Host "You may need to choose a different port or stop the process using port 8080"
} else {
    Write-Host "Port 8080 is available" -ForegroundColor Green
}

# Try to run the minimal Flask app
Write-Host ""
Write-Host "Attempting to run minimal Flask app on port 8080..."
Write-Host "Press Ctrl+C to stop the server when done"
Write-Host "==============================================="

try {
    python -c "
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Flask server is running on port 8080!'

if __name__ == '__main__':
    print('Starting Flask server on port 8080...')
    app.run(host='localhost', port=8080, debug=True)
"
} catch {
    Write-Host "Error running Flask app:" -ForegroundColor Red
    Write-Host $_.Exception.Message
}

Write-Host ""
Write-Host "Script completed. Press any key to exit."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

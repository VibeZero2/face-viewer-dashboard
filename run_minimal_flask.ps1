# PowerShell script to check port 8080 and run a minimal Flask app

# Check if port 8080 is in use
$portInUse = $false
try {
    $connection = New-Object System.Net.Sockets.TcpClient("localhost", 8080)
    if ($connection.Connected) {
        $portInUse = $true
        $connection.Close()
    }
} catch {
    $portInUse = $false
}

if ($portInUse) {
    Write-Host "ERROR: Port 8080 is already in use by another process!" -ForegroundColor Red
    Write-Host "Please close any applications that might be using this port."
    Write-Host "Common applications that use port 8080:"
    Write-Host "- Other Flask applications"
    Write-Host "- Apache Tomcat"
    Write-Host "- Development servers"
    
    # List processes using port 8080
    Write-Host "`nAttempting to find processes using port 8080..." -ForegroundColor Yellow
    try {
        $netstatOutput = netstat -ano | findstr :8080
        Write-Host "Processes using port 8080:" -ForegroundColor Yellow
        Write-Host $netstatOutput
        
        # Extract PIDs
        $pids = @()
        $netstatOutput | ForEach-Object {
            if ($_ -match ":8080\s+.*?LISTENING\s+(\d+)") {
                $pids += $matches[1]
            }
        }
        
        if ($pids.Count -gt 0) {
            Write-Host "`nProcess details:" -ForegroundColor Yellow
            $pids | ForEach-Object {
                $process = Get-Process -Id $_ -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "PID: $_ - Name: $($process.ProcessName) - Path: $($process.Path)"
                }
            }
        }
    } catch {
        Write-Host "Could not determine which process is using port 8080" -ForegroundColor Red
    }
} else {
    Write-Host "SUCCESS: Port 8080 is available!" -ForegroundColor Green
    
    # Create a minimal Flask app
    $flaskAppContent = @"
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello! The Flask server is running on port 8080."

@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    print("=" * 50)
    print("Starting MINIMAL Flask server on port 8080")
    print("=" * 50)
    print("Access at: http://localhost:8080")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=8080, debug=True)
"@
    
    # Save the Flask app to a temporary file
    $tempFlaskApp = "temp_minimal_flask_app.py"
    $flaskAppContent | Out-File -FilePath $tempFlaskApp -Encoding utf8
    
    Write-Host "`nCreated minimal Flask app: $tempFlaskApp" -ForegroundColor Green
    Write-Host "Starting Flask server..." -ForegroundColor Green
    
    # Run the Flask app
    try {
        Write-Host "`nRunning: python $tempFlaskApp" -ForegroundColor Cyan
        Write-Host "=" * 50
        Write-Host "Server will be available at: http://localhost:8080"
        Write-Host "Press Ctrl+C to stop the server"
        Write-Host "=" * 50
        
        python $tempFlaskApp
    } catch {
        Write-Host "Error running Flask app: $_" -ForegroundColor Red
    }
}

Write-Host "`nPress Enter to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

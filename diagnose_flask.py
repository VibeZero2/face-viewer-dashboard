"""
Flask Server Diagnostic Tool
This script will:
1. Check if Flask is installed
2. Check if port 8080 is available
3. Try to start a minimal Flask server
4. Provide detailed error information
"""
import sys
import socket
import subprocess
import os
import time
import platform
from datetime import datetime

def log(message):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def check_python_version():
    """Check Python version"""
    log(f"Python version: {sys.version}")
    log(f"Python executable: {sys.executable}")
    return True

def check_flask_installation():
    """Check if Flask is installed"""
    try:
        import flask
        log(f"Flask is installed (version: {flask.__version__})")
        return True
    except ImportError:
        log("ERROR: Flask is not installed")
        log("Please install Flask with: pip install flask")
        return False

def is_port_available(port):
    """Check if a port is available"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            if result == 0:
                log(f"ERROR: Port {port} is already in use")
                return False
            else:
                log(f"Port {port} is available")
                return True
    except Exception as e:
        log(f"Error checking port {port}: {str(e)}")
        return False

def find_process_using_port(port):
    """Find process using a specific port"""
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output(f"netstat -ano | findstr :{port}", shell=True).decode()
            for line in output.splitlines():
                if "LISTENING" in line:
                    parts = line.split()
                    pid = parts[-1]
                    try:
                        process_info = subprocess.check_output(f"tasklist /fi \"PID eq {pid}\"", shell=True).decode()
                        log(f"Process using port {port}:\n{process_info}")
                    except:
                        log(f"Process with PID {pid} is using port {port}")
        else:
            output = subprocess.check_output(f"lsof -i :{port}", shell=True).decode()
            log(f"Process using port {port}:\n{output}")
    except:
        log(f"Could not determine which process is using port {port}")

def test_minimal_flask_server(port):
    """Test starting a minimal Flask server"""
    try:
        log(f"Attempting to start a minimal Flask server on port {port}...")
        
        # Create a minimal Flask app
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def hello():
            return "Flask diagnostic test successful!"
        
        # Set up a timeout to kill the server after 5 seconds
        def shutdown_server():
            time.sleep(5)
            os._exit(0)
        
        import threading
        threading.Thread(target=shutdown_server, daemon=True).start()
        
        # Try to start the server
        log(f"Starting Flask server on port {port} (will automatically shut down after 5 seconds)...")
        app.run(host='0.0.0.0', port=port, debug=False)
        
        return True
    except Exception as e:
        log(f"ERROR starting Flask server: {str(e)}")
        return False

def check_network_config():
    """Check network configuration"""
    try:
        log("Checking network configuration...")
        if platform.system() == "Windows":
            output = subprocess.check_output("ipconfig", shell=True).decode()
            log("Network configuration (abbreviated):")
            for line in output.splitlines()[:20]:  # Show first 20 lines
                if "IPv4" in line or "Subnet" in line or "Adapter" in line:
                    log(f"  {line.strip()}")
        else:
            output = subprocess.check_output("ifconfig | head -20", shell=True).decode()
            log(f"Network configuration (abbreviated):\n{output}")
    except Exception as e:
        log(f"Error checking network configuration: {str(e)}")

def check_firewall():
    """Check if firewall might be blocking the port"""
    log("Checking for potential firewall issues...")
    if platform.system() == "Windows":
        try:
            output = subprocess.check_output("netsh advfirewall show currentprofile", shell=True).decode()
            if "State                                 ON" in output:
                log("Windows Firewall is ON - it might be blocking port 8080")
                log("Consider adding a firewall rule or temporarily disabling the firewall")
            else:
                log("Windows Firewall appears to be OFF")
        except:
            log("Could not determine Windows Firewall status")
    else:
        try:
            output = subprocess.check_output("sudo ufw status", shell=True).decode()
            log(f"Firewall status:\n{output}")
        except:
            log("Could not determine firewall status")

def main():
    """Main diagnostic function"""
    log("=" * 60)
    log("FLASK SERVER DIAGNOSTIC TOOL")
    log("=" * 60)
    
    # Check Python version
    check_python_version()
    
    # Check Flask installation
    if not check_flask_installation():
        return
    
    # Check port 8080
    port = 8080
    if not is_port_available(port):
        find_process_using_port(port)
        log(f"Trying an alternative port (5000) to see if it's a port-specific issue...")
        if is_port_available(5000):
            test_minimal_flask_server(5000)
    else:
        # Try to start a minimal Flask server on port 8080
        test_minimal_flask_server(port)
    
    # Check network configuration
    check_network_config()
    
    # Check firewall
    check_firewall()
    
    log("=" * 60)
    log("DIAGNOSTIC COMPLETE")
    log("=" * 60)

if __name__ == "__main__":
    main()
    input("Press Enter to exit...")

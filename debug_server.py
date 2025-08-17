"""
Debug server for Face Viewer Dashboard
This script provides detailed output about the server status
"""
from flask import Flask, render_template_string
import os
import socket
import sys

app = Flask(__name__)

@app.route('/')
def hello():
    # Get system info for debugging
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    python_version = sys.version
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Debug Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; background-color: white; 
                        border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .success { color: green; font-weight: bold; }
            .info { background-color: #f0f0f0; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
            .debug { background-color: #ffe; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
            pre { background-color: #f8f8f8; padding: 10px; border-radius: 4px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Face Viewer Dashboard - Debug Server</h1>
            <p class="success">✅ Debug server is running successfully!</p>
            
            <h2>Connection Information</h2>
            <div class="info">
                <p><strong>Hostname:</strong> {{ hostname }}</p>
                <p><strong>Local IP:</strong> {{ local_ip }}</p>
                <p><strong>Port:</strong> {{ port }}</p>
                <p><strong>Access URLs:</strong></p>
                <ul>
                    <li>Local: <a href="http://localhost:{{ port }}">http://localhost:{{ port }}</a></li>
                    <li>Network: <a href="http://{{ local_ip }}:{{ port }}">http://{{ local_ip }}:{{ port }}</a></li>
                </ul>
            </div>
            
            <h2>System Information</h2>
            <div class="debug">
                <p><strong>Python Version:</strong> {{ python_version }}</p>
                <p><strong>Working Directory:</strong> {{ working_dir }}</p>
                <p><strong>Environment Variables:</strong></p>
                <pre>{{ env_vars }}</pre>
            </div>
            
            <h2>Next Steps</h2>
            <p>If you can see this page, your server is working correctly. Try these links:</p>
            <ul>
                <li><a href="/dashboard-preview">View Dashboard Preview</a></li>
                <li><a href="/test-connection">Test Database Connection</a></li>
            </ul>
        </div>
    </body>
    </html>
    """, 
    hostname=hostname,
    local_ip=local_ip,
    port=port,
    python_version=python_version,
    working_dir=os.getcwd(),
    env_vars="\n".join([f"{k}: {v}" for k, v in sorted(os.environ.items()) if k.startswith(('FLASK', 'DASHBOARD', 'FACE', 'PORT', 'PATH', 'PYTHON'))])
    )

@app.route('/dashboard-preview')
def dashboard_preview():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard Preview</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f5f5f5;
            }
            .navbar {
                background-color: #343a40;
                padding: 15px;
                color: white;
            }
            .navbar a {
                color: white;
                text-decoration: none;
                margin-right: 15px;
                font-weight: bold;
            }
            .navbar a.active {
                color: #ffc107;
            }
            .container {
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
                background-color: white;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .stats-container {
                display: flex;
                flex-wrap: wrap;
                justify-content: space-between;
                margin-bottom: 20px;
            }
            .stat-card {
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                padding: 15px;
                width: 22%;
                margin-bottom: 15px;
            }
            .stat-card h3 {
                margin-top: 0;
                color: #343a40;
            }
            .stat-card p {
                font-size: 24px;
                font-weight: bold;
                margin: 0;
                color: #007bff;
            }
        </style>
    </head>
    <body>
        <div class="navbar">
            <a href="/" class="active">Dashboard</a>
            <a href="#">Analytics</a>
            <a href="#">Participants</a>
            <a href="#">Export</a>
            <a href="#">Admin</a>
        </div>

        <div class="container">
            <h1>Dashboard Preview</h1>
            
            <div class="stats-container">
                <div class="stat-card">
                    <h3>Total Participants</h3>
                    <p>42</p>
                </div>
                <div class="stat-card">
                    <h3>Total Responses</h3>
                    <p>126</p>
                </div>
                <div class="stat-card">
                    <h3>Avg. Trust Rating</h3>
                    <p>5.2</p>
                </div>
                <div class="stat-card">
                    <h3>Trust SD</h3>
                    <p>1.3</p>
                </div>
            </div>
            
            <p><a href="/" style="color: #007bff;">← Back to Debug Page</a></p>
        </div>
    </body>
    </html>
    """)

@app.route('/test-connection')
def test_connection():
    # Test if we can create a data directory
    try:
        data_dir = os.path.join(os.getcwd(), 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            dir_created = True
        else:
            dir_created = False
            
        # Try to write a test file
        test_file_path = os.path.join(data_dir, 'test_connection.txt')
        with open(test_file_path, 'w') as f:
            f.write('Connection test successful at ' + os.path.basename(__file__))
            
        file_written = True
    except Exception as e:
        dir_created = False
        file_written = False
        error_message = str(e)
    
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Connection Test</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; background-color: white; 
                        border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            h1 { color: #333; }
            .success { color: green; font-weight: bold; }
            .error { color: red; font-weight: bold; }
            .info { background-color: #f0f0f0; padding: 10px; border-radius: 4px; margin-bottom: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Connection Test Results</h1>
            
            {% if file_written %}
            <p class="success">✅ Connection test successful!</p>
            {% else %}
            <p class="error">❌ Connection test failed: {{ error_message }}</p>
            {% endif %}
            
            <div class="info">
                <p><strong>Data Directory:</strong> {{ data_dir }}</p>
                <p><strong>Directory Created:</strong> {{ 'Yes' if dir_created else 'No (already existed)' }}</p>
                <p><strong>Test File:</strong> {{ test_file_path }}</p>
                <p><strong>File Written:</strong> {{ 'Yes' if file_written else 'No' }}</p>
            </div>
            
            <p><a href="/" style="color: #007bff;">← Back to Debug Page</a></p>
        </div>
    </body>
    </html>
    """, 
    data_dir=data_dir,
    dir_created=dir_created,
    test_file_path=test_file_path,
    file_written=file_written,
    error_message=error_message if not file_written else ""
    )

if __name__ == '__main__':
    # Explicitly use port 8080
    port = 8080
    
    print("=" * 50)
    print(f"Starting Face Viewer Dashboard Debug Server")
    print("=" * 50)
    print(f"Server will be available at:")
    print(f"  http://localhost:{port}")
    
    # Get local IP for network access
    hostname = socket.gethostname()
    try:
        local_ip = socket.gethostbyname(hostname)
        print(f"  http://{local_ip}:{port}")
    except Exception as e:
        print(f"Error getting local IP: {e}")
    
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    # Check if port is available
    try:
        test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        test_socket.bind(('localhost', port))
        test_socket.close()
        print(f"Port {port} is available!")
    except Exception as e:
        print(f"WARNING: Port {port} may not be available: {e}")
        print("The server may fail to start if the port is in use.")
    
    try:
        # Run with explicit host and port
        print("Starting Flask server...")
        app.run(host='localhost', port=port, debug=True)
    except Exception as e:
        print(f"ERROR: Failed to start server: {e}")
        import traceback
        traceback.print_exc()

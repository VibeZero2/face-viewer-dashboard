"""
Ultra Minimal Flask App - Port 5000 Test
"""
from flask import Flask, render_template_string

app = Flask(__name__)

# Simple HTML template
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Flask Test - Port 5000</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px;
            line-height: 1.6;
            color: #333;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
        h1 { color: #0066cc; }
        .success { color: green; font-weight: bold; }
        .info { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Flask Server Test</h1>
        <p class="success">✅ Success! Flask server is running on port 5000.</p>
        <p>This confirms that:</p>
        <ul>
            <li>Python is working correctly</li>
            <li>Flask is installed properly</li>
            <li>Port 5000 is available and not blocked</li>
        </ul>
        <p class="info">Server time: {{ server_time }}</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    from datetime import datetime
    return render_template_string(HTML, server_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

@app.route('/health')
def health():
    return {"status": "healthy", "port": 5000}

if __name__ == '__main__':
    # Print user-friendly message
    print("=" * 50)
    print("Starting Ultra Minimal Flask App on port 5000")
    print("=" * 50)
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the Flask app
    app.run(host='localhost', port=5000, debug=True)

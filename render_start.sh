#!/bin/bash
# Script to start the Face Viewer Dashboard on Render

# Create a properly formatted Python file
cat > minimal_app.py << 'EOF'
"""
Minimal Flask application for the Face Viewer Dashboard
"""
import os
import sys
from flask import Flask, render_template_string

# Create Flask app
app = Flask(__name__)

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Face Viewer Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }
        .info {
            background-color: #f0f0f0;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        .success {
            color: green;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Face Viewer Dashboard</h1>
        <p class="success">✅ Application is running!</p>
        
        <h2>Environment Information</h2>
        <div class="info">
            <p><strong>Python Version:</strong> {{ python_version }}</p>
            <p><strong>Working Directory:</strong> {{ working_dir }}</p>
            <p><strong>Available Files:</strong></p>
            <ul>
                {% for file in files %}
                <li>{{ file }}</li>
                {% endfor %}
            </ul>
        </div>
        
        <h2>Next Steps</h2>
        <p>This is a minimal version of the Face Viewer Dashboard. Once deployment is working, we can implement the full functionality.</p>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the index page with environment information"""
    # Get environment information
    python_version = sys.version
    working_dir = os.getcwd()
    
    try:
        files = os.listdir(working_dir)
    except Exception as e:
        files = [f"Error listing files: {e}"]
    
    # Render the template with environment information
    return render_template_string(
        HTML_TEMPLATE, 
        python_version=python_version,
        working_dir=working_dir,
        files=files
    )

# This is the standard WSGI application variable that Gunicorn looks for
application = app
EOF

# Print file contents to verify
echo "Created minimal_app.py:"
cat minimal_app.py

# Start Gunicorn with the minimal app
echo "Starting Gunicorn with minimal_app.py..."
gunicorn minimal_app:application

"""
Simplified version of the Face Viewer Dashboard app without encryption requirements
"""
import os
import sys
from flask import Flask, render_template_string

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev_key_for_testing')

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Face Viewer Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            padding-top: 2rem;
        }
        .header {
            background-color: #f8f9fa;
            padding: 1rem;
            margin-bottom: 2rem;
            border-radius: 0.25rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Face Viewer Dashboard</h1>
            <p class="text-success">✅ Application is running!</p>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h2>Environment Information</h2>
                    </div>
                    <div class="card-body">
                        <p><strong>Python Version:</strong> {{ python_version }}</p>
                        <p><strong>Working Directory:</strong> {{ working_dir }}</p>
                        <p><strong>Environment Variables:</strong></p>
                        <ul>
                            {% for var in env_vars %}
                            <li>{{ var }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
            
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h2>Available Files</h2>
                    </div>
                    <div class="card-body">
                        <ul>
                            {% for file in files %}
                            <li>{{ file }}</li>
                            {% endfor %}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card mt-4">
            <div class="card-header">
                <h2>Next Steps</h2>
            </div>
            <div class="card-body">
                <p>This is a simplified version of the Face Viewer Dashboard without encryption requirements.</p>
                <p>To deploy the full version, set the following environment variables in Render:</p>
                <ul>
                    <li><code>FERNET_KEY</code>: A valid 32-byte URL-safe base64-encoded encryption key</li>
                    <li><code>FLASK_SECRET_KEY</code>: A secure secret key for Flask sessions</li>
                    <li><code>FACE_VIEWER_DATA_DIR</code>: Path to data directory</li>
                    <li><code>FACE_VIEWER_BACKEND_URL</code>: URL of the backend API</li>
                    <li><code>ADMIN_API_KEY</code>: API key for admin operations</li>
                </ul>
                <p>Once these are set, you can switch back to the full application.</p>
            </div>
        </div>
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
    
    # Get environment variables (excluding sensitive ones)
    env_vars = []
    for key in sorted(os.environ.keys()):
        if not any(sensitive in key.lower() for sensitive in ['key', 'secret', 'password', 'token']):
            env_vars.append(f"{key}: {os.environ.get(key)}")
    
    try:
        files = sorted(os.listdir(working_dir))
    except Exception as e:
        files = [f"Error listing files: {e}"]
    
    # Render the template with environment information
    return render_template_string(
        HTML_TEMPLATE, 
        python_version=python_version,
        working_dir=working_dir,
        env_vars=env_vars,
        files=files
    )

# This is the standard WSGI application variable that Gunicorn looks for
app = app
application = app

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

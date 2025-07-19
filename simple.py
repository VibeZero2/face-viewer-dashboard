"""
Minimal Flask application for Face Viewer Dashboard
This is a simplified version that uses minimal dependencies
"""
from flask import Flask, render_template_string
import os
import sys

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('DASHBOARD_SECRET_KEY', os.urandom(24).hex())

@app.route('/')
def index():
    """Render the index page"""
    return render_template_string("""
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
            .success {
                color: green;
                font-weight: bold;
            }
            .info {
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Face Viewer Dashboard</h1>
            <p class="success">✅ Application is running successfully!</p>
            
            <h2>Environment Information</h2>
            <div class="info">
                <p><strong>Python Version:</strong> {{ python_version }}</p>
                <p><strong>Working Directory:</strong> {{ working_dir }}</p>
                <p><strong>Environment Variables:</strong></p>
                <ul>
                    {% for key, value in env_vars.items() %}
                    <li>{{ key }}: {% if "SECRET" in key or "KEY" in key %}[HIDDEN]{% else %}{{ value }}{% endif %}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </body>
    </html>
    """, 
    python_version=sys.version,
    working_dir=os.getcwd(),
    env_vars={k: v for k, v in os.environ.items() if k.startswith(('FLASK', 'DASHBOARD', 'FACE', 'PORT'))}
    )

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return {"status": "ok", "message": "Face Viewer Dashboard is running"}

# This is the standard WSGI application variable that Gunicorn looks for
application = app

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

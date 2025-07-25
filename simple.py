"""
Minimal Flask application for Face Viewer Dashboard
This is a simplified version that uses minimal dependencies
"""
from flask import Flask, render_template_string, render_template
import os
import sys

# Import blueprints
from routes.dashboard_no_pandas import dashboard_bp
from routes.analytics_no_pandas import analytics_bp
from routes.export_no_pandas import export_bp
from routes.participants_no_pandas import participants_bp
from routes.api import api_bp

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('DASHBOARD_SECRET_KEY', os.urandom(24).hex())

# Register blueprints
app.register_blueprint(dashboard_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(export_bp)
app.register_blueprint(participants_bp)
app.register_blueprint(api_bp)

@app.route('/')
def index():
    """Redirect to the dashboard page"""
    from flask import redirect, url_for
    return redirect(url_for('dashboard.dashboard'))
    
# Legacy index page, keeping for reference
def legacy_index():
    """Render the legacy index page"""
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

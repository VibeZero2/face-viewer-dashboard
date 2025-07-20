"""
Face Viewer Dashboard Flask App
With caching for dashboard statistics
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
import secrets
import json

# Import integration modules
from app_integration import integrate_participant_management
from app_dashboard_integration import integrate_dashboard

# Create Flask app
app = Flask(__name__)

# Configure app
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16))
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['USE_DEMO_DATA'] = os.environ.get('USE_DEMO_DATA', 'False').lower() == 'true'

# Integrate components
app = integrate_participant_management(app)
app = integrate_dashboard(app)

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/healthz')
def health_check():
    """Health check endpoint for Render"""
    return "OK", 200

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    """404 page"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """500 page"""
    return render_template('errors/500.html'), 500

# Run app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

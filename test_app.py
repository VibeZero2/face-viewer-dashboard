"""
Test script for Face Viewer Dashboard
This script tests the login and registration functionality
"""
import os
import sys
from flask import Flask

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Create a minimal Flask app for testing
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret_key'
app.config['TESTING'] = True

# Initialize admin authentication and permissions
from admin.auth import AdminAuth
from admin.audit import AuditLog
from admin.permissions import Permissions

# Initialize the modules
admin_auth = AdminAuth(app)
audit_log = AuditLog(app)
permissions = Permissions(app)

# Import and register admin blueprint
from admin.routes import admin_bp
app.register_blueprint(admin_bp, url_prefix='/admin')

# Add a simple index route
@app.route('/')
def index():
    return "Test app is running. Visit <a href='/admin/login'>Login</a> or <a href='/admin/register'>Register</a>"

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Run the app
    app.run(debug=True, port=5000)

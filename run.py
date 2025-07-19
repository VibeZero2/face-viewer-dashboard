"""
Face Viewer Dashboard - Run Script
This script starts the Face Viewer Dashboard application.
"""
import os
import sys

# Add the current directory to the path so that the app module can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the simplified Flask app to avoid pandas dependency
from simple import app

# This is needed for Gunicorn to find the app
application = app

# This is for compatibility with different WSGI servers
app = application

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')

"""
Face Viewer Dashboard - Run Script
This script starts the Face Viewer Dashboard application.
"""
import os
from app import app

# This is needed for Gunicorn to find the app
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')

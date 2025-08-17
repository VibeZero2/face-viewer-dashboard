"""
Face Viewer Dashboard - WSGI Entry Point
This file serves as the WSGI entry point for Gunicorn.
Import the app from app_production_5000.py which includes analytics dashboard.
"""

# Import the app from app_production_5000.py
from app_production_5000 import app

# This is the standard WSGI application variable that Gunicorn looks for
application = app

if __name__ == "__main__":
    app.run(debug=True)

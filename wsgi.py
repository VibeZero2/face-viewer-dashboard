"""
Face Viewer Dashboard - WSGI Entry Point
This file serves as the WSGI entry point for Gunicorn.
Import the app from simple.py which has no login requirements.
"""

# Import the app from simple.py
from simple import app

# This is the standard WSGI application variable that Gunicorn looks for
application = app

if __name__ == "__main__":
    app.run(debug=True)

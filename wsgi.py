"""
Face Viewer Dashboard - WSGI Entry Point
This file serves as the WSGI entry point for Gunicorn.
"""
# Import the completely pandas-free app to avoid dependency issues
from app_no_pandas import app

# This is the standard WSGI application variable that Gunicorn looks for
application = app

if __name__ == "__main__":
    app.run()

"""
WSGI entry point for Render deployment
"""
from dashboard_app import app

# Create the WSGI application object
application = app

if __name__ == "__main__":
    application.run()

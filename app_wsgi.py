"""
Simple WSGI entry point for the Face Viewer Dashboard
"""
import os
import sys

# Add the current directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import the Flask app
try:
    from app import app as application
except ImportError as e:
    print(f"Error importing app: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Python path: {sys.path}")
    print(f"Directory contents: {os.listdir(current_dir)}")
    raise

# For debugging
print(f"Successfully imported app from {current_dir}")
print(f"Python version: {sys.version}")

if __name__ == "__main__":
    application.run()

#!/usr/bin/env python
"""
Debug script for Face Viewer Dashboard deployment on Render
"""
import os
import sys
import importlib.util

def debug_environment():
    """Print debug information about the environment"""
    print("=" * 50)
    print("DEBUG INFORMATION")
    print("=" * 50)
    
    # Current directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Python version
    print(f"Python version: {sys.version}")
    
    # Python path
    print("Python path:")
    for path in sys.path:
        print(f"  - {path}")
    
    # List files in current directory
    print("\nFiles in current directory:")
    for file in sorted(os.listdir(current_dir)):
        print(f"  - {file}")
    
    # Try to import app
    print("\nTrying to import app module:")
    try:
        import app
        print("  Success! app module imported")
        print(f"  app.__file__: {app.__file__}")
    except ImportError as e:
        print(f"  Failed to import app: {e}")
    
    # Check if specific files exist
    files_to_check = ['app.py', 'run.py', 'wsgi.py', 'app_wsgi.py']
    print("\nChecking for specific files:")
    for file in files_to_check:
        path = os.path.join(current_dir, file)
        exists = os.path.exists(path)
        print(f"  - {file}: {'EXISTS' if exists else 'NOT FOUND'}")
        if exists:
            print(f"    Full path: {path}")
            print(f"    Size: {os.path.getsize(path)} bytes")
    
    print("=" * 50)

if __name__ == "__main__":
    debug_environment()
    
    # Create a simple WSGI application for testing
    def simple_app(environ, start_response):
        """Simple WSGI application that returns debug information"""
        status = '200 OK'
        headers = [('Content-type', 'text/plain; charset=utf-8')]
        start_response(status, headers)
        
        output = ["Face Viewer Dashboard Debug Information\n\n"]
        
        # Add environment information
        output.append("Environment Variables:\n")
        for key, value in sorted(os.environ.items()):
            if not key.startswith(('SECRET', 'KEY', 'PASSWORD', 'TOKEN')):
                output.append(f"{key}: {value}\n")
        
        return [line.encode('utf-8') for line in output]
    
    # Export the application
    application = simple_app
    
    print("Simple WSGI application created and ready to serve")
    print("Use 'gunicorn debug_app:application' to start the server")

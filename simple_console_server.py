"""
Super simple Flask server with console output for debugging
"""
import sys
import os
from flask import Flask

# Create Flask app
app = Flask(__name__)

@app.route('/')
def hello():
    print("Root route accessed!")
    sys.stdout.flush()  # Force output to console
    return """
    <html>
        <head><title>Test Server</title></head>
        <body>
            <h1>Test Server Working!</h1>
            <p>If you can see this, the server is working correctly.</p>
        </body>
    </html>
    """

if __name__ == '__main__':
    # Print diagnostic info
    print("\n" + "="*60)
    print("STARTING SERVER - DIAGNOSTIC INFO")
    print("="*60)
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Flask app: {app}")
    print("="*60 + "\n")
    
    # Flush to ensure output appears
    sys.stdout.flush()
    
    # Run with explicit host and port
    print("Starting server on http://localhost:5000")
    sys.stdout.flush()
    
    try:
        app.run(host='localhost', port=5000, debug=True)
    except Exception as e:
        print(f"ERROR STARTING SERVER: {str(e)}")
        print("="*60)
        sys.stdout.flush()
        input("Press Enter to exit...")  # Keep console window open

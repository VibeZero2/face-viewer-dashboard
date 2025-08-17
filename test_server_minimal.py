"""
Minimal test server with detailed error output
"""
from flask import Flask
import sys
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return """
    <html>
        <head>
            <title>Server Test</title>
            <style>
                body { font-family: Arial; margin: 40px; }
                .success { color: green; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>Test Server</h1>
            <p class="success">Server is running successfully!</p>
            <p>If you can see this message, the Flask server is working correctly.</p>
            <p>Python version: {}</p>
            <p>Working directory: {}</p>
        </body>
    </html>
    """.format(sys.version, os.getcwd())

if __name__ == '__main__':
    print("=" * 50)
    print("Starting minimal test server")
    print("=" * 50)
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    # Use 127.0.0.1 instead of 0.0.0.0 for Windows compatibility
    app.run(host='127.0.0.1', port=5000, debug=True)

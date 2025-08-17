from flask import Flask

# Create a minimal Flask application
app = Flask(__name__)

@app.route('/')
def index():
    return """
    <html>
        <head>
            <title>Minimal Flask App</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                .container { max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
                h1 { color: #333; }
                .success { color: green; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Minimal Flask App</h1>
                <p class="success">✅ Server is running successfully on port 8080!</p>
                <p>This confirms that port 8080 is available and Flask is working correctly.</p>
                <p>You can now proceed with debugging the main application.</p>
            </div>
        </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    print("=" * 50)
    print("Starting minimal Flask server on port 8080")
    print("=" * 50)
    print("Access at: http://localhost:8080")
    print("Press Ctrl+C to stop the server")
    
    # Run with explicit host and port
    app.run(host='0.0.0.0', port=8080)

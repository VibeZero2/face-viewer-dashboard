from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return """
    <html>
    <head>
        <title>Super Minimal Flask Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
            h1 { color: #333; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Super Minimal Flask Server</h1>
            <p>This server is running successfully!</p>
            <p>If you can see this message, the server is working correctly.</p>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    print("Starting super minimal server on port 8080...")
    print("Access at: http://127.0.0.1:8080")
    app.run(host='127.0.0.1', port=8080, debug=True)

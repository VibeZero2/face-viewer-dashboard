from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return """
    <html>
    <head>
        <title>Simple Test</title>
        <style>
            body { font-family: Arial; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; }
            h1 { color: #333; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Simple Test Server</h1>
            <p>This is a minimal test server to verify Flask is working.</p>
            <p>If you can see this page, the server is running correctly!</p>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("Starting server on http://localhost:10000")
    app.run(host='0.0.0.0', port=10000, debug=True)

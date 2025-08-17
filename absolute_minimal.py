from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello! The Flask server is running on port 8080."

@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    print("=" * 50)
    print("Starting MINIMAL Flask server on port 8080")
    print("=" * 50)
    print("Access at: http://localhost:8080")
    print("Press Ctrl+C to stop the server")
    app.run(host='0.0.0.0', port=8080, debug=True)

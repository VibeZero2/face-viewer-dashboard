from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "Flask server is running on port 8080!"

@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    print("Starting minimal test server on port 8080...")
    print("Access at: http://localhost:8080")
    app.run(host='localhost', port=8080, debug=True)

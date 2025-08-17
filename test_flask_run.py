"""
Simple Flask test script to verify server runs correctly
"""
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return "Flask server is running!"

@app.route('/test')
def test():
    return "Test route is working!"

if __name__ == '__main__':
    print("Starting Flask test server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)

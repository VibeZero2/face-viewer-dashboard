"""
Face Viewer Dashboard - Pandas-Free App
This file provides a minimal Flask app without pandas dependencies.
"""
from flask import Flask, render_template, jsonify

# Create a Flask app
app = Flask(__name__)

# Configure the app
app.config['SECRET_KEY'] = 'your-secret-key'

# Define routes
@app.route('/')
def index():
    return render_template('index.html', title='Face Viewer Dashboard')

@app.route('/health')
@app.route('/healthz')
def health():
    return jsonify({"status": "healthy", "message": "Face Viewer Dashboard is running without pandas"})

# This ensures that if anything imports from this file, it gets the pandas-free version
print("Using completely pandas-free app")

if __name__ == '__main__':
    app.run(debug=True)

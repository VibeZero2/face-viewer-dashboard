"""
Face Viewer Dashboard - Simplified App
No login required, minimal dependencies
"""
from flask import Flask, render_template, redirect, url_for

# Initialize Flask app
app = Flask(__name__)

# Root route redirects to dashboard
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

# Dashboard route
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Analytics route
@app.route('/r-analysis')
def r_analysis():
    return render_template('r_analysis.html')

# Health check
@app.route('/health')
def health():
    return {"status": "healthy"}

# This is the standard WSGI application variable that Gunicorn looks for
application = app

if __name__ == '__main__':
    app.run(debug=True)

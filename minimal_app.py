import os
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        return f"""
        <html>
        <head>
            <title>Face Viewer Dashboard</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                h1 {{ color: #333; }}
                .menu {{ margin-bottom: 20px; }}
                .menu a {{ margin-right: 15px; text-decoration: none; color: #0066cc; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="menu">
                    <a href="/dashboard">Dashboard</a>
                    <a href="/r-analysis">Analytics</a>
                </div>
                <h1>Face Viewer Dashboard</h1>
                <p>This is a minimal version of the Face Viewer Dashboard.</p>
                <p>The application is running successfully!</p>
                <p>Error loading template: {str(e)}</p>
            </div>
        </body>
        </html>
        """

@app.route('/r-analysis')
def r_analysis():
    try:
        return render_template('r_analysis.html')
    except Exception as e:
        return f"""
        <html>
        <head>
            <title>Face Viewer Analytics</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
                h1 {{ color: #333; }}
                .menu {{ margin-bottom: 20px; }}
                .menu a {{ margin-right: 15px; text-decoration: none; color: #0066cc; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="menu">
                    <a href="/dashboard">Dashboard</a>
                    <a href="/r-analysis">Analytics</a>
                </div>
                <h1>Face Viewer Analytics</h1>
                <p>This is the analytics page.</p>
                <p>Error loading template: {str(e)}</p>
            </div>
        </body>
        </html>
        """

@app.route('/health')
def health():
    return {"status": "healthy"}

# This is the standard WSGI application variable that Gunicorn looks for
application = app

if __name__ == '__main__':
    print("Starting server on port 8080...")
    print("Access the dashboard at: http://localhost:8080")
    app.run(host='localhost', port=8080, debug=True)

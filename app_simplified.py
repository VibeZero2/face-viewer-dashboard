from flask import Flask, redirect, url_for, render_template

app = Flask(__name__)

# Import dashboard integration
from app_dashboard_integration import integrate_dashboard

# Integrate dashboard components
app = integrate_dashboard(app)

@app.route('/')
def index():
    return redirect('/dashboard')

# Health check
@app.route('/health')
def health():
    return {"status": "healthy"}

# This is the standard WSGI application variable that Gunicorn looks for
application = app

if __name__ == '__main__':
    print("Starting server on port 8080...")
    print("Access the dashboard at: http://localhost:8080")
    app.run(host='localhost', port=8080, debug=True)

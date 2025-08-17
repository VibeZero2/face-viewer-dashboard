from flask import Flask, redirect

app = Flask(__name__)

# Root route redirects to dashboard
@app.route('/')
def index():
    return redirect('/dashboard')

# Import dashboard blueprint
from routes.dashboard import dashboard_bp

# Register blueprint
app.register_blueprint(dashboard_bp)

# Health check
@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    print("Starting server on port 8080...")
    print("Access the dashboard at: http://localhost:8080")
    app.run(host='localhost', port=8080)

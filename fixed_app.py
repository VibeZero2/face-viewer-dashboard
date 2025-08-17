from flask import Flask, redirect, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    print("Starting server on port 8080...")
    print("Access the dashboard at: http://localhost:8080")
    app.run(host='localhost', port=8080)

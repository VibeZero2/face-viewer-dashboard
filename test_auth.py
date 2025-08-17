"""
Test script for admin authentication
"""
import os
import sys
from flask import Flask, render_template, redirect, url_for, request, flash, session

# Create a minimal Flask app for testing
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret_key'
app.config['TESTING'] = True

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Initialize admin authentication
from admin.auth import AdminAuth
admin_auth = AdminAuth(app)

# Simple routes for testing
@app.route('/')
def index():
    return """
    <h1>Authentication Test</h1>
    <p><a href='/register'>Register</a></p>
    <p><a href='/login'>Login</a></p>
    <p><a href='/logout'>Logout</a></p>
    <p><a href='/status'>Check Status</a></p>
    """

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if admin_auth.create_user(username, password, role='admin'):
            flash('Registration successful!', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists', 'danger')
    
    return """
    <h1>Register</h1>
    <form method="POST">
        <p>Username: <input type="text" name="username" required></p>
        <p>Password: <input type="password" name="password" required></p>
        <p><button type="submit">Register</button></p>
    </form>
    <p><a href='/'>Back to Home</a></p>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if admin_auth.authenticate(username, password):
            flash('Login successful!', 'success')
            return redirect(url_for('status'))
        else:
            flash('Invalid username or password', 'danger')
    
    return """
    <h1>Login</h1>
    <form method="POST">
        <p>Username: <input type="text" name="username" required></p>
        <p>Password: <input type="password" name="password" required></p>
        <p><button type="submit">Login</button></p>
    </form>
    <p><a href='/'>Back to Home</a></p>
    """

@app.route('/logout')
def logout():
    admin_auth.logout()
    return redirect(url_for('index'))

@app.route('/status')
def status():
    is_authenticated = admin_auth.is_authenticated()
    user = admin_auth.current_user()
    
    if is_authenticated:
        return f"""
        <h1>Authentication Status</h1>
        <p>Authenticated: {is_authenticated}</p>
        <p>Username: {user['username']}</p>
        <p>Role: {user['role']}</p>
        <p><a href='/logout'>Logout</a></p>
        <p><a href='/'>Back to Home</a></p>
        """
    else:
        return """
        <h1>Authentication Status</h1>
        <p>Not authenticated</p>
        <p><a href='/login'>Login</a></p>
        <p><a href='/'>Back to Home</a></p>
        """

if __name__ == '__main__':
    app.run(debug=True, port=5000)

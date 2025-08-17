"""
Test script for login and registration functionality
"""
import os
import sys
import logging
from flask import Flask, render_template, redirect, url_for, request, flash, session

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    <h1>Login and Registration Test</h1>
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
        confirm_password = request.form.get('confirm_password')
        
        logger.debug(f"Registration attempt for user: {username}")
        
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('admin/register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('admin/register.html')
        
        if admin_auth.create_user(username, password, role='admin'):
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Username already exists', 'danger')
    
    return render_template('admin/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        logger.debug(f"Login attempt for user: {username}")
        
        if admin_auth.authenticate(username, password):
            flash('Login successful!', 'success')
            return redirect(url_for('status'))
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('admin/login.html')

@app.route('/logout')
def logout():
    admin_auth.logout()
    flash('You have been logged out', 'info')
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
    logger.info("Starting test login/register application")
    app.run(debug=True, port=5000)

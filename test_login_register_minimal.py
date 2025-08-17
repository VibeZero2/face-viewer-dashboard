"""
Minimal test script for login and registration functionality
"""
import os
import sys
import logging
from flask import Flask, render_template, redirect, url_for, request, flash, session

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])
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
            flash('Username and password are required')
            return """
            <h1>Register</h1>
            <p style="color: red;">Username and password are required</p>
            <form method="POST">
                <p>Username: <input type="text" name="username" required></p>
                <p>Password: <input type="password" name="password" required></p>
                <p>Confirm Password: <input type="password" name="confirm_password" required></p>
                <p><button type="submit">Register</button></p>
            </form>
            <p><a href='/'>Back to Home</a></p>
            """
            
        if password != confirm_password:
            flash('Passwords do not match')
            return """
            <h1>Register</h1>
            <p style="color: red;">Passwords do not match</p>
            <form method="POST">
                <p>Username: <input type="text" name="username" required></p>
                <p>Password: <input type="password" name="password" required></p>
                <p>Confirm Password: <input type="password" name="confirm_password" required></p>
                <p><button type="submit">Register</button></p>
            </form>
            <p><a href='/'>Back to Home</a></p>
            """
        
        if admin_auth.create_user(username, password, role='admin'):
            logger.debug(f"User {username} registered successfully")
            return f"""
            <h1>Registration Successful</h1>
            <p>User {username} has been registered successfully!</p>
            <p><a href='/login'>Login</a></p>
            <p><a href='/'>Back to Home</a></p>
            """
        else:
            logger.debug(f"Username {username} already exists")
            return f"""
            <h1>Registration Failed</h1>
            <p style="color: red;">Username {username} already exists</p>
            <p><a href='/register'>Try again</a></p>
            <p><a href='/'>Back to Home</a></p>
            """
    
    return """
    <h1>Register</h1>
    <form method="POST">
        <p>Username: <input type="text" name="username" required></p>
        <p>Password: <input type="password" name="password" required></p>
        <p>Confirm Password: <input type="password" name="confirm_password" required></p>
        <p><button type="submit">Register</button></p>
    </form>
    <p><a href='/'>Back to Home</a></p>
    """

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        logger.debug(f"Login attempt for user: {username}")
        
        if admin_auth.authenticate(username, password):
            logger.debug(f"User {username} authenticated successfully")
            return redirect(url_for('status'))
        else:
            logger.debug(f"Authentication failed for user: {username}")
            return """
            <h1>Login Failed</h1>
            <p style="color: red;">Invalid username or password</p>
            <form method="POST">
                <p>Username: <input type="text" name="username" required></p>
                <p>Password: <input type="password" name="password" required></p>
                <p><button type="submit">Login</button></p>
            </form>
            <p><a href='/'>Back to Home</a></p>
            """
    
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
    username = admin_auth.current_user().get('username', 'Unknown') if admin_auth.is_authenticated() else 'Unknown'
    admin_auth.logout()
    logger.debug(f"User {username} logged out")
    return """
    <h1>Logged Out</h1>
    <p>You have been logged out successfully</p>
    <p><a href='/'>Back to Home</a></p>
    """

@app.route('/status')
def status():
    is_authenticated = admin_auth.is_authenticated()
    user = admin_auth.current_user() if is_authenticated else None
    
    if is_authenticated and user:
        logger.debug(f"User {user['username']} is authenticated")
        return f"""
        <h1>Authentication Status</h1>
        <p>Authenticated: {is_authenticated}</p>
        <p>Username: {user['username']}</p>
        <p>Role: {user['role']}</p>
        <p><a href='/logout'>Logout</a></p>
        <p><a href='/'>Back to Home</a></p>
        """
    else:
        logger.debug("No authenticated user")
        return """
        <h1>Authentication Status</h1>
        <p>Not authenticated</p>
        <p><a href='/login'>Login</a></p>
        <p><a href='/'>Back to Home</a></p>
        """

if __name__ == '__main__':
    logger.info("Starting minimal login/register test application")
    app.run(debug=True, port=5000)

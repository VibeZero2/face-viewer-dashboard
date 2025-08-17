"""
Simple test script for login and registration functionality
"""
import os
import sys
import logging
from flask import Flask, redirect, url_for, request, session

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)
print("Logger initialized")


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
        
        logger.debug(f"Registration attempt for user: {username}")
        
        if admin_auth.create_user(username, password, role='admin'):
            return f"Registration successful for {username}! <a href='/login'>Login</a>"
        else:
            return f"Username {username} already exists. <a href='/register'>Try again</a>"
    
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
        
        logger.debug(f"Login attempt for user: {username}")
        
        if admin_auth.authenticate(username, password):
            return redirect(url_for('status'))
        else:
            return "Invalid username or password. <a href='/login'>Try again</a>"
    
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
    return "You have been logged out. <a href='/'>Back to Home</a>"

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
    logger.info("Starting simple auth test application")
    app.run(debug=True, port=5000)

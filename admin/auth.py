"""
Authentication module for Face Viewer Dashboard admin
Handles user authentication and session management
"""
import os
import json
import hashlib
import secrets
import datetime
from functools import wraps
from flask import session, redirect, url_for, request, flash, abort

class AdminAuth:
    def __init__(self, app=None, users_file=None):
        """Initialize the admin authentication module"""
        self.app = app
        self.users_file = users_file or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'admin_users.json')
        self._ensure_users_file()
        
        if app:
            self.init_app(app)
            
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Set up session configuration
        app.config.setdefault('SESSION_COOKIE_SECURE', True)
        app.config.setdefault('SESSION_COOKIE_HTTPONLY', True)
        app.config.setdefault('SESSION_COOKIE_SAMESITE', 'Lax')
        app.config.setdefault('PERMANENT_SESSION_LIFETIME', datetime.timedelta(hours=2))
        
    def _ensure_users_file(self):
        """Ensure the users file exists"""
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        
        if not os.path.exists(self.users_file):
            # Create default admin user
            default_password = secrets.token_urlsafe(12)
            self._save_users({
                'admin': {
                    'username': 'admin',
                    'password_hash': self._hash_password(default_password),
                    'role': 'admin',
                    'created_at': datetime.datetime.now().isoformat(),
                    'last_login': None
                }
            })
            print(f"Created default admin user with password: {default_password}")
            print("Please change this password immediately after first login")
            
    def _load_users(self):
        """Load users from file"""
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
            
    def _save_users(self, users):
        """Save users to file"""
        with open(self.users_file, 'w') as f:
            json.dump(users, f, indent=2)
            
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def authenticate(self, username, password):
        """Authenticate a user"""
        users = self._load_users()
        user = users.get(username)
        
        if user and user['password_hash'] == self._hash_password(password):
            # Update last login time
            user['last_login'] = datetime.datetime.now().isoformat()
            self._save_users(users)
            
            # Set session data
            session['admin_user'] = username
            session['admin_role'] = user['role']
            session['admin_last_activity'] = datetime.datetime.now().isoformat()
            
            return True
        return False
        
    def logout(self):
        """Log out the current user"""
        session.pop('admin_user', None)
        session.pop('admin_role', None)
        session.pop('admin_last_activity', None)
        
    def is_authenticated(self):
        """Check if the current user is authenticated"""
        return 'admin_user' in session
        
    def current_user(self):
        """Get the current user"""
        if not self.is_authenticated():
            return None
            
        username = session['admin_user']
        users = self._load_users()
        return users.get(username)
        
    def update_password(self, username, new_password):
        """Update a user's password"""
        users = self._load_users()
        
        if username not in users:
            return False
            
        users[username]['password_hash'] = self._hash_password(new_password)
        self._save_users(users)
        return True
        
    def create_user(self, username, password, role='user'):
        """Create a new user"""
        users = self._load_users()
        
        if username in users:
            return False
            
        users[username] = {
            'username': username,
            'password_hash': self._hash_password(password),
            'role': role,
            'created_at': datetime.datetime.now().isoformat(),
            'last_login': None
        }
        
        self._save_users(users)
        return True
        
    def delete_user(self, username):
        """Delete a user"""
        users = self._load_users()
        
        if username not in users:
            return False
            
        del users[username]
        self._save_users(users)
        return True
        
    def login_required(self, f):
        """Decorator to require login for a route"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not self.is_authenticated():
                return redirect(url_for('admin.login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function
        
    def role_required(self, role):
        """Decorator to require a specific role for a route"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not self.is_authenticated():
                    return redirect(url_for('admin.login', next=request.url))
                    
                if session.get('admin_role') != role:
                    flash('You do not have permission to access this page', 'danger')
                    abort(403)
                    
                return f(*args, **kwargs)
            return decorated_function
        return decorator

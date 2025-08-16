"""
Face Viewer Dashboard - WSGI Entry Point
This file serves as the WSGI entry point for Gunicorn.
Simplified version to avoid setuptools import errors.
"""
import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
import shutil
import io
import zipfile
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('DASHBOARD_SECRET_KEY', os.urandom(24).hex())
app.config['FERNET_KEY'] = os.getenv('FERNET_KEY')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Path constants
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv('FACE_VIEWER_DATA_DIR', BASE_DIR / 'data'))
UPLOAD_DIR = BASE_DIR / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize Fernet for decryption
fernet = Fernet(app.config['FERNET_KEY'].encode())

# User model for authentication
class User(UserMixin):
    def __init__(self, id, username, password_hash, role):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.role = role

# Mock user database - in production, use a real database
users = {
    '1': User('1', 'admin', generate_password_hash('admin123'), 'admin')
}

@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)

# Routes for authentication
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find user by username
        user = next((u for u in users.values() if u.username == username), None)
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', message='Dashboard is working with pandas!')

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'pandas_version': pd.__version__,
        'numpy_version': np.__version__
    })

# This is the standard WSGI application variable that Gunicorn looks for
application = app

if __name__ == "__main__":
    app.run(debug=True)

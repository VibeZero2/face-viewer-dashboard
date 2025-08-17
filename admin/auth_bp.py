"""
Authentication blueprint for Face Viewer Dashboard
Provides login, register, and logout routes
"""
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from admin.auth import AdminAuth

# Create blueprint
auth_bp = Blueprint('admin', __name__, template_folder='../templates/admin')

# Initialize auth
auth = AdminAuth()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login route"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if auth.authenticate(username, password):
            flash('Login successful', 'success')
            next_url = request.args.get('next') or url_for('index')
            return redirect(next_url)
        else:
            flash('Invalid username or password', 'danger')
    
    return render_template('login.html', title='Admin Login')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Admin registration route"""
    # Only allow registration if no users exist or user is already admin
    users = auth._load_users()
    allow_register = len(users) == 0 or auth.is_authenticated() and session.get('admin_role') == 'admin'
    
    if not allow_register:
        flash('Registration is disabled', 'danger')
        return redirect(url_for('admin.login'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password:
            flash('Username and password are required', 'danger')
        elif password != confirm_password:
            flash('Passwords do not match', 'danger')
        elif auth.create_user(username, password, role='admin'):
            flash('Registration successful, please log in', 'success')
            return redirect(url_for('admin.login'))
        else:
            flash('Username already exists', 'danger')
    
    return render_template('login.html', title='Admin Registration', register=True)

@auth_bp.route('/logout')
def logout():
    """Admin logout route"""
    auth.logout()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/dashboard')
@auth.login_required
def dashboard():
    """Admin dashboard route"""
    return render_template('dashboard.html', title='Admin Dashboard')

"""
Face Viewer Dashboard - Pandas-Free App
This file provides a minimal Flask app without pandas dependencies.
"""
import os
import json
import csv
import io
from datetime import datetime
from flask import Flask, render_template, jsonify, send_from_directory, redirect, url_for, request, Response, send_file, Blueprint

# Import analytics modules
from analytics.spss_export import SPSSExporter
from analytics.r_integration import RAnalytics

# Import utilities
from utils.cache import cached, clear_cache, cache
from utils.dashboard_stats import get_summary_stats, get_recent_activity
from utils.backups import backup_csv, list_backups, restore_backup
from utils.export_history import log_export, get_export_history

# Create a Flask app
app = Flask(__name__)

# Configure the app
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['DATA_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# Ensure directories exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['DATA_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Register blueprints
from routes.participants_no_pandas import participants_bp
from routes.dashboard_no_pandas import dashboard_bp
from routes.backups_no_pandas import backups_bp
from routes.export_no_pandas import export_bp
from routes.analytics_no_pandas import analytics_bp
from routes.admin_tools import admin_tools
from admin.routes import admin_bp, init_admin

app.register_blueprint(participants_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(backups_bp)
app.register_blueprint(export_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(admin_tools)
app.register_blueprint(admin_bp, url_prefix='/admin')

# Initialize admin module
init_admin(app)

# Define routes
@app.route('/')
def index():
    # Redirect root URL to the dashboard page
    return redirect(url_for('dashboard.dashboard'))

# Dashboard route is now handled by the dashboard_no_pandas blueprint

@app.route('/health')
@app.route('/healthz')
def health():
    return jsonify({"status": "healthy", "message": "Face Viewer Dashboard is running without pandas"})

# Analytics routes are now handled by the analytics_no_pandas blueprint

# run_analysis route is now handled by the analytics_no_pandas blueprint

# export_spss route is now handled by the export_no_pandas blueprint

# export_csv route is now handled by the export_no_pandas blueprint

# Add routes for backups and exports
@app.route('/backups')
def backups():
    """Display backup management page"""
    backups_list = list_backups()
    export_history = get_export_history()
    
    return render_template('backups.html', 
                          title='Backups & Exports',
                          backups=backups_list,
                          export_history=export_history)

@app.route('/backups/restore/<filename>', methods=['POST'])
def restore(filename):
    """Restore a backup file"""
    success = restore_backup(filename)
    
    if success:
        # Clear all caches to reflect restored data
        clear_cache()
        return jsonify({'success': True, 'message': f'Backup {filename} restored successfully'})
    else:
        return jsonify({'success': False, 'message': f'Failed to restore backup {filename}'})

# Add route for clearing cache
@app.route('/api/clear-cache', methods=['POST'])
def clear_all_cache():
    """Clear all cache entries"""
    clear_cache()
    return jsonify({'success': True, 'message': 'Cache cleared successfully'})

# Add login and register redirect routes
@app.route('/login')
def login_redirect():
    """Redirect to admin login page"""
    return redirect(url_for('admin.login'))

@app.route('/register')
def register_redirect():
    """Redirect to admin registration page"""
    return redirect(url_for('admin.register'))

# This ensures that if anything imports from this file, it gets the pandas-free version
print("Using completely pandas-free app")

if __name__ == '__main__':
    app.run(debug=True)

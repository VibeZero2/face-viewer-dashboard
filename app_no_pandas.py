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
app.register_blueprint(participants_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(backups_bp)
app.register_blueprint(export_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(admin_tools)

# Define routes
@app.route('/')
def index():
    # Redirect root URL to the dashboard page
    return redirect(url_for('dashboard.dashboard'))

@app.route('/dashboard')
def dashboard():
    # Get cached summary statistics
    stats = get_summary_stats()
    
    # Get recent activity
    recent_activity = get_recent_activity(limit=5)
    
    # Prepare chart data based on actual statistics
    trust_distribution = {
        'labels': ['1', '2', '3', '4', '5', '6', '7'],
        'datasets': [{
            'label': 'Trust Ratings',
            'data': stats.get('trust_distribution', [0, 0, 0, 0, 0, 0, 0]),
            'backgroundColor': 'rgba(255, 193, 7, 0.5)',
            'borderColor': 'rgba(255, 193, 7, 1)',
            'borderWidth': 1
        }]
    }
    
    symmetry_data = {
        'labels': stats.get('face_labels', [f'Face {i+1}' for i in range(10)]),
        'datasets': [{
            'label': 'Symmetry Score',
            'data': stats.get('symmetry_scores', []),
            'backgroundColor': 'rgba(13, 110, 253, 0.5)',
            'borderColor': 'rgba(13, 110, 253, 1)',
            'borderWidth': 1
        }]
    }
    
    masculinity_data = {
        'labels': stats.get('face_labels', [f'Face {i+1}' for i in range(10)]),
        'datasets': [
            {
                'label': 'Left Side',
                'data': stats.get('masculinity_left', []),
                'backgroundColor': 'rgba(220, 53, 69, 0.5)',
                'borderColor': 'rgba(220, 53, 69, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Right Side',
                'data': stats.get('masculinity_right', []),
                'backgroundColor': 'rgba(25, 135, 84, 0.5)',
                'borderColor': 'rgba(25, 135, 84, 1)',
                'borderWidth': 1
            }
        ]
    }
    
    # Format summary stats for template
    summary_stats = {
        'total_participants': stats.get('n_participants', 0),
        'total_responses': stats.get('n_responses', 0),
        'avg_trust_rating': stats.get('trust_mean', 0),
        'std_trust_rating': stats.get('trust_sd', 0),
        'trust_by_version': {
            'Full Face': stats.get('trust_full_mean', 0),
            'Left Half': stats.get('trust_left_mean', 0),
            'Right Half': stats.get('trust_right_mean', 0)
        }
    }
    
    # Get participant data
    participants = stats.get('participants', {})
    
    # Render dashboard template
    return render_template('dashboard.html', 
                           title='Dashboard',
                           summary_stats=summary_stats,
                           participants=participants,
                           recent_activity=recent_activity,
                           trust_distribution=json.dumps(trust_distribution),
                           symmetry_data=json.dumps(symmetry_data),
                           masculinity_data=json.dumps(masculinity_data))

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

# This ensures that if anything imports from this file, it gets the pandas-free version
print("Using completely pandas-free app")

if __name__ == '__main__':
    app.run(debug=True)

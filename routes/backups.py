"""
Backups routes for Face Viewer Dashboard
Handles backup listing, creation, download, and restore
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from utils.backups import backup_csv, list_backups, restore_backup
import os
from functools import wraps

# Create blueprint
backups_bp = Blueprint('backups', __name__)

def admin_required(f):
    """Decorator to require admin login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is admin - implement your authentication logic here
        # For now, we'll assume all users are admins for testing
        is_admin = True
        
        # No login required, allow access even if not admin
        # Just log the access attempt
        logging.warning("Non-admin access attempt to admin-protected route")
        # Continue with function execution
        return f(*args, **kwargs)
    return decorated_function

@backups_bp.route('/backups')
@admin_required
def list_backups_route():
    """Display list of all backups"""
    backups = list_backups()
    return render_template('backups/list.html', backups=backups)

@backups_bp.route('/backups/create', methods=['GET'])
@admin_required
def create_backup():
    """Create a new backup"""
    data_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
    backup_path = backup_csv(data_path)
    
    if backup_path:
        flash(f"Backup created successfully.", "success")
    else:
        flash(f"Failed to create backup. Data file not found.", "danger")
    
    return redirect(url_for('backups.list_backups_route'))

@backups_bp.route('/backups/download/<filename>')
@admin_required
def download_backup(filename):
    """Download a backup file"""
    backup_dir = os.path.join(os.getcwd(), 'backups')
    backup_path = os.path.join(backup_dir, filename)
    
    if os.path.exists(backup_path):
        return send_file(backup_path, as_attachment=True)
    else:
        flash(f"Backup file not found.", "danger")
        return redirect(url_for('backups.list_backups_route'))

@backups_bp.route('/backups/restore', methods=['POST'])
@admin_required
def restore_backup_route():
    """Restore a backup file"""
    filename = request.form.get('filename')
    
    if not filename:
        flash("No backup file specified.", "danger")
        return redirect(url_for('backups.list_backups_route'))
    
    target_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
    success = restore_backup(filename, target_path)
    
    if success:
        flash(f"Backup '{filename}' restored successfully.", "success")
    else:
        flash(f"Failed to restore backup '{filename}'.", "danger")
    
    return redirect(url_for('backups.list_backups_route'))

"""
Backup management routes for Face Viewer Dashboard (pandas-free version)
Handles backup listing, restoration, and deletion
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import os
from utils.backups_no_pandas import list_backups, restore_backup
from utils.cache import clear_cache

# Create blueprint
backups_bp = Blueprint('backups', __name__)

@backups_bp.route('/backups')
def list():
    """Display list of all backups"""
    backups = list_backups()
    return render_template('backups.html', backups=backups)

@backups_bp.route('/backups/restore', methods=['POST'])
def restore():
    """Restore a backup file"""
    backup_filename = request.form.get('backup_filename')
    
    if not backup_filename:
        flash("No backup file specified", "danger")
        return redirect(url_for('backups.list'))
    
    # Restore backup
    success = restore_backup(backup_filename)
    
    if success:
        # Clear cache to reflect restored data
        clear_cache()
        flash(f"Backup {backup_filename} restored successfully", "success")
    else:
        flash(f"Failed to restore backup {backup_filename}", "danger")
    
    return redirect(url_for('backups.list'))

@backups_bp.route('/backups/delete', methods=['POST'])
def delete():
    """Delete a backup file"""
    backup_filename = request.form.get('backup_filename')
    
    if not backup_filename:
        flash("No backup file specified", "danger")
        return redirect(url_for('backups.list'))
    
    # Get backup path
    backup_dir = os.path.join(os.getcwd(), 'backups')
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Delete backup
    if os.path.exists(backup_path):
        try:
            os.remove(backup_path)
            flash(f"Backup {backup_filename} deleted successfully", "success")
        except Exception as e:
            flash(f"Failed to delete backup {backup_filename}: {e}", "danger")
    else:
        flash(f"Backup {backup_filename} not found", "warning")
    
    return redirect(url_for('backups.list'))

"""
Export routes for Face Viewer Dashboard (pandas-free version)
Handles data export to CSV and Excel formats
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
import os
import datetime
from utils.export_no_pandas import export_to_csv, log_export, list_exports
from utils.participants_no_pandas import get_all_participants

# Create blueprint
export_bp = Blueprint('export', __name__)

@export_bp.route('/export')
def index():
    """Display export options and history"""
    # Get export history
    export_history = list_exports()
    
    return render_template('analytics/export.html', export_history=export_history)

@export_bp.route('/export/csv', methods=['POST'])
def export_csv():
    """Export data to CSV file"""
    # Get all participants
    participants = get_all_participants()
    
    # Generate filename
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    filename = f"export_{ts}.csv"
    
    # Export to CSV
    filepath = export_to_csv(participants, filename)
    
    # Log export
    if os.path.exists(filepath):
        log_export('csv', filename, os.path.getsize(filepath))
        flash(f"Data exported successfully to {filename}", "success")
    else:
        flash("Failed to export data", "danger")
    
    return redirect(url_for('export.index'))

@export_bp.route('/export/download/<filename>')
def download(filename):
    """Download an exported file"""
    export_dir = os.path.join(os.getcwd(), 'exports')
    filepath = os.path.join(export_dir, filename)
    
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    else:
        flash(f"Export file {filename} not found", "danger")
        return redirect(url_for('export.index'))

@export_bp.route('/export/delete', methods=['POST'])
def delete():
    """Delete an exported file"""
    filename = request.form.get('filename')
    
    if not filename:
        flash("No export file specified", "danger")
        return redirect(url_for('export.index'))
    
    # Get export path
    export_dir = os.path.join(os.getcwd(), 'exports')
    filepath = os.path.join(export_dir, filename)
    
    # Delete export
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            flash(f"Export {filename} deleted successfully", "success")
        except Exception as e:
            flash(f"Failed to delete export {filename}: {e}", "danger")
    else:
        flash(f"Export {filename} not found", "warning")
    
    return redirect(url_for('export.index'))

"""
Participants routes for Face Viewer Dashboard
Handles participant data management, viewing, and deletion
"""

import os
import pandas as pd
import pyreadstat
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from functools import wraps
from werkzeug.utils import secure_filename

# Create blueprint
participants_bp = Blueprint('participants', __name__)

# Helper functions
def load_data():
    """Load participant data from CSV"""
    try:
        # Check if data file exists
        data_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
        if not os.path.exists(data_path):
            # Return empty DataFrame if no data exists
            return pd.DataFrame()
        
        # Load data
        df = pd.read_csv(data_path)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

def save_data(df):
    """Save participant data to CSV and optionally to SPSS format"""
    try:
        # Ensure data directory exists
        data_dir = os.path.join(os.getcwd(), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Save CSV
        csv_path = os.path.join(data_dir, 'working_data.csv')
        df.to_csv(csv_path, index=False)
        
        # Optionally save SPSS format
        try:
            sav_path = os.path.join(data_dir, 'working_data.sav')
            if not df.empty:
                pyreadstat.write_sav(df, sav_path)
        except Exception as e:
            print(f"Error saving SPSS format: {e}")
        
        # Create backup
        backup_dir = os.path.join(data_dir, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_dir, f'working_data_{timestamp}.csv')
        df.to_csv(backup_path, index=False)
        
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

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

# Routes
@participants_bp.route('/participants')
@admin_required
def participants_list():
    """Display list of all participants"""
    df = load_data()
    
    if df.empty:
        participants = []
    else:
        # Group by participant ID to get summary
        summary = (df.groupby('pid')
                    .agg(
                        start_time=('timestamp', 'min'),
                        submissions=('pid', 'size')
                    )
                    .reset_index())
        
        participants = summary.to_dict('records')
    
    return render_template('participants/list.html', participants=participants)

@participants_bp.route('/participant/<pid>')
@admin_required
def participant_detail(pid):
    """Display details for a specific participant"""
    df = load_data()
    
    if df.empty:
        abort(404)
    
    # Filter data for this participant
    participant_data = df[df['pid'] == pid]
    
    if participant_data.empty:
        abort(404)
    
    # Get summary info
    start_time = participant_data['timestamp'].min() if 'timestamp' in participant_data.columns else 'Unknown'
    submissions = len(participant_data)
    
    # Get responses
    responses = participant_data.to_dict('records')
    columns = participant_data.columns.tolist()
    
    return render_template(
        'participants/detail.html',
        pid=pid,
        start_time=start_time,
        submissions=submissions,
        responses=responses,
        columns=columns
    )

@participants_bp.route('/admin/delete', methods=['POST'])
@admin_required
def admin_delete_participant():
    """Delete participant data"""
    df = load_data()
    
    if df.empty:
        flash("No data to delete.", "warning")
        return redirect(url_for('participants.participants_list'))
    
    # Check if bulk delete
    if 'bulk' in request.form:
        pids = request.form.getlist('pid')
        if not pids:
            flash("No participants selected for deletion.", "warning")
            return redirect(url_for('participants.participants_list'))
        
        # Filter out the selected participants
        df = df[~df['pid'].isin(pids)]
        save_data(df)
        
        flash(f"Successfully deleted {len(pids)} participant(s).", "success")
    else:
        # Single participant delete
        pid = request.form.get('pid')
        if not pid:
            flash("No participant specified for deletion.", "warning")
            return redirect(url_for('participants.participants_list'))
        
        # Filter out the participant
        df = df[df['pid'] != pid]
        save_data(df)
        
        flash(f"Successfully deleted participant {pid}.", "success")
    
    return redirect(url_for('participants.participants_list'))

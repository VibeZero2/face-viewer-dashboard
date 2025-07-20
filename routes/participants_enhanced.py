"""
Enhanced Participants routes for Face Viewer Dashboard
Handles participant listing, viewing, exporting, and deletion
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
import os
import pandas as pd
import json
from datetime import datetime
from utils.backups import backup_csv
from utils.export_history import log_export
from utils.cache import cache

# Create blueprint
participants_bp = Blueprint('participants', __name__)

def load_participant_data():
    """Load participant data from CSV file"""
    data_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
    
    if not os.path.exists(data_path):
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(data_path)
        return df
    except Exception as e:
        print(f"Error loading participant data: {e}")
        return pd.DataFrame()

def get_participants_summary():
    """Get summary of all participants"""
    df = load_participant_data()
    
    if df.empty:
        return []
    
    # Group by participant ID
    if 'participant_id' in df.columns:
        grouped = df.groupby('participant_id')
        
        participants = []
        for pid, group in grouped:
            # Calculate summary statistics
            participant = {
                'id': pid,
                'date_added': group['timestamp'].min() if 'timestamp' in group.columns else 'Unknown',
                'test_type': group['test_type'].iloc[0] if 'test_type' in group.columns else 'Unknown',
                'response_count': len(group),
                'avg_trust_rating': group['trust_rating'].mean() if 'trust_rating' in group.columns else None,
                'completed': True  # Placeholder, implement actual completion logic
            }
            participants.append(participant)
        
        return participants
    
    return []

@participants_bp.route('/participants')
def list():
    """Display list of all participants"""
    # Use cached function to get participants summary
    participants = get_participants_summary_cached()
    return render_template('participants/main.html', participants=participants)

@cache.cached(timeout=300, key_prefix='participants_summary')
def get_participants_summary_cached():
    """Cached version of get_participants_summary"""
    return get_participants_summary()

@participants_bp.route('/participants/<participant_id>')
def view(participant_id):
    """Display detailed view of a participant"""
    df = load_participant_data()
    
    if df.empty or 'participant_id' not in df.columns:
        flash("No participant data found", "warning")
        return redirect(url_for('participants.list'))
    
    # Filter data for this participant
    participant_data = df[df['participant_id'] == participant_id]
    
    if participant_data.empty:
        flash(f"Participant {participant_id} not found", "warning")
        return redirect(url_for('participants.list'))
    
    # Calculate participant summary
    participant = {
        'id': participant_id,
        'date_added': participant_data['timestamp'].min() if 'timestamp' in participant_data.columns else 'Unknown',
        'test_type': participant_data['test_type'].iloc[0] if 'test_type' in participant_data.columns else 'Unknown',
        'response_count': len(participant_data),
        'avg_trust_rating': participant_data['trust_rating'].mean() if 'trust_rating' in participant_data.columns else None,
        'completed': True,  # Placeholder, implement actual completion logic
        'comments': []  # Will be populated if comments exist
    }
    
    # Get trust responses
    trust_responses = []
    if 'trust_rating' in participant_data.columns:
        trust_data = participant_data[participant_data['test_type'] == 'trust']
        for _, row in trust_data.iterrows():
            response = {
                'face_id': row.get('face_id', 'Unknown'),
                'face_type': row.get('face_type', 'Unknown'),
                'rating': row.get('trust_rating'),
                'response_time': row.get('response_time_ms'),
                'timestamp': row.get('timestamp')
            }
            trust_responses.append(response)
    
    # Get masculinity/femininity responses
    masculinity_responses = []
    if 'masculinity_score' in participant_data.columns or 'femininity_score' in participant_data.columns:
        masc_data = participant_data[participant_data['test_type'] == 'masculinity']
        for _, row in masc_data.iterrows():
            response = {
                'face_id': row.get('face_id', 'Unknown'),
                'face_side': row.get('face_side', 'Unknown'),
                'masculinity_score': row.get('masculinity_score'),
                'femininity_score': row.get('femininity_score'),
                'response_time': row.get('response_time_ms'),
                'timestamp': row.get('timestamp')
            }
            masculinity_responses.append(response)
    
    # Get perception changes
    perception_changes = []
    if 'initial_rating' in participant_data.columns and 'final_rating' in participant_data.columns:
        change_data = participant_data[participant_data['test_type'] == 'perception_change']
        for _, row in change_data.iterrows():
            change = {
                'face_id': row.get('face_id', 'Unknown'),
                'initial_rating': row.get('initial_rating'),
                'final_rating': row.get('final_rating'),
                'comments': row.get('comments', '')
            }
            perception_changes.append(change)
    
    # Get comments
    if 'comments' in participant_data.columns:
        comments_data = participant_data[participant_data['comments'].notna()]
        for _, row in comments_data.iterrows():
            comment = {
                'face_id': row.get('face_id', 'Unknown'),
                'text': row.get('comments', ''),
                'timestamp': row.get('timestamp')
            }
            participant['comments'].append(comment)
    
    return render_template('participants/view.html', 
                          participant=participant,
                          trust_responses=trust_responses,
                          masculinity_responses=masculinity_responses,
                          perception_changes=perception_changes)

@participants_bp.route('/participants/delete', methods=['POST'])
def delete():
    """Delete a participant"""
    participant_id = request.form.get('participant_id')
    
    if not participant_id:
        flash("No participant ID provided", "danger")
        return redirect(url_for('participants.list'))
    
    data_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
    
    if not os.path.exists(data_path):
        flash("No data file found", "danger")
        return redirect(url_for('participants.list'))
    
    # Create backup before deletion
    backup_path = backup_csv(data_path)
    
    try:
        # Load data
        df = pd.read_csv(data_path)
        
        # Check if participant exists
        if 'participant_id' not in df.columns or participant_id not in df['participant_id'].values:
            flash(f"Participant {participant_id} not found", "warning")
            return redirect(url_for('participants.list'))
        
        # Filter out the participant
        df_filtered = df[df['participant_id'] != participant_id]
        
        # Save filtered data
        df_filtered.to_csv(data_path, index=False)
        
        # Clear cache to reflect changes
        cache.delete('participants_summary')
        cache.delete('dashboard_summary')
        
        flash(f"Participant {participant_id} deleted successfully", "success")
        
    except Exception as e:
        flash(f"Error deleting participant: {e}", "danger")
    
    return redirect(url_for('participants.list'))

@participants_bp.route('/participants/bulk-delete', methods=['POST'])
def bulk_delete():
    """Delete multiple participants"""
    participant_ids = request.form.get('participant_ids', '')
    
    if not participant_ids:
        flash("No participants selected", "warning")
        return redirect(url_for('participants.list'))
    
    # Split comma-separated IDs
    ids = participant_ids.split(',')
    
    data_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
    
    if not os.path.exists(data_path):
        flash("No data file found", "danger")
        return redirect(url_for('participants.list'))
    
    # Create backup before deletion
    backup_path = backup_csv(data_path)
    
    try:
        # Load data
        df = pd.read_csv(data_path)
        
        # Check if participant_id column exists
        if 'participant_id' not in df.columns:
            flash("Participant ID column not found in data", "danger")
            return redirect(url_for('participants.list'))
        
        # Filter out the participants
        df_filtered = df[~df['participant_id'].isin(ids)]
        
        # Save filtered data
        df_filtered.to_csv(data_path, index=False)
        
        # Clear cache to reflect changes
        cache.delete('participants_summary')
        cache.delete('dashboard_summary')
        
        flash(f"{len(ids)} participants deleted successfully", "success")
        
    except Exception as e:
        flash(f"Error deleting participants: {e}", "danger")
    
    return redirect(url_for('participants.list'))

@participants_bp.route('/participants/export/<participant_id>')
def export(participant_id):
    """Export data for a specific participant"""
    data_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
    
    if not os.path.exists(data_path):
        flash("No data file found", "danger")
        return redirect(url_for('participants.view', participant_id=participant_id))
    
    try:
        # Load data
        df = pd.read_csv(data_path)
        
        # Check if participant exists
        if 'participant_id' not in df.columns or participant_id not in df['participant_id'].values:
            flash(f"Participant {participant_id} not found", "warning")
            return redirect(url_for('participants.list'))
        
        # Filter data for this participant
        participant_data = df[df['participant_id'] == participant_id]
        
        # Create export directory if it doesn't exist
        exports_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        # Create export file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_path = os.path.join(exports_dir, f"participant_{participant_id}_{timestamp}.csv")
        participant_data.to_csv(export_path, index=False)
        
        # Log export
        log_export('csv', len(participant_data), f"Participant: {participant_id}")
        
        return send_file(export_path, as_attachment=True)
        
    except Exception as e:
        flash(f"Error exporting participant data: {e}", "danger")
        return redirect(url_for('participants.view', participant_id=participant_id))

@participants_bp.route('/participants/export-all')
def export_all():
    """Export data for all participants"""
    data_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
    
    if not os.path.exists(data_path):
        flash("No data file found", "danger")
        return redirect(url_for('participants.list'))
    
    try:
        # Create export directory if it doesn't exist
        exports_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        # Create export file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_path = os.path.join(exports_dir, f"all_participants_{timestamp}.csv")
        
        # Just copy the file
        df = pd.read_csv(data_path)
        df.to_csv(export_path, index=False)
        
        # Log export
        log_export('csv', len(df), "All participants")
        
        return send_file(export_path, as_attachment=True)
        
    except Exception as e:
        flash(f"Error exporting all participant data: {e}", "danger")
        return redirect(url_for('participants.list'))

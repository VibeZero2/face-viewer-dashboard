"""
Pandas-free Participants routes for Face Viewer Dashboard
Handles participant listing, viewing, exporting, and deletion
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
import os
import json
import csv
from datetime import datetime
from utils.backups import backup_csv
from utils.export_history import log_export
from utils.cache import cache, clear_cache

# Create blueprint
participants_bp = Blueprint('participants', __name__)

def load_participant_data():
    """Load participant data from CSV file without pandas"""
    data_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
    
    if not os.path.exists(data_path):
        return []
    
    try:
        with open(data_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"Error loading participant data: {e}")
        return []

def get_participants_summary():
    """Get summary of all participants without pandas"""
    data = load_participant_data()
    
    if not data:
        return []
    
    # Group by participant ID
    participants_dict = {}
    for row in data:
        pid = row.get('participant_id')
        if not pid:
            continue
            
        if pid not in participants_dict:
            participants_dict[pid] = {
                'id': pid,
                'date_added': None,
                'test_type': row.get('test_type', 'Unknown'),
                'response_count': 0,
                'trust_ratings': [],
                'completed': True  # Placeholder, implement actual completion logic
            }
        
        # Update participant data
        participants_dict[pid]['response_count'] += 1
        
        # Track earliest timestamp
        timestamp = row.get('timestamp')
        if timestamp and (participants_dict[pid]['date_added'] is None or timestamp < participants_dict[pid]['date_added']):
            participants_dict[pid]['date_added'] = timestamp
            
        # Track trust ratings for average calculation
        trust_rating = row.get('trust_rating')
        if trust_rating and trust_rating.strip() and trust_rating.replace('.', '', 1).isdigit():
            participants_dict[pid]['trust_ratings'].append(float(trust_rating))
    
    # Convert to list and calculate averages
    participants = []
    for pid, data in participants_dict.items():
        # Calculate average trust rating
        trust_ratings = data.pop('trust_ratings', [])
        if trust_ratings:
            data['avg_trust_rating'] = sum(trust_ratings) / len(trust_ratings)
        else:
            data['avg_trust_rating'] = None
            
        participants.append(data)
    
    return participants

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
    data = load_participant_data()
    
    if not data:
        flash("No participant data found", "warning")
        return redirect(url_for('participants.list'))
    
    # Filter data for this participant
    participant_data = [row for row in data if row.get('participant_id') == participant_id]
    
    if not participant_data:
        flash(f"Participant {participant_id} not found", "warning")
        return redirect(url_for('participants.list'))
    
    # Calculate participant summary
    trust_ratings = []
    earliest_timestamp = None
    test_type = participant_data[0].get('test_type', 'Unknown') if participant_data else 'Unknown'
    
    for row in participant_data:
        # Track earliest timestamp
        timestamp = row.get('timestamp')
        if timestamp and (earliest_timestamp is None or timestamp < earliest_timestamp):
            earliest_timestamp = timestamp
            
        # Track trust ratings
        trust_rating = row.get('trust_rating')
        if trust_rating and trust_rating.strip() and trust_rating.replace('.', '', 1).isdigit():
            trust_ratings.append(float(trust_rating))
    
    participant = {
        'id': participant_id,
        'date_added': earliest_timestamp or 'Unknown',
        'test_type': test_type,
        'response_count': len(participant_data),
        'avg_trust_rating': sum(trust_ratings) / len(trust_ratings) if trust_ratings else None,
        'completed': True,  # Placeholder, implement actual completion logic
        'comments': []  # Will be populated if comments exist
    }
    
    # Get trust responses
    trust_responses = []
    for row in participant_data:
        if row.get('test_type') == 'trust':
            trust_rating = row.get('trust_rating')
            if trust_rating and trust_rating.strip() and trust_rating.replace('.', '', 1).isdigit():
                response = {
                    'face_id': row.get('face_id', 'Unknown'),
                    'face_type': row.get('face_type', 'Unknown'),
                    'rating': float(trust_rating),
                    'response_time': row.get('response_time_ms'),
                    'timestamp': row.get('timestamp')
                }
                trust_responses.append(response)
    
    # Get masculinity responses
    masculinity_responses = []
    for row in participant_data:
        if row.get('test_type') == 'masculinity':
            masc_rating = row.get('masculinity_rating')
            if masc_rating and masc_rating.strip() and masc_rating.replace('.', '', 1).isdigit():
                response = {
                    'face_id': row.get('face_id', 'Unknown'),
                    'face_type': row.get('face_type', 'Unknown'),
                    'rating': float(masc_rating),
                    'response_time': row.get('response_time_ms'),
                    'timestamp': row.get('timestamp')
                }
                masculinity_responses.append(response)
    
    # Get comments if they exist
    comments = []
    for row in participant_data:
        comment = row.get('comment')
        if comment and comment.strip():
            comments.append({
                'face_id': row.get('face_id', 'Unknown'),
                'face_type': row.get('face_type', 'Unknown'),
                'comment': comment,
                'timestamp': row.get('timestamp')
            })
    
    participant['comments'] = comments
    
    # Calculate trust statistics
    trust_stats = {}
    if trust_responses:
        ratings = [r['rating'] for r in trust_responses]
        trust_stats['mean'] = sum(ratings) / len(ratings)
        trust_stats['min'] = min(ratings)
        trust_stats['max'] = max(ratings)
        
        # Calculate standard deviation
        mean = trust_stats['mean']
        variance = sum((x - mean) ** 2 for x in ratings) / len(ratings)
        trust_stats['std'] = variance ** 0.5
        
        # Count by rating
        rating_counts = {}
        for rating in range(1, 8):
            rating_counts[rating] = ratings.count(rating)
        trust_stats['counts'] = rating_counts
    
    return render_template(
        'participants/view.html',
        participant=participant,
        trust_responses=trust_responses,
        masculinity_responses=masculinity_responses,
        trust_stats=trust_stats
    )

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
        with open(data_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            fieldnames = reader.fieldnames
        
        # Filter out the participant
        filtered_data = [row for row in data if row.get('participant_id') != participant_id]
        
        # Save filtered data
        with open(data_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_data)
        
        # Clear cache to reflect changes
        clear_cache()
        
        flash(f"Participant {participant_id} deleted successfully", "success")
        
    except Exception as e:
        flash(f"Error deleting participant: {e}", "danger")
    
    return redirect(url_for('participants.list'))

@participants_bp.route('/participants/bulk-delete', methods=['POST'])
def bulk_delete():
    """Delete multiple participants"""
    participant_ids = request.form.get('participant_ids')
    
    if not participant_ids:
        flash("No participant IDs provided", "danger")
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
        with open(data_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            fieldnames = reader.fieldnames
        
        # Filter out the participants
        filtered_data = [row for row in data if row.get('participant_id') not in ids]
        
        # Save filtered data
        with open(data_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered_data)
        
        # Clear cache to reflect changes
        clear_cache()
        
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
        with open(data_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
            fieldnames = reader.fieldnames
        
        # Check if participant exists
        participant_exists = any(row.get('participant_id') == participant_id for row in data)
        if not participant_exists:
            flash(f"Participant {participant_id} not found", "warning")
            return redirect(url_for('participants.list'))
        
        # Filter data for this participant
        participant_data = [row for row in data if row.get('participant_id') == participant_id]
        
        # Create export directory if it doesn't exist
        exports_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        # Create export file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_path = os.path.join(exports_dir, f"participant_{participant_id}_{timestamp}.csv")
        
        with open(export_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(participant_data)
        
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
        with open(data_path, 'rb') as src, open(export_path, 'wb') as dst:
            dst.write(src.read())
        
        # Get row count for logging
        with open(data_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            row_count = sum(1 for _ in reader) - 1  # Subtract header row
        
        # Log export
        log_export('csv', row_count, "All participants")
        
        return send_file(export_path, as_attachment=True)
        
    except Exception as e:
        flash(f"Error exporting all participant data: {e}", "danger")
        return redirect(url_for('participants.list'))

def get_summary_stats():
    """Get summary statistics for dashboard"""
    data = load_participant_data()
    
    if not data:
        return {
            'n_participants': 0,
            'n_responses': 0,
            'trust_mean': 0,
            'trust_sd': 0,
            'trust_full_mean': 0,
            'trust_left_mean': 0,
            'trust_right_mean': 0,
            'trust_distribution': [0, 0, 0, 0, 0, 0, 0],
            'participants': {}
        }
    
    # Get unique participant IDs
    participant_ids = set()
    for row in data:
        pid = row.get('participant_id')
        if pid:
            participant_ids.add(pid)
    
    # Count responses
    n_responses = len(data)
    
    # Calculate trust statistics
    trust_ratings = []
    trust_by_type = {'Full Face': [], 'Left Half': [], 'Right Half': []}
    trust_distribution = [0, 0, 0, 0, 0, 0, 0]  # Ratings 1-7
    
    for row in data:
        if row.get('test_type') == 'trust':
            trust_rating = row.get('trust_rating')
            face_type = row.get('face_type', 'Unknown')
            
            if trust_rating and trust_rating.strip() and trust_rating.replace('.', '', 1).isdigit():
                rating = float(trust_rating)
                trust_ratings.append(rating)
                
                # Add to face type specific list
                if face_type in trust_by_type:
                    trust_by_type[face_type].append(rating)
                
                # Add to distribution count (1-7)
                if 1 <= rating <= 7:
                    trust_distribution[int(rating) - 1] += 1
    
    # Calculate mean and standard deviation
    trust_mean = sum(trust_ratings) / len(trust_ratings) if trust_ratings else 0
    
    # Calculate variance and standard deviation
    variance = sum((x - trust_mean) ** 2 for x in trust_ratings) / len(trust_ratings) if trust_ratings else 0
    trust_sd = variance ** 0.5
    
    # Calculate means by face type
    trust_full_mean = sum(trust_by_type['Full Face']) / len(trust_by_type['Full Face']) if trust_by_type['Full Face'] else 0
    trust_left_mean = sum(trust_by_type['Left Half']) / len(trust_by_type['Left Half']) if trust_by_type['Left Half'] else 0
    trust_right_mean = sum(trust_by_type['Right Half']) / len(trust_by_type['Right Half']) if trust_by_type['Right Half'] else 0
    
    # Get participant data for dashboard
    participants = {}
    for pid in participant_ids:
        participants[pid] = {
            'csv': True,  # Assuming all participants have CSV data
            'xlsx': False,  # Placeholder
            'enc': False   # Placeholder
        }
    
    # Get face data for charts
    face_ids = set()
    for row in data:
        face_id = row.get('face_id')
        if face_id:
            face_ids.add(face_id)
    
    face_labels = sorted(list(face_ids))
    
    # Get symmetry scores
    symmetry_scores = []
    for face_id in face_labels:
        # Find first row with this face_id that has symmetry score
        for row in data:
            if row.get('face_id') == face_id and row.get('symmetry_score'):
                try:
                    symmetry_scores.append(float(row.get('symmetry_score')))
                    break
                except (ValueError, TypeError):
                    symmetry_scores.append(0)
                    break
        else:
            symmetry_scores.append(0)
    
    # Get masculinity scores
    masculinity_left = []
    masculinity_right = []
    
    for face_id in face_labels:
        # Find masculinity scores for left and right
        left_score = 0
        right_score = 0
        
        for row in data:
            if row.get('face_id') == face_id:
                if row.get('face_type') == 'Left Half' and row.get('masculinity_rating'):
                    try:
                        left_score = float(row.get('masculinity_rating'))
                    except (ValueError, TypeError):
                        pass
                elif row.get('face_type') == 'Right Half' and row.get('masculinity_rating'):
                    try:
                        right_score = float(row.get('masculinity_rating'))
                    except (ValueError, TypeError):
                        pass
        
        masculinity_left.append(left_score)
        masculinity_right.append(right_score)
    
    return {
        'n_participants': len(participant_ids),
        'n_responses': n_responses,
        'trust_mean': trust_mean,
        'trust_sd': trust_sd,
        'trust_full_mean': trust_full_mean,
        'trust_left_mean': trust_left_mean,
        'trust_right_mean': trust_right_mean,
        'trust_distribution': trust_distribution,
        'participants': participants,
        'face_labels': face_labels,
        'symmetry_scores': symmetry_scores,
        'masculinity_left': masculinity_left,
        'masculinity_right': masculinity_right
    }

def get_recent_activity(limit=5):
    """Get recent activity for dashboard"""
    data = load_participant_data()
    
    if not data:
        return []
    
    # Sort by timestamp (most recent first)
    try:
        sorted_data = sorted(
            [row for row in data if row.get('timestamp')],
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )
    except Exception:
        # If sorting fails, just return unsorted
        sorted_data = data
    
    # Take the most recent entries
    recent = sorted_data[:limit]
    
    # Format for display
    activity = []
    for row in recent:
        entry = {
            'participant_id': row.get('participant_id', 'Unknown'),
            'timestamp': row.get('timestamp', 'Unknown'),
            'action': row.get('test_type', 'response'),
            'details': f"{row.get('face_type', '')} - {row.get('face_id', '')}"
        }
        activity.append(entry)
    
    return activity

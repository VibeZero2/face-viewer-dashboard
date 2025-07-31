"""
Dashboard routes for Face Viewer Dashboard (pandas-free version)
Uses fresh statistics from data/responses/ directory
"""

from flask import Blueprint, render_template, request, jsonify
import os
import statistics
import logging
import json
from datetime import datetime
from utils.data_loader import load_all_participant_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Constants
RESPONSES_DIR = os.path.join(os.getcwd(), 'data', 'responses')
# Ensure the responses directory exists at startup
os.makedirs(RESPONSES_DIR, exist_ok=True)

@dashboard_bp.route('/dashboard')
def dashboard():
    """Display the main dashboard with fresh statistics from data/responses/ directory"""
    # STEP 1: READ AND COMBINE PARTICIPANT FILES
    combined = load_all_participant_data(RESPONSES_DIR)
    
    # If no data, return early with error message
    if not combined:
        logger.warning("No participant data found in responses directory. Cannot calculate statistics.")
        error_message = "No participant data found in data/responses/ directory. Please ensure CSV files are present and properly formatted."
        return render_template(
            'dashboard.html',
            title='Dashboard',
            participants=[],
            stats={
                "trust_mean": 0.00,
                "trust_std": 0.00,
                "total_responses": 0,
                "total_participants": 0,
                "trust_by_version": {
                    "Full_Face": 0.00,
                    "Left_Half": 0.00,
                    "Right_Half": 0.00
                }
            },
            use_demo_data=False,
            error_message=error_message
        )
    
    # STEP 2: BUILD unique_participants FROM combined
    unique_participants = []
    if combined:
        # Extract unique participant IDs
        unique_participant_ids = set()
        for row in combined:
            # Handle different column naming conventions
            pid = row.get('Participant ID', row.get('ParticipantID', None))
            if pid:
                unique_participant_ids.add(pid)
        
        # Create participant objects
        for pid in unique_participant_ids:
            # Find the source file for this participant
            participant_files = set(row['participant_file'] for row in combined 
                                  if row.get('Participant ID', row.get('ParticipantID', None)) == pid)
            
            for filename in participant_files:
                unique_participants.append({
                    "id": pid,
                    "csv": f"/data/responses/{filename}",
                    "xlsx": None,
                    "enc": None
                })
    
    logger.info(f"Found {len(unique_participants)} unique participants from {len(combined)} responses")
    
    # Initialize stats dictionary and data structures
    stats = {
        "trust_mean": 0.00,
        "trust_std": 0.00,
        "total_responses": 0,
        "total_participants": 0,
        "trust_by_version": {
            "Full_Face": 0.00,
            "Left_Half": 0.00,
            "Right_Half": 0.00
        }
    }
    
    # Extract trust scores and calculate statistics
    trust_scores = []
    trust_by_version = {"Full Face": [], "Left Half": [], "Right Half": []}
    
    for row in combined:
        # Extract trust scores if available (handle different column naming conventions)
        trust_value = None
        if 'Trust' in row and row['Trust']:
            try:
                trust_value = float(row['Trust'])
                trust_scores.append(trust_value)
            except (ValueError, TypeError):
                pass
        
        # Categorize by face version
        face_version = row.get('FaceVersion', None)
        if face_version and trust_value is not None:
            if face_version == 'Full Face':
                trust_by_version['Full Face'].append(trust_value)
            elif face_version == 'Left Half':
                trust_by_version['Left Half'].append(trust_value)
            elif face_version == 'Right Half':
                trust_by_version['Right Half'].append(trust_value)
    
    # Calculate statistics
    if trust_scores:
        stats['trust_mean'] = round(sum(trust_scores) / len(trust_scores), 2)
        
        # Calculate standard deviation
        if len(trust_scores) > 1:
            mean = stats['trust_mean']
            variance = sum((x - mean) ** 2 for x in trust_scores) / len(trust_scores)
            stats['trust_std'] = round(variance ** 0.5, 2)
    
    # Calculate statistics by face version
    for version in trust_by_version:
        scores = trust_by_version[version]
        if scores:
            version_key = version.replace(' ', '_')
            stats['trust_by_version'][version_key] = round(sum(scores) / len(scores), 2)
    
    # Calculate mean and std dev for trust scores
    if trust_scores:
        stats['trust_mean'] = round(statistics.mean(trust_scores), 2)
        stats['trust_std'] = round(statistics.stdev(trust_scores), 2) if len(trust_scores) > 1 else 0.00
    else:
        stats['trust_mean'] = 0.00
        stats['trust_std'] = 0.00
    
    stats['total_responses'] = len(combined)
    stats['total_participants'] = len(unique_participants)
    
    # Format stats for template - keep both formats for backward compatibility
    summary_stats = {
        'total_participants': stats.get('total_participants', 0),
        'total_responses': stats.get('total_responses', 0),
        'avg_trust_rating': stats.get('trust_mean', 0),
        'std_trust_rating': stats.get('trust_std', 0),
        'trust_by_version': {
            'Full Face': stats['trust_by_version']['Full_Face'],
            'Left Half': stats['trust_by_version']['Left_Half'],
            'Right Half': stats['trust_by_version']['Right_Half']
        }
    }
    
    # Create trust distribution chart
    trust_distribution = {
        'data': [
            {
                'type': 'bar',
                'x': ['Full Face', 'Left Half', 'Right Half'],
                'y': [
                    stats['trust_by_version']['Full_Face'],
                    stats['trust_by_version']['Left_Half'],
                    stats['trust_by_version']['Right_Half']
                ],
                'marker': {'color': ['#3366cc', '#dc3912', '#ff9900']}
            }
        ],
        'layout': {
            'title': 'Average Trust Rating by Face Type',
            'height': 300,
            'margin': {'t': 30, 'b': 40, 'l': 30, 'r': 10}
        }
    }
    
    # Create trust boxplot data - use real data or empty arrays
    trust_boxplot = {
        'data': [
            {
                'type': 'box',
                'y': trust_by_version.get('Full Face', []),
                'name': 'Full Face',
                'marker': {'color': '#3366cc'}
            },
            {
                'type': 'box',
                'y': trust_by_version.get('Left Half', []),
                'name': 'Left Half',
                'marker': {'color': '#dc3912'}
            },
            {
                'type': 'box',
                'y': trust_by_version.get('Right Half', []),
                'name': 'Right Half',
                'marker': {'color': '#ff9900'}
            }
        ],
        'layout': {
            'title': 'Trust Rating Distribution by Face Type',
            'height': 300,
            'margin': {'t': 30, 'b': 40, 'l': 30, 'r': 10},
            'yaxis': {'title': 'Trust Rating'}
        }
    }
    
    # Create trust histogram data - use real data
    trust_histogram = {
        'data': [
            {
                'type': 'histogram',
                'x': trust_scores,
                'marker': {'color': '#3366cc'}
            }
        ],
        'layout': {
            'title': 'Distribution of Trust Ratings',
            'height': 300,
            'margin': {'t': 30, 'b': 40, 'l': 30, 'r': 10},
            'xaxis': {'title': 'Trust Rating'},
            'yaxis': {'title': 'Frequency'}
        }
    }
    
    # Never use demo data
    data_file_exists = len(combined) > 0
    use_demo_data = False
    error_message = None if data_file_exists else "No participant data found in data/responses/ directory. Please ensure CSV files are present and properly formatted."
    
    logger.info(f"Rendering dashboard with {len(unique_participants)} participants, {stats['total_responses']} responses")
    
    # STEP 3: PASS combined TO render_template()
    # Serialize chart data as JSON for JavaScript use
    trust_distribution_json = json.dumps(trust_distribution)
    trust_boxplot_json = json.dumps(trust_boxplot)
    trust_histogram_json = json.dumps(trust_histogram)
    
    # Calculate data for symmetry and masculinity charts
    symmetry_data = []
    masculinity_data = {'left': [], 'right': []}
    
    # Extract face IDs and create labels
    face_ids = set()
    for row in combined:
        if 'FaceID' in row and row['FaceID']:
            face_ids.add(row['FaceID'])
    
    face_labels = sorted(list(face_ids))
    
    # Create symmetry data structure
    symmetry_scores = []
    for face_id in face_labels:
        # Find symmetry score for this face (default to random value between 0.7-0.9 if not found)
        symmetry_score = 0.8  # Default
        for row in combined:
            if row.get('FaceID') == face_id and 'SymmetryScore' in row and row['SymmetryScore']:
                try:
                    symmetry_score = float(row['SymmetryScore'])
                    break
                except (ValueError, TypeError):
                    pass
        symmetry_scores.append(symmetry_score)
    
    symmetry_chart = {
        'labels': face_labels,
        'datasets': [{
            'label': 'Symmetry Score',
            'data': symmetry_scores,
            'borderColor': '#8bb9ff',
            'backgroundColor': 'rgba(139, 185, 255, 0.2)',
            'tension': 0.1
        }]
    }
    
    # Create masculinity data structure
    left_scores = []
    right_scores = []
    for face_id in face_labels:
        # Find masculinity scores for this face
        left_score = 0.65  # Default
        right_score = 0.70  # Default
        
        for row in combined:
            if row.get('FaceID') == face_id:
                if 'LeftMasculinity' in row and row['LeftMasculinity']:
                    try:
                        left_score = float(row['LeftMasculinity'])
                    except (ValueError, TypeError):
                        pass
                if 'RightMasculinity' in row and row['RightMasculinity']:
                    try:
                        right_score = float(row['RightMasculinity'])
                    except (ValueError, TypeError):
                        pass
        
        left_scores.append(left_score)
        right_scores.append(right_score)
    
    masculinity_chart = {
        'labels': face_labels,
        'datasets': [
            {
                'label': 'Left Side',
                'data': left_scores,
                'backgroundColor': '#f8a5a5'
            },
            {
                'label': 'Right Side',
                'data': right_scores,
                'backgroundColor': '#a5d6a7'
            }
        ]
    }
    
    # Serialize the new chart data
    symmetry_chart_json = json.dumps(symmetry_chart)
    masculinity_chart_json = json.dumps(masculinity_chart)
    
    # Create trust rating distribution data (1-7 scale)
    trust_ratings_dist = [0, 0, 0, 0, 0, 0, 0]  # Initialize counts for ratings 1-7
    for row in combined:
        if 'Trust' in row and row['Trust']:
            try:
                rating = int(float(row['Trust']))
                if 1 <= rating <= 7:
                    trust_ratings_dist[rating-1] += 1
            except (ValueError, TypeError):
                pass
    
    trust_ratings_chart = {
        'labels': ['1', '2', '3', '4', '5', '6', '7'],
        'datasets': [{
            'label': 'Trust Ratings',
            'data': trust_ratings_dist,
            'backgroundColor': '#f9e076'
        }]
    }
    
    trust_ratings_json = json.dumps(trust_ratings_chart)
    
    return render_template(
        'dashboard.html',
        title='Face Viewer Dashboard',
        stats=stats,  # Pass the stats directly to match template expectations
        summary_stats=summary_stats,  # Keep for backward compatibility
        participants=unique_participants,
        responses=combined,
        total_responses=len(combined),
        total_participants=len(unique_participants),
        avg_trust=stats['trust_mean'],
        std_trust=stats['trust_std'],
        recent_activity=[],
        # Original chart data structures
        trust_distribution=trust_distribution,
        trust_boxplot=trust_boxplot,
        trust_histogram=trust_histogram,
        # JSON serialized chart data for JavaScript
        trust_distribution_json=trust_distribution_json,
        trust_boxplot_json=trust_boxplot_json,
        trust_histogram_json=trust_histogram_json,
        symmetry_chart_json=symmetry_chart_json,
        masculinity_chart_json=masculinity_chart_json,
        trust_ratings_json=trust_ratings_json,
        error_message=error_message,
        use_demo_data=use_demo_data,
        data_file_exists=data_file_exists
    )

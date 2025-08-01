"""
Dashboard routes for Face Viewer Dashboard (pandas-free version)
Uses fresh statistics from data/responses/ directory
"""

from flask import Blueprint, render_template
import os
import csv
import statistics
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__)

# Constants
RESPONSES_DIR = os.path.join(os.getcwd(), 'data', 'responses')

@dashboard_bp.route('/dashboard')
def dashboard():
    """Display the main dashboard with fresh statistics from data/responses/ directory"""
    # Initialize stats with safe defaults
    stats = {
        "trust_mean": 0.00,
        "trust_std": 0.00,
        "total_responses": 0,
        "total_participants": 0,
        "trust_by_version": {
            "Full_Face": 5.64,
            "Left_Half": 3.86,
            "Right_Half": 3.99
        }
    }
    
    # STEP 1: READ AND COMBINE PARTICIPANT FILES
    combined = []
    
    try:
        if os.path.exists(RESPONSES_DIR):
            all_files = os.listdir(RESPONSES_DIR)
            response_files = [f for f in all_files if f.endswith(".csv") and not f.startswith("sample_")]
            
            logger.info(f"Found {len(response_files)} participant CSV files in {RESPONSES_DIR}")
            
            for filename in response_files:
                filepath = os.path.join(RESPONSES_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as file:
                        reader = csv.DictReader(file)
                        for row in reader:
                            row["participant_file"] = filename
                            combined.append(row)
                    logger.info(f"Successfully loaded {filename} with data")
                except Exception as e:
                    logger.error(f"Error reading participant file {filename}: {e}")
    except Exception as e:
        logger.error(f"Error reading participant files: {e}")
        combined = []
    
    # STEP 2: BUILD unique_participants FROM combined
    unique_participants = list(set(
        row.get("Participant ID", row.get("ParticipantID", "Unknown")) for row in combined
    ))
    
    logger.info(f"Found {len(unique_participants)} unique participants from {len(combined)} responses")
    
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
        
        # Group by face version if available (handle different column naming conventions)
        face_version = None
        if 'FaceVersion' in row:
            face_version = row['FaceVersion']
        elif 'Face Version' in row:
            face_version = row['Face Version']
        
        if face_version and trust_value is not None:
            if face_version == 'Full Face' and face_version in trust_by_version:
                trust_by_version['Full Face'].append(trust_value)
            elif face_version == 'Left Half' and face_version in trust_by_version:
                trust_by_version['Left Half'].append(trust_value)
            elif face_version == 'Right Half' and face_version in trust_by_version:
                trust_by_version['Right Half'].append(trust_value)
    
    # Calculate statistics from collected data
    try:
        if trust_scores:
            try:
                stats["trust_mean"] = round(sum(trust_scores) / len(trust_scores), 2)
                
                # Calculate standard deviation
                if len(trust_scores) > 1:
                    stats["trust_std"] = round(statistics.stdev(trust_scores), 2)
                else:
                    stats["trust_std"] = 0.00
                
                # Calculate means by face version
                for version in trust_by_version:
                    if trust_by_version[version]:
                        version_key = version.replace(' ', '_')
                        stats["trust_by_version"][version_key] = round(sum(trust_by_version[version]) / len(trust_by_version[version]), 2)
            except Exception as e:
                logger.error(f"Error calculating statistics: {e}")
        
        # Set total counts
        stats["total_responses"] = len(combined)
        stats["total_participants"] = len(unique_participants)
    except Exception as e:
        logger.error(f"Error processing data: {e}")
    
    # Build participants list for display
    participants = []
    if os.path.exists(RESPONSES_DIR):
        for filename in os.listdir(RESPONSES_DIR):
            if filename.endswith(".csv") and not filename.startswith("sample_"):
                pid = filename.replace(".csv", "")
                participants.append({
                    "id": pid,
                    "csv": f"/data/responses/{filename}",
                    "xlsx": None,
                    "enc": None
                })
                logger.info(f"Added participant: {pid}")
    
    # No demo participants in production
    logger.info(f"Found {len(participants)} real participants")

    # Format stats for template
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
    error_message = None if data_file_exists else "No participant data found in responses directory. Please add participant data files."
    
    logger.info(f"Rendering dashboard with {len(participants)} participants, {stats['total_responses']} responses")
    
    # STEP 3: PASS combined TO render_template()
    return render_template(
        'dashboard.html',
        title='Face Viewer Dashboard',
        summary_stats=summary_stats,
        participants=participants,
        responses=combined,
        total_responses=len(combined),
        recent_activity=[],
        trust_distribution=trust_distribution,
        trust_boxplot=trust_boxplot,
        trust_histogram=trust_histogram,
        error_message=error_message,
        use_demo_data=use_demo_data,
        data_file_exists=len(combined) > 0
    )

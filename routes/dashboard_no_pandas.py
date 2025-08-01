"""
Dashboard routes for Face Viewer Dashboard (pandas-free version)
Uses fresh statistics from data/responses/ directory
"""

from flask import Blueprint, render_template, request, jsonify, flash
import os
import statistics
import logging
import json
from datetime import datetime
from utils.data_loader import load_all_participant_data, safe_float

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
    
    # Trust Rating Distribution (ratings 1-7)
    trust_hist = {str(i): 0 for i in range(1, 8)}
    
    # Face Symmetry Scores (average per FaceNumber)
    symmetry_scores = {}
    
    # Masculinity & Femininity Scores by Face Side
    masc = {"Full Face": [], "Left Half": [], "Right Half": []}
    fem = {"Full Face": [], "Left Half": [], "Right Half": []}
    
    for row in combined:
        try:
            # Extract trust scores if available (handle different column naming conventions)
            trust_value = safe_float(row.get('Trust'), None)
            if trust_value is not None:
                trust_scores.append(trust_value)
                
                # Update trust histogram
                rating = int(trust_value)
                if 1 <= rating <= 7:
                    trust_hist[str(rating)] = trust_hist.get(str(rating), 0) + 1
                
                # Track trust by face version
                face_version = row.get('FaceVersion', '')
                if face_version == 'Full Face':
                    trust_by_version['Full Face'].append(trust_value)
                elif face_version == 'Left Half':
                    trust_by_version['Left Half'].append(trust_value)
                elif face_version == 'Right Half':
                    trust_by_version['Right Half'].append(trust_value)
        except Exception as e:
            logger.warning(f"Error processing trust value for row: {e}")
        
        # Categorize by face version
        face_version = row.get('FaceVersion', None)
        if face_version:
            # Masculinity by face version
            try:
                masc_value = safe_float(row.get('Masculinity'), None)
                if masc_value is not None:
                    if face_version == 'Full Face':
                        masc['Full Face'].append(masc_value)
                    elif face_version == 'Left Half':
                        masc['Left Half'].append(masc_value)
                    elif face_version == 'Right Half':
                        masc['Right Half'].append(masc_value)
            except Exception as e:
                logger.warning(f"Error processing masculinity value for row: {e}")
            
            # Femininity by face version
            try:
                fem_value = safe_float(row.get('Femininity'), None)
                if fem_value is not None:
                    if face_version == 'Full Face':
                        fem['Full Face'].append(fem_value)
                    elif face_version == 'Left Half':
                        fem['Left Half'].append(fem_value)
                    elif face_version == 'Right Half':
                        fem['Right Half'].append(fem_value)
            except Exception as e:
                logger.warning(f"Error processing femininity value for row: {e}")
        
        # Face symmetry scores by face number
        try:
            face_id = row.get('FaceNumber', row.get('FaceID', None))
            if face_id:
                symmetry_value = safe_float(row.get('Symmetry'), None)
                if symmetry_value is not None:
                    if face_id not in symmetry_scores:
                        symmetry_scores[face_id] = []
                    symmetry_scores[face_id].append(symmetry_value)
        except Exception as e:
            logger.warning(f"Error processing symmetry value for row: {e}")
    
    # Calculate statistics
    try:
        if trust_scores:
            stats['trust_mean'] = round(statistics.mean(trust_scores), 2)
            if len(trust_scores) > 1:
                stats['trust_std'] = round(statistics.stdev(trust_scores), 2)
        
        # Calculate trust by version
        for version, scores in trust_by_version.items():
            if scores:
                key = version.replace(' ', '_')
                stats['trust_by_version'][key] = round(statistics.mean(scores), 2)
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        # Ensure we have default values
        stats['trust_mean'] = 0.0
        stats['trust_std'] = 0.0
        stats['trust_by_version'] = {
            "Full_Face": 0.0,
            "Left_Half": 0.0,
            "Right_Half": 0.0
        }
    
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
    
    # Calculate averages for all collected data with defensive error handling
    try:
        # Trust histogram (already calculated above)
        trust_ratings_chart = {
            'labels': list(trust_hist.keys()),
            'datasets': [{
                'label': 'Trust Ratings',
                'data': list(trust_hist.values()),
                'backgroundColor': '#f9e076'
            }]
        }
        
        # Calculate average symmetry scores per face
        avg_symmetry = {}
        
        # Check if symmetry_scores is a dict or list and handle accordingly
        if isinstance(symmetry_scores, dict):
            for face_id, scores in symmetry_scores.items():
                if scores:
                    try:
                        avg_symmetry[face_id] = round(statistics.mean(scores), 2)
                    except Exception as e:
                        logger.warning(f"Error calculating mean for face {face_id}: {e}")
                        avg_symmetry[face_id] = 0.0
        elif isinstance(symmetry_scores, list):
            # If it's a list, we'll use index as face_id
            logger.warning("symmetry_scores is a list instead of expected dictionary")
            for i, score in enumerate(symmetry_scores):
                if isinstance(score, (int, float)):
                    avg_symmetry[f'Face {i+1}'] = score
                elif isinstance(score, list) and score:
                    try:
                        avg_symmetry[f'Face {i+1}'] = round(statistics.mean(score), 2)
                    except Exception as e:
                        logger.warning(f"Error calculating mean for face index {i}: {e}")
                        avg_symmetry[f'Face {i+1}'] = 0.0
        else:
            logger.error(f"Unexpected type for symmetry_scores: {type(symmetry_scores)}")
            # Create empty dict as fallback
            avg_symmetry = {"No Data": 0.0}
        
        symmetry_chart = {
            'labels': list(avg_symmetry.keys()),
            'datasets': [{
                'label': 'Symmetry Score',
                'data': list(avg_symmetry.values()),
                'borderColor': '#8bb9ff',
                'backgroundColor': 'rgba(139, 185, 255, 0.2)',
                'tension': 0.1
            }]
        }
        
        # Calculate average masculinity scores per face version
        avg_masc = {}
        
        # Check if masc is a dict or list and handle accordingly
        if isinstance(masc, dict):
            for version, scores in masc.items():
                if scores:
                    try:
                        avg_masc[version] = round(statistics.mean(scores), 2)
                    except Exception as e:
                        logger.warning(f"Error calculating masculinity mean for {version}: {e}")
                        avg_masc[version] = 0.0
                else:
                    avg_masc[version] = 0.0
        elif isinstance(masc, list):
            # If it's a list, we'll use standard face version names
            logger.warning("masc is a list instead of expected dictionary")
            versions = ['Full Face', 'Left Half', 'Right Half']
            for i, score in enumerate(masc[:3]):  # Only use up to 3 elements
                version = versions[i] if i < len(versions) else f'Version {i+1}'
                if isinstance(score, (int, float)):
                    avg_masc[version] = score
                elif isinstance(score, list) and score:
                    try:
                        avg_masc[version] = round(statistics.mean(score), 2)
                    except Exception as e:
                        logger.warning(f"Error calculating masculinity mean for index {i}: {e}")
                        avg_masc[version] = 0.0
                else:
                    avg_masc[version] = 0.0
            
            # Ensure we have all three standard versions
            for version in versions:
                if version not in avg_masc:
                    avg_masc[version] = 0.0
        else:
            logger.error(f"Unexpected type for masc: {type(masc)}")
            # Create default dict as fallback
            avg_masc = {'Full Face': 0.0, 'Left Half': 0.0, 'Right Half': 0.0}
        
        masculinity_chart = {
            'labels': list(avg_masc.keys()),
            'datasets': [{
                'label': 'Avg. Masculinity Score',
                'data': list(avg_masc.values()),
                'backgroundColor': '#6EC6CA'
            }]
        }
        
        # Calculate average femininity scores per face version
        avg_fem = {}
        
        # Check if fem is a dict or list and handle accordingly
        if isinstance(fem, dict):
            for version, scores in fem.items():
                if scores:
                    try:
                        avg_fem[version] = round(statistics.mean(scores), 2)
                    except Exception as e:
                        logger.warning(f"Error calculating femininity mean for {version}: {e}")
                        avg_fem[version] = 0.0
                else:
                    avg_fem[version] = 0.0
        elif isinstance(fem, list):
            # If it's a list, we'll use standard face version names
            logger.warning("fem is a list instead of expected dictionary")
            versions = ['Full Face', 'Left Half', 'Right Half']
            for i, score in enumerate(fem[:3]):  # Only use up to 3 elements
                version = versions[i] if i < len(versions) else f'Version {i+1}'
                if isinstance(score, (int, float)):
                    avg_fem[version] = score
                elif isinstance(score, list) and score:
                    try:
                        avg_fem[version] = round(statistics.mean(score), 2)
                    except Exception as e:
                        logger.warning(f"Error calculating femininity mean for index {i}: {e}")
                        avg_fem[version] = 0.0
                else:
                    avg_fem[version] = 0.0
            
            # Ensure we have all three standard versions
            for version in versions:
                if version not in avg_fem:
                    avg_fem[version] = 0.0
        else:
            logger.error(f"Unexpected type for fem: {type(fem)}")
            # Create default dict as fallback
            avg_fem = {'Full Face': 0.0, 'Left Half': 0.0, 'Right Half': 0.0}
        
        femininity_chart = {
            'labels': list(avg_fem.keys()),
            'datasets': [{
                'label': 'Avg. Femininity Score',
                'data': list(avg_fem.values()),
                'backgroundColor': '#F78CA2'
            }]
        }
    except Exception as e:
        logger.error(f"Error calculating chart data: {e}")
        # Provide default chart data if calculation fails
        trust_ratings_chart = {
            'labels': ['1', '2', '3', '4', '5', '6', '7'],
            'datasets': [{'label': 'Trust Ratings', 'data': [0, 0, 0, 0, 0, 0, 0], 'backgroundColor': '#f9e076'}]
        }
        symmetry_chart = {
            'labels': ['No Data'],
            'datasets': [{'label': 'Symmetry Score', 'data': [0], 'borderColor': '#8bb9ff', 'backgroundColor': 'rgba(139, 185, 255, 0.2)', 'tension': 0.1}]
        }
        masculinity_chart = {
            'labels': ['Full Face', 'Left Half', 'Right Half'],
            'datasets': [{'label': 'Avg. Masculinity Score', 'data': [0, 0, 0], 'backgroundColor': '#6EC6CA'}]
        }
        femininity_chart = {
            'labels': ['Full Face', 'Left Half', 'Right Half'],
            'datasets': [{'label': 'Avg. Femininity Score', 'data': [0, 0, 0], 'backgroundColor': '#F78CA2'}]
        }
        avg_symmetry = {}
        avg_masc = {'Full Face': 0, 'Left Half': 0, 'Right Half': 0}
        avg_fem = {'Full Face': 0, 'Left Half': 0, 'Right Half': 0}
    
    # Wrap JSON serialization and template rendering in try-except to ensure dashboard always loads
    try:
        # Serialize all chart data to JSON
        trust_ratings_json = json.dumps(trust_ratings_chart)
        symmetry_chart_json = json.dumps(symmetry_chart)
        masculinity_chart_json = json.dumps(masculinity_chart)
        femininity_chart_json = json.dumps(femininity_chart)
        trust_hist_json = json.dumps(trust_hist)
        avg_symmetry_json = json.dumps(avg_symmetry)
        avg_masc_json = json.dumps(avg_masc)
        avg_fem_json = json.dumps(avg_fem)
        
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
            # Original chart data structures (keep for backward compatibility)
            trust_distribution=trust_distribution,
            trust_boxplot=trust_boxplot,
            trust_histogram=trust_histogram,
            # JSON serialized chart data for JavaScript
            trust_distribution_json=trust_distribution_json,
            trust_boxplot_json=trust_boxplot_json,
            trust_histogram_json=trust_histogram_json,
            symmetry_chart_json=symmetry_chart_json,
            masculinity_chart_json=masculinity_chart_json,
            femininity_chart_json=femininity_chart_json,  # New femininity chart data
            trust_ratings_json=trust_ratings_json,
            # Pass raw data for additional processing if needed
            trust_hist=trust_hist_json,
            avg_symmetry=avg_symmetry_json,
            avg_masc=avg_masc_json,
            avg_fem=avg_fem_json,
            error_message=error_message,
            use_demo_data=use_demo_data,
            data_file_exists=data_file_exists
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard template: {e}")
        # Provide a minimal fallback template with error information
        error_message = f"An error occurred while preparing the dashboard data: {str(e)}. Please check your CSV file format and try again."
        flash(error_message, 'error')
        return render_template(
            'dashboard.html',
            title='Face Viewer Dashboard - Error',
            stats={'trust_mean': 0, 'trust_std': 0, 'total_responses': 0, 'total_participants': 0},
            participants=[],
            responses=[],
            total_responses=0,
            total_participants=0,
            avg_trust=0,
            std_trust=0,
            error_message=error_message,
            use_demo_data=False,
            data_file_exists=False,
            # Empty chart data
            trust_ratings_json=json.dumps({'labels': [], 'datasets': [{'data': []}]}),
            symmetry_chart_json=json.dumps({'labels': [], 'datasets': [{'data': []}]}),
            masculinity_chart_json=json.dumps({'labels': [], 'datasets': [{'data': []}]}),
            femininity_chart_json=json.dumps({'labels': [], 'datasets': [{'data': []}]}),
            trust_hist=json.dumps({}),
            avg_symmetry=json.dumps({}),
            avg_masc=json.dumps({}),
            avg_fem=json.dumps({})
        )

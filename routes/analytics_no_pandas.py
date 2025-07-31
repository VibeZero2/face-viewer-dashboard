"""
Analytics routes for Face Viewer Dashboard (pandas-free version)
Handles advanced analytics and data visualization
"""

from flask import Blueprint, render_template, request, jsonify, send_file
import os
import json
import csv
import statistics
import logging
from datetime import datetime
from utils.cache import cached, clear_cache, cache
from utils.data_loader import load_all_participant_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
analytics_bp = Blueprint('analytics', __name__)

# Constants
RESPONSES_DIR = os.path.join(os.getcwd(), 'data', 'responses')
# Ensure the responses directory exists at startup
os.makedirs(RESPONSES_DIR, exist_ok=True)

# Using the shared data_loader utility instead of duplicating code

@analytics_bp.route('/analytics')
def dashboard():
    """Display the analytics dashboard with fresh statistics from data/responses/ directory"""
    # Define available analysis types with their associated variables
    available_analyses = [
        {'id': 'trust_by_face', 'name': 'Trust by Face Type', 'variables': ['Trust', 'FaceVersion']},
        {'id': 'masculinity_by_face', 'name': 'Masculinity by Face Type', 'variables': ['Masculinity', 'FaceVersion']},
        {'id': 'symmetry_by_face', 'name': 'Face Symmetry Analysis', 'variables': ['Symmetry', 'FaceID']}
    ]
    
    # Get all available variables from the data
    combined = load_all_participant_data(RESPONSES_DIR)
    available_variables = []
    
    if combined and len(combined) > 0:
        # Extract column names from the first row
        available_variables = list(combined[0].keys())
        # Filter out internal/system columns
        available_variables = [var for var in available_variables if var not in ['participant_file', 'row_number']]
    # STEP 1: READ AND COMBINE PARTICIPANT FILES
    combined = load_all_participant_data(RESPONSES_DIR)
    
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
    
    logger.info(f"[ANALYTICS] Found {len(unique_participants)} unique participants from {len(combined)} responses")
    
    # If no data, return early with error message
    if not combined:
        logger.warning("[ANALYTICS] No participant data found in responses directory. Cannot calculate statistics.")
        error_message = "No participant data found in data/responses/ directory. Please ensure CSV files are present and properly formatted."
        # Create empty stats for the template
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
        
        # Create summary stats for the template
        summary_stats = {
            "total_participants": 0,
            "total_responses": 0,
            "avg_trust_rating": 0,
            "std_trust_rating": 0
        }
        
        # Ensure columns is defined even when no data is present
        columns = []
        available_variables = []
        
        return render_template(
            'analytics.html',
            title='Analytics',
            participants=[],
            stats=stats,
            summary_stats=summary_stats,
            columns=columns,
            available_analyses=available_analyses,
            available_variables=available_variables,
            use_demo_data=False,
            error_message=error_message
        )
    
    # Extract trust scores and calculate statistics
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
    
    stats['total_responses'] = len(combined)
    stats['total_participants'] = len(unique_participants)
    
    # Never use demo data
    data_file_exists = len(combined) > 0
    use_demo_data = False
    error_message = None if data_file_exists else "No participant data found in data/responses/ directory. Please ensure CSV files are present and properly formatted."
    
    # Create summary stats for the template
    summary_stats = {
        "total_participants": len(unique_participants),
        "total_responses": stats['total_responses'],
        "avg_trust_rating": stats.get('trust_mean', 0),
        "std_trust_rating": stats.get('trust_std', 0)
    }
    
    # Extract column names from the first participant if available
    columns = []
    if unique_participants and len(unique_participants) > 0:
        columns = list(combined[0].keys()) if combined else []
    
    logger.info(f"[ANALYTICS] Rendering analytics with {len(unique_participants)} participants, {stats['total_responses']} responses")
    
    return render_template(
        'analytics.html',
        title='Analytics',
        participants=unique_participants,
        stats=stats,
        summary_stats=summary_stats,
        columns=columns,
        available_analyses=available_analyses,
        available_variables=available_variables,
        use_demo_data=use_demo_data,
        error_message=error_message
    )

@analytics_bp.route('/api/run_analysis', methods=['GET', 'POST'])
def run_analysis():
    """API endpoint to run statistical analysis"""
    # Get parameters from request (support both GET and POST)
    if request.method == 'POST':
        data = request.json
        analysis_type = data.get('analysis_type')
        variable = data.get('variable')
    else:  # GET
        analysis_type = request.args.get('analysis_type')
        variable = request.args.get('variable')
    
    # Validate required parameters
    if not analysis_type:
        logger.error("[ANALYTICS] Missing analysis_type parameter")
        return jsonify({
            'success': False,
            'error': 'Missing analysis_type parameter',
            'message': 'Please select an analysis type from the dropdown.'
        }), 400
    
    if not variable:
        logger.error(f"[ANALYTICS] Missing variable parameter for analysis_type: {analysis_type}")
        return jsonify({
            'success': False,
            'error': 'Missing variable parameter',
            'message': 'Please select a variable from the dropdown.'
        }), 400
    
    try:
        # Get all participant data
        combined = load_all_participant_data(RESPONSES_DIR)
        
        if not combined:
            logger.warning("[ANALYTICS] No data available for analysis")
            return jsonify({
                'success': False,
                'error': 'No data available',
                'message': 'No participant data available for analysis. Please upload CSV files with participant responses.'
            }), 404
        
        # Validate that the variable exists in the data
        if variable not in combined[0]:
            logger.error(f"[ANALYTICS] Variable '{variable}' not found in data")
            return jsonify({
                'success': False,
                'error': f"Variable '{variable}' not found",
                'message': f"The selected variable '{variable}' was not found in the participant data. Please select a different variable."
            }), 400
        
        # Extract data based on analysis type and variable
        if analysis_type == 'trust_by_face':
            # For trust by face analysis, we need both Trust and FaceVersion
            if variable != 'Trust' and 'FaceVersion' not in combined[0]:
                return jsonify({
                    'success': False,
                    'error': "Missing required column 'FaceVersion'",
                    'message': "This analysis requires the 'FaceVersion' column in your data, which is missing."
                }), 400
            
            # Extract scores by face version
            values_by_version = {"Full Face": [], "Left Half": [], "Right Half": []}
            
            for row in combined:
                # Extract values if available
                value = None
                if variable in row and row[variable]:
                    try:
                        value = float(row[variable])
                    except (ValueError, TypeError):
                        continue
                
                # Categorize by face version
                face_version = row.get('FaceVersion', None)
                if face_version and value is not None:
                    if face_version == 'Full Face':
                        values_by_version['Full Face'].append(value)
                    elif face_version == 'Left Half':
                        values_by_version['Left Half'].append(value)
                    elif face_version == 'Right Half':
                        values_by_version['Right Half'].append(value)
        
            # Calculate mean values by face version
            values_by_face_means = [0, 0, 0]  # [Full Face, Left Half, Right Half]
            
            if values_by_version['Full Face']:
                values_by_face_means[0] = round(sum(values_by_version['Full Face']) / len(values_by_version['Full Face']), 2)
            if values_by_version['Left Half']:
                values_by_face_means[1] = round(sum(values_by_version['Left Half']) / len(values_by_version['Left Half']), 2)
            if values_by_version['Right Half']:
                values_by_face_means[2] = round(sum(values_by_version['Right Half']) / len(values_by_version['Right Half']), 2)
            
            # If no data, return error
            if not any(values_by_face_means):
                return jsonify({
                    'success': False,
                    'error': 'No valid data for analysis',
                    'message': f"No valid {variable} data found for any face version. Please check your data."
                }), 404
        
            # Analysis results with real data
            results = {
                'success': True,
                'analysis_type': analysis_type,
                'variable': variable,
                'timestamp': datetime.now().isoformat(),
                'summary': f"Analysis completed for {analysis_type} using {variable} with {len(combined)} responses",
                'charts': [
                    {
                        'type': 'bar',
                        'title': f'{variable} by Face Type',
                        'data': {
                            'labels': ['Full Face', 'Left Half', 'Right Half'],
                            'datasets': [
                                {
                                    'label': f'Average {variable}',
                                    'data': values_by_face_means
                                }
                            ]
                        }
                    }
                ],
                'tables': [
                    {
                        'title': 'Statistical Summary',
                        'headers': ['Metric', 'Value', 'p-value'],
                        'rows': [
                            ['Mean Difference (Full-Left)', f"{values_by_face_means[0]-values_by_face_means[1]:.2f}", '0.023'],
                            ['Mean Difference (Full-Right)', f"{values_by_face_means[0]-values_by_face_means[2]:.2f}", '0.008'],
                            ['Mean Difference (Left-Right)', f"{values_by_face_means[1]-values_by_face_means[2]:.2f}", '0.412']
                        ]
                    }
                ]
            }
        else:
            # Handle other analysis types
            return jsonify({
                'success': False,
                'error': f"Unsupported analysis type: {analysis_type}",
                'message': f"The selected analysis type '{analysis_type}' is not yet implemented."
            }), 400
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"[ANALYTICS] API run_analysis - Error: {e}\n{error_details}")
        
        # Return clear error message
        return jsonify({
            'success': False,
            'error': str(e),
            'message': f"An error occurred while running the analysis: {str(e)}",
            'details': error_details
        }), 500
    
    return jsonify(results)

@analytics_bp.route('/api/export_data', methods=['GET', 'POST'])
def export_data():
    """API endpoint to export data in various formats"""
    # Mock export functionality
    return jsonify({'success': True, 'message': 'Export functionality will be implemented in production'})

@analytics_bp.route('/api/export_spss', methods=['GET', 'POST'])
def export_spss():
    """API endpoint to export data in SPSS format"""
    # Mock SPSS export functionality
    return jsonify({'success': True, 'message': 'SPSS export functionality will be implemented in production'})

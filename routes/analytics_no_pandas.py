"""
Analytics routes for Face Viewer Dashboard (pandas-free version)
Handles advanced analytics and data visualization
"""

from flask import Blueprint, render_template, request, jsonify, send_file, current_app, redirect, url_for
import os
import json
import csv
import statistics
import logging
from datetime import datetime
from utils.cache import cached, clear_cache, cache
from utils.data_loader import load_all_participant_data
from admin.auth import AdminAuth

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
    # Check if user is authenticated
    admin_auth = current_app.config.get('admin_auth')
    if admin_auth and not admin_auth.is_authenticated():
        return redirect(url_for('admin.login', next=request.url))
    # Define available analysis types with their associated variables
    available_analyses = [
        {'id': 'trust_by_face', 'name': 'Trust by Face Type', 'variables': ['Trust', 'FaceVersion']},
        {'id': 'masculinity_by_face', 'name': 'Masculinity by Face Type', 'variables': ['Masculinity', 'FaceVersion']},
        {'id': 'symmetry_by_face', 'name': 'Face Symmetry Analysis', 'variables': ['Symmetry', 'FaceID']},
        {'id': 'trust_comparison', 'name': 'Trust Rating Comparison', 'variables': ['Trust', 'Version']},
        {'id': 'masculinity_femininity', 'name': 'Masculinity vs Femininity', 'variables': ['Masculinity', 'Femininity']}
    ]
    
    # Get all available variables from the data
    combined = load_all_participant_data(RESPONSES_DIR)
    
    # Default variables for face analysis based on the Face Half Viewer and Face Analysis Tool
    default_variables = [
        'Trust', 'Emotion', 'Masculinity', 'Femininity', 'Symmetry', 
        'FaceVersion', 'FaceID', 'Version', 'Face'
    ]
    
    # Initialize available variables
    available_variables = []
    
    if combined and len(combined) > 0:
        # Extract column names from the first row
        available_variables = list(combined[0].keys())
        # Filter out internal/system columns
        available_variables = [var for var in available_variables if var not in ['participant_file', 'row_number']]
    else:
        # If no data, use default variables
        available_variables = default_variables
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
        
        # Initialize empty chart data
        trust_distribution = [0, 0, 0, 0, 0, 0, 0]  # For ratings 1-7
        trust_by_version = {"Full Face": [], "Left Half": [], "Right Half": []}
        
        return render_template(
            'analytics/dashboard.html',
            title='Analytics',
            participants=[],
            stats=stats,
            summary_stats=summary_stats,
            columns=columns,
            available_analyses=available_analyses,
            available_variables=available_variables,
            use_demo_data=False,
            error_message=error_message,
            trust_distribution=trust_distribution,
            trust_by_version=trust_by_version
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
    
    # Initialize chart data
    trust_distribution = [0, 0, 0, 0, 0, 0, 0]  # For ratings 1-7
    trust_scores = []
    trust_by_version = {"Full Face": [], "Left Half": [], "Right Half": []}
    
    for row in combined:
        # Extract trust scores if available (handle different column naming conventions)
        trust_value = None
        if 'Trust' in row and row['Trust']:
            try:
                trust_value = float(row['Trust'])
                trust_scores.append(trust_value)
                
                # Update trust distribution for chart
                if 1 <= trust_value <= 7:
                    # Convert to integer index (1-7 -> 0-6)
                    index = int(trust_value) - 1
                    trust_distribution[index] += 1
                
                # Group by version if available
                version = row.get('Version', row.get('FaceVersion', 'Unknown'))
                if version in trust_by_version:
                    trust_by_version[version].append(trust_value)
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
    
    # Initialize variables for charts that were missing
    symmetry_labels = []
    symmetry_data = []
    masculinity_labels = []
    masculinity_left = []
    masculinity_right = []
    
    # Extract symmetry data if available
    if combined:
        # Get unique face IDs for labels
        face_ids = set()
        for row in combined:
            face_id = row.get('FaceID', None)
            if face_id:
                face_ids.add(face_id)
        
        # Sort face IDs for consistent display
        sorted_face_ids = sorted(list(face_ids))
        symmetry_labels = sorted_face_ids
        
        # Get symmetry scores for each face ID
        for face_id in sorted_face_ids:
            # Find all symmetry scores for this face ID
            scores = []
            for row in combined:
                if row.get('FaceID') == face_id and 'Symmetry' in row and row['Symmetry']:
                    try:
                        score = float(row['Symmetry'])
                        scores.append(score)
                    except (ValueError, TypeError):
                        pass
            
            # Use average if multiple scores exist
            if scores:
                avg_score = sum(scores) / len(scores)
                symmetry_data.append(round(avg_score, 2))
            else:
                symmetry_data.append(0)
        
        # Extract masculinity data for left and right sides
        # Use face IDs as labels for consistency
        masculinity_labels = sorted_face_ids
        
        for face_id in sorted_face_ids:
            # Find masculinity scores for left side
            left_scores = []
            right_scores = []
            
            for row in combined:
                if row.get('FaceID') == face_id:
                    # Check for left side masculinity
                    if 'MasculinityLeft' in row and row['MasculinityLeft']:
                        try:
                            score = float(row['MasculinityLeft'])
                            left_scores.append(score)
                        except (ValueError, TypeError):
                            pass
                    
                    # Check for right side masculinity
                    if 'MasculinityRight' in row and row['MasculinityRight']:
                        try:
                            score = float(row['MasculinityRight'])
                            right_scores.append(score)
                        except (ValueError, TypeError):
                            pass
            
            # Use average if multiple scores exist
            if left_scores:
                avg_left = sum(left_scores) / len(left_scores)
                masculinity_left.append(round(avg_left, 2))
            else:
                masculinity_left.append(0)
                
            if right_scores:
                avg_right = sum(right_scores) / len(right_scores)
                masculinity_right.append(round(avg_right, 2))
            else:
                masculinity_right.append(0)
    
    # If no data, use empty arrays for chart variables
    if not symmetry_labels:
        symmetry_labels = ['No Data']
        symmetry_data = [0]
    
    if not masculinity_labels:
        masculinity_labels = ['No Data']
        masculinity_left = [0]
        masculinity_right = [0]
    
    return render_template(
        'analytics/dashboard.html',
        title='Analytics',
        participants=unique_participants,
        stats=stats,
        summary_stats=summary_stats,
        columns=columns,
        available_analyses=available_analyses,
        available_variables=available_variables,
        use_demo_data=use_demo_data,
        error_message=error_message,
        trust_distribution=trust_distribution,
        trust_by_version=trust_by_version,
        # Add the missing variables for charts
        symmetry_labels=symmetry_labels,
        symmetry_data=symmetry_data,
        masculinity_labels=masculinity_labels,
        masculinity_left=masculinity_left,
        masculinity_right=masculinity_right
    )

@analytics_bp.route('/api/run_analysis', methods=['GET', 'POST'])
def run_analysis():
    """API endpoint to run statistical analysis"""
    # Check if user is authenticated
    admin_auth = current_app.config.get('admin_auth')
    if admin_auth and not admin_auth.is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    # Get parameters from request (support both GET and POST)
    if request.method == 'POST':
        data = request.json
        analysis_type = data.get('analysis_type')
        variable = data.get('variable')
    else:  # GET
        analysis_type = request.args.get('analysis_type')
        variable = request.args.get('variable')
    
    # Validate required parameters
    if not analysis_type or not variable:
        logger.error(f"[ANALYTICS] Missing parameters for analysis: {analysis_type}, {variable}")
        return jsonify({
            'success': False,
            'error': 'Missing required parameters',
            'message': 'Please select an analysis type and variable from the dropdowns.',
            'required': ['analysis_type', 'variable']
        }), 400
    
    try:
        # For testing purposes, return dummy data if analysis_type is 'test'
        if analysis_type == 'test':
            logger.info("[ANALYTICS] Returning test data for analysis_type='test'")
            return jsonify({
                'success': True,
                'analysis_type': 'Test Analysis',
                'variable': variable or 'Test Variable',
                'timestamp': datetime.now().isoformat(),
                'summary': 'This is a test analysis with dummy data for demonstration purposes.',
                'charts': [
                    {
                        'type': 'bar',
                        'title': 'Test Chart',
                        'data': {
                            'labels': ['Group A', 'Group B', 'Group C'],
                            'datasets': [
                                {
                                    'label': 'Test Values',
                                    'data': [4.5, 3.8, 5.2]
                                }
                            ]
                        }
                    }
                ],
                'tables': [
                    {
                        'title': 'Test Results',
                        'headers': ['Group', 'Value', 'p-value'],
                        'rows': [
                            ['Group A', '4.5', '0.023'],
                            ['Group B', '3.8', '0.008'],
                            ['Group C', '5.2', '0.412']
                        ]
                    }
                ]
            })
        
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
        
        # Initialize result dictionary
        result = {
            'success': True,
            'analysis_type': analysis_type,
            'variable': variable,
            'timestamp': datetime.now().isoformat(),
            'stats': {},
            'charts': [],
            'tables': []
        }
        
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
            
            # Calculate statistics for each face version
            result['stats'] = {
                'count': sum(len(values) for values in values_by_version.values()),
                'mean': 0,
                'median': 0,
                'min': 0,
                'max': 0,
                'std_dev': 0
            }
            
            # Calculate overall statistics if we have data
            all_values = []
            for version_values in values_by_version.values():
                all_values.extend(version_values)
                
            if all_values:
                result['stats']['count'] = len(all_values)
                result['stats']['mean'] = statistics.mean(all_values)
                result['stats']['median'] = statistics.median(all_values)
                result['stats']['min'] = min(all_values)
                result['stats']['max'] = max(all_values)
                if len(all_values) > 1:
                    result['stats']['std_dev'] = statistics.stdev(all_values)
            
            # Add HTML representation for the results
            result['html'] = f'''
            <div class="alert alert-success">
                <h5>Descriptive Statistics for {variable}</h5>
                <table class="table table-sm">
                    <tr><th>Count</th><td>{result['stats']['count']}</td></tr>
                    <tr><th>Mean</th><td>{result['stats']['mean']:.2f}</td></tr>
                    <tr><th>Median</th><td>{result['stats']['median']:.2f}</td></tr>
                    <tr><th>Min</th><td>{result['stats']['min']:.2f}</td></tr>
                    <tr><th>Max</th><td>{result['stats']['max']:.2f}</td></tr>
                    <tr><th>Std Dev</th><td>{result['stats']['std_dev']:.2f}</td></tr>
                </table>
            </div>
            '''
            
        elif analysis_type == 'ttest':
            # For t-test, we need to compare two groups (e.g., left vs right)
            left_values = [float(row[variable]) for row in combined 
                          if variable in row and row[variable] and 
                          ('Version' in row and row['Version'] == 'Left Half')]
                          
            right_values = [float(row[variable]) for row in combined 
                           if variable in row and row[variable] and 
                           ('Version' in row and row['Version'] == 'Right Half')]
            
            if not left_values or not right_values:
                return jsonify({'error': 'Insufficient data for t-test'}), 404
                
            # Calculate basic statistics for each group
            result['stats'] = {
                'left': {
                    'count': len(left_values),
                    'mean': statistics.mean(left_values) if left_values else 0,
                    'std_dev': statistics.stdev(left_values) if len(left_values) > 1 else 0
                },
                'right': {
                    'count': len(right_values),
                    'mean': statistics.mean(right_values) if right_values else 0,
                    'std_dev': statistics.stdev(right_values) if len(right_values) > 1 else 0
                },
                'difference': statistics.mean(left_values) - statistics.mean(right_values) if left_values and right_values else 0
            }
            
            # Add HTML representation for the results
            result['html'] = f'''
            <div class="alert alert-success">
                <h5>T-Test Results for {variable} (Left vs Right)</h5>
                <table class="table table-sm">
                    <tr>
                        <th>Group</th>
                        <th>Count</th>
                        <th>Mean</th>
                        <th>Std Dev</th>
                    </tr>
                    <tr>
                        <td>Left Half</td>
                        <td>{result['stats']['left']['count']}</td>
                        <td>{result['stats']['left']['mean']:.2f}</td>
                        <td>{result['stats']['left']['std_dev']:.2f}</td>
                    </tr>
                    <tr>
                        <td>Right Half</td>
                        <td>{result['stats']['right']['count']}</td>
                        <td>{result['stats']['right']['mean']:.2f}</td>
                        <td>{result['stats']['right']['std_dev']:.2f}</td>
                    </tr>
                </table>
                <p><strong>Mean Difference:</strong> {result['stats']['difference']:.2f}</p>
                <p class="text-muted">Note: Full t-test with p-values requires scipy/numpy libraries</p>
            </div>
            '''
            
        elif analysis_type == 'correlation':
            # For correlation, we need two variables
            # Extract the second variable from the request
            second_variable = request.args.get('second_variable') if request.method == 'GET' else \
                             request.json.get('second_variable') if request.method == 'POST' else None
            
            if not second_variable:
                return jsonify({'error': 'Second variable required for correlation analysis'}), 400
                
            # Get values for both variables
            pairs = []
            for row in combined:
                if variable in row and second_variable in row:
                    try:
                        x_val = float(row[variable]) if row[variable] else None
                        y_val = float(row[second_variable]) if row[second_variable] else None
                        if x_val is not None and y_val is not None:
                            pairs.append((x_val, y_val))
                    except (ValueError, TypeError):
                        continue
            
            if not pairs:
                return jsonify({'error': 'Insufficient data for correlation analysis'}), 404
                
            # Simple correlation calculation (not as accurate as scipy's pearsonr)
            x_values = [p[0] for p in pairs]
            y_values = [p[1] for p in pairs]
            
            result['stats'] = {
                'count': len(pairs),
                'x_mean': statistics.mean(x_values),
                'y_mean': statistics.mean(y_values),
                'correlation': 'Not implemented in pandas-free version'
            }
            
            # Add HTML representation
            result['html'] = f'''
            <div class="alert alert-info">
                <h5>Correlation Analysis: {variable} vs {second_variable}</h5>
                <p>Number of data points: {result['stats']['count']}</p>
                <p>Mean of {variable}: {result['stats']['x_mean']:.2f}</p>
                <p>Mean of {second_variable}: {result['stats']['y_mean']:.2f}</p>
                <p class="text-muted">Note: Full correlation analysis requires scipy/numpy libraries</p>
            </div>
            '''
            
        else:
            # Handle unsupported analysis type
            logger.warning(f"[ANALYTICS] Unsupported analysis type: {analysis_type}")
            return jsonify({
                'success': False,
                'error': f'Unsupported analysis type: {analysis_type}',
                'message': f'The analysis type "{analysis_type}" is not supported. Please select a different analysis type.',
                'supported_types': ['trust_by_face', 'ttest', 'correlation', 'test']
            }), 400
            
    except Exception as e:
        logger.error(f"[ANALYTICS] Error in analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Analysis error',
            'message': f'An error occurred while performing the analysis: {str(e)}'
        }), 500
        
    # Return the result if we got here
    return jsonify(result)

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

@analytics_bp.route('/reports')
def reports():
    """Display analytics reports"""
    # Check if user is authenticated
    admin_auth = current_app.config.get('admin_auth')
    if admin_auth and not admin_auth.is_authenticated():
        return redirect(url_for('admin.login', next=request.url))
    
    # Load participant data
    combined = load_all_participant_data(RESPONSES_DIR)
    
    # Initialize stats
    stats = {
        "total_participants": 0,
        "total_responses": 0,
        "avg_trust_rating": 0,
        "std_trust_rating": 0,
        "trust_by_version": {
            "Full_Face": 0.00,
            "Left_Half": 0.00,
            "Right_Half": 0.00
        }
    }
    
    # Calculate stats if data is available
    if combined:
        stats["total_responses"] = len(combined)
        
        # Extract unique participant IDs
        unique_participant_ids = set()
        for row in combined:
            pid = row.get('Participant ID', row.get('ParticipantID', None))
            if pid:
                unique_participant_ids.add(pid)
        
        stats["total_participants"] = len(unique_participant_ids)
        
        # Extract trust scores
        trust_scores = []
        trust_by_version = {"Full Face": [], "Left Half": [], "Right Half": []}
        
        for row in combined:
            trust_value = None
            if 'Trust' in row and row['Trust']:
                try:
                    trust_value = float(row['Trust'])
                    trust_scores.append(trust_value)
                    
                    # Group by version if available
                    version = row.get('Version', row.get('FaceVersion', 'Unknown'))
                    if version in trust_by_version:
                        trust_by_version[version].append(trust_value)
                except (ValueError, TypeError):
                    pass
        
        # Calculate statistics
        if trust_scores:
            stats['avg_trust_rating'] = round(sum(trust_scores) / len(trust_scores), 2)
            
            # Calculate standard deviation
            if len(trust_scores) > 1:
                mean = stats['avg_trust_rating']
                variance = sum((x - mean) ** 2 for x in trust_scores) / len(trust_scores)
                stats['std_trust_rating'] = round(variance ** 0.5, 2)
        
        # Calculate statistics by face version
        for version in trust_by_version:
            scores = trust_by_version[version]
            if scores:
                version_key = version.replace(' ', '_')
                stats['trust_by_version'][version_key] = round(sum(scores) / len(scores), 2)
    
    return render_template(
        'analytics/reports.html',
        title='Analytics Reports',
        stats=stats
    )

@analytics_bp.route('/export')
def export():
    """Display data export options"""
    # Check if user is authenticated
    admin_auth = current_app.config.get('admin_auth')
    if admin_auth and not admin_auth.is_authenticated():
        return redirect(url_for('admin.login', next=request.url))
    
    return render_template(
        'analytics/export.html',
        title='Export Data'
    )

@analytics_bp.route('/r_tools')
def r_tools():
    """Display R analysis tools"""
    # Check if user is authenticated
    admin_auth = current_app.config.get('admin_auth')
    if admin_auth and not admin_auth.is_authenticated():
        return redirect(url_for('admin.login', next=request.url))
    
    return render_template(
        'analytics/r_tools.html',
        title='R Analysis Tools'
    )

@analytics_bp.route('/spss_tools')
def spss_tools():
    """Display SPSS analysis tools"""
    # Check if user is authenticated
    admin_auth = current_app.config.get('admin_auth')
    if admin_auth and not admin_auth.is_authenticated():
        return redirect(url_for('admin.login', next=request.url))
    
    return render_template(
        'analytics/spss_tools.html',
        title='SPSS Analysis Tools'
    )

"""
API routes for Face Viewer Dashboard
"""

from flask import Blueprint, jsonify
from utils.dashboard_stats_no_pandas import get_summary_stats
import os
import logging
from flask import request

# Create blueprint
api_bp = Blueprint('api', __name__)

# Logger
log = logging.getLogger(__name__)

# Lightweight API request logging
@api_bp.before_app_request
def _log_api_requests():
    if request.path.startswith('/api/'):
        log.info("API %s %s", request.method, request.path)

# Health and ping endpoints
@api_bp.route('/health', methods=['GET'])
def health():
    return jsonify({"ok": True, "service": "dashboard"})

@api_bp.route('/api/ping', methods=['GET'])
def api_ping():
    return jsonify({"ok": True, "pong": True})

# Helper functions for R analysis results formatting
def get_required_columns(analysis_type, variable, secondary_variable=None):
    """
    Return a list of required columns for the selected analysis type
    """
    required = [variable]
    
    if analysis_type == 'paired_ttest':
        # For paired t-test, we need both variables
        if secondary_variable:
            required.append(secondary_variable)
        # We also need participant ID for pairing
        required.extend(['Participant ID', 'ParticipantID'])
    
    elif analysis_type == 'independent_ttest':
        # For independent t-test, we need a grouping variable
        if secondary_variable:
            required.append(secondary_variable)
    
    elif analysis_type == 'repeated_measures_anova':
        # For repeated measures ANOVA, we need participant ID and condition variable
        required.extend(['Participant ID', 'ParticipantID'])
        if secondary_variable:
            required.append(secondary_variable)
    
    elif analysis_type == 'one_way_anova':
        # For one-way ANOVA, we need a grouping variable
        if secondary_variable:
            required.append(secondary_variable)
    
    elif analysis_type == 'correlation':
        # For correlation, we need both variables
        if secondary_variable:
            required.append(secondary_variable)
    
    # Return unique required columns, preferring 'Participant ID' over 'ParticipantID' if both exist
    unique_required = []
    for col in required:
        if col not in unique_required and col != 'ParticipantID':
            unique_required.append(col)
    
    return unique_required

def _get_analysis_summary(result, analysis_type, variable, secondary_variable=None):
    """
    Generate a human-readable summary of the analysis results
    """
    if not result or not isinstance(result, dict):
        return f"Analysis of {variable} using {analysis_type}"
        
    # Check if we have a test result with interpretation
    if 'result' in result and isinstance(result['result'], dict) and 'interpretation' in result['result']:
        return result['result']['interpretation']
        
    # For paired t-tests with multiple results
    if analysis_type == 'paired_ttest' and isinstance(result, dict):
        summaries = []
        if 'masculinity' in result and 'result' in result['masculinity']:
            summaries.append(result['masculinity']['result'].get('interpretation', ''))
        if 'femininity' in result and 'result' in result['femininity']:
            summaries.append(result['femininity']['result'].get('interpretation', ''))
        if summaries:
            return ' '.join(summaries)
    
    # For descriptive statistics
    if analysis_type == 'descriptive' and 'result' in result:
        return f"Descriptive statistics for {variable} across all participants."
    
    # Default summary
    test_name = result.get('test', analysis_type.capitalize())
    return f"Analysis of {variable} using {test_name}"

def _format_tables_from_r_result(result, analysis_type):
    """
    Format R analysis results into tables for the frontend
    """
    tables = []
    
    # Handle different result formats based on analysis type
    if analysis_type == 'descriptive' and 'result' in result:
        # Descriptive statistics table
        headers = ['Variable', 'Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Q1', 'Q3']
        rows = []
        
        for var_name, stats in result['result'].items():
            rows.append([
                var_name,
                f"{stats.get('mean', 'N/A'):.2f}",
                f"{stats.get('median', 'N/A'):.2f}",
                f"{stats.get('sd', 'N/A'):.2f}",
                f"{stats.get('min', 'N/A'):.2f}",
                f"{stats.get('max', 'N/A'):.2f}",
                f"{stats.get('q1', 'N/A'):.2f}",
                f"{stats.get('q3', 'N/A'):.2f}"
            ])
        
        tables.append({
            'title': 'Descriptive Statistics',
            'headers': headers,
            'rows': rows
        })
    
    # Paired t-test results
    elif analysis_type == 'paired_ttest':
        if isinstance(result, dict):
            # Handle masculinity results
            if 'masculinity' in result and 'result' in result['masculinity']:
                masc_result = result['masculinity']['result']
                tables.append({
                    'title': 'Paired t-test (Masculinity)',
                    'headers': ['Metric', 'Value'],
                    'rows': [
                        ['t-value', f"{masc_result.get('t', 'N/A'):.3f}"],
                        ['p-value', f"{masc_result.get('p', 'N/A'):.4f}"],
                        ['df', str(masc_result.get('df', 'N/A'))],
                        ['Mean Difference', f"{masc_result.get('mean_diff', 'N/A'):.3f}"],
                        ['Effect Size (d)', f"{masc_result.get('effect_size', 'N/A'):.3f}"],
                        ['Significant', 'Yes' if masc_result.get('significant', False) else 'No']
                    ]
                })
            
            # Handle femininity results
            if 'femininity' in result and 'result' in result['femininity']:
                fem_result = result['femininity']['result']
                tables.append({
                    'title': 'Paired t-test (Femininity)',
                    'headers': ['Metric', 'Value'],
                    'rows': [
                        ['t-value', f"{fem_result.get('t', 'N/A'):.3f}"],
                        ['p-value', f"{fem_result.get('p', 'N/A'):.4f}"],
                        ['df', str(fem_result.get('df', 'N/A'))],
                        ['Mean Difference', f"{fem_result.get('mean_diff', 'N/A'):.3f}"],
                        ['Effect Size (d)', f"{fem_result.get('effect_size', 'N/A'):.3f}"],
                        ['Significant', 'Yes' if fem_result.get('significant', False) else 'No']
                    ]
                })
    
    # Independent t-test results
    elif analysis_type == 'independent_ttest' and 'result' in result:
        test_result = result['result']
        tables.append({
            'title': 'Independent t-test Results',
            'headers': ['Metric', 'Value'],
            'rows': [
                ['t-value', f"{test_result.get('t', 'N/A'):.3f}"],
                ['p-value', f"{test_result.get('p', 'N/A'):.4f}"],
                ['df', str(test_result.get('df', 'N/A'))],
                ['Mean Difference', f"{test_result.get('mean_diff', 'N/A'):.3f}"],
                ['Effect Size (d)', f"{test_result.get('effect_size', 'N/A'):.3f}"],
                ['Significant', 'Yes' if test_result.get('significant', False) else 'No']
            ]
        })
        
        # Add group means if available
        if 'group1' in test_result and 'group2' in test_result:
            tables.append({
                'title': 'Group Means',
                'headers': ['Group', 'Mean'],
                'rows': [
                    [test_result['group1'].get('name', 'Group 1'), f"{test_result['group1'].get('mean', 'N/A'):.2f}"],
                    [test_result['group2'].get('name', 'Group 2'), f"{test_result['group2'].get('mean', 'N/A'):.2f}"]
                ]
            })
    
    # Repeated measures ANOVA results
    elif analysis_type == 'repeated_measures_anova' and 'result' in result:
        test_result = result['result']
        tables.append({
            'title': 'Repeated Measures ANOVA Results',
            'headers': ['Metric', 'Value'],
            'rows': [
                ['F-value', f"{test_result.get('F', 'N/A'):.3f}"],
                ['p-value', f"{test_result.get('p', 'N/A'):.4f}"],
                ['df1', str(test_result.get('df1', 'N/A'))],
                ['df2', str(test_result.get('df2', 'N/A'))],
                ['Effect Size (η²)', f"{test_result.get('effect_size', 'N/A'):.3f}"],
                ['Significant', 'Yes' if test_result.get('significant', False) else 'No']
            ]
        })
    
    # One-way ANOVA results
    elif analysis_type == 'one_way_anova' and 'result' in result:
        test_result = result['result']
        tables.append({
            'title': 'One-Way ANOVA Results',
            'headers': ['Metric', 'Value'],
            'rows': [
                ['F-value', f"{test_result.get('F', 'N/A'):.3f}"],
                ['p-value', f"{test_result.get('p', 'N/A'):.4f}"],
                ['df1', str(test_result.get('df1', 'N/A'))],
                ['df2', str(test_result.get('df2', 'N/A'))],
                ['Effect Size (η²)', f"{test_result.get('effect_size', 'N/A'):.3f}"],
                ['Significant', 'Yes' if test_result.get('significant', False) else 'No']
            ]
        })
    
    # Correlation results
    elif analysis_type == 'correlation' and 'result' in result:
        test_result = result['result']
        tables.append({
            'title': 'Correlation Results',
            'headers': ['Metric', 'Value'],
            'rows': [
                ['Correlation (r)', f"{test_result.get('r', 'N/A'):.3f}"],
                ['p-value', f"{test_result.get('p', 'N/A'):.4f}"],
                ['df', str(test_result.get('df', 'N/A'))],
                ['Significant', 'Yes' if test_result.get('significant', False) else 'No']
            ]
        })
    
    # If no specific formatting, return a generic table with all result data
    if not tables and 'result' in result and isinstance(result['result'], dict):
        headers = ['Metric', 'Value']
        rows = []
        for key, value in result['result'].items():
            if isinstance(value, (int, float)):
                rows.append([key, f"{value:.3f}" if isinstance(value, float) else str(value)])
            else:
                rows.append([key, str(value)])
        
        tables.append({
            'title': result.get('test', 'Analysis Results'),
            'headers': headers,
            'rows': rows
        })
    
    # If still no tables, return a simple message
    if not tables:
        tables.append({
            'title': 'Analysis Results',
            'headers': ['Message'],
            'rows': [['No detailed results available']]
        })
    
    return tables

@api_bp.route('/api/dashboard/stats')
def dashboard_stats():
    """
    API endpoint to provide dashboard statistics
    Returns JSON data for dashboard charts and stats cards
    """
    try:
        # Get cached summary statistics
        stats = get_summary_stats()
        
        # Format response data
        response = {
            'total_participants': stats.get('n_participants', 0),
            'total_responses': stats.get('n_responses', 0),
            'trust_mean': stats.get('trust_mean', 0),
            'trust_std': stats.get('trust_sd', 0),
            'trust_distribution': {
                '1': stats.get('trust_dist', {}).get('1', 0),
                '2': stats.get('trust_dist', {}).get('2', 0),
                '3': stats.get('trust_dist', {}).get('3', 0),
                '4': stats.get('trust_dist', {}).get('4', 0),
                '5': stats.get('trust_dist', {}).get('5', 0),
                '6': stats.get('trust_dist', {}).get('6', 0),
                '7': stats.get('trust_dist', {}).get('7', 0)
            },
            'masculinity_by_version': {
                'Full Face': stats.get('masculinity_by_version', {}).get('full', 0),
                'Left Half': stats.get('masculinity_by_version', {}).get('left', 0),
                'Right Half': stats.get('masculinity_by_version', {}).get('right', 0)
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        # Return error response
        return jsonify({
            'error': str(e),
            'message': 'Error retrieving dashboard statistics'
        }), 500

@api_bp.route('/api/run_analysis', methods=['POST'])
def run_analysis():
    """
    API endpoint to run analysis on face data
    Returns JSON data for analytics charts
    """
    from flask import request
    import json
    import csv
    from analytics.r_integration import RAnalytics
    
    try:
        # Get request data
        data = request.get_json() or {}
        # Accept 'test' (preferred) and fall back to 'analysis_type'
        analysis_type = data.get('test') or data.get('analysis_type')
        variables = data.get('variables', {})
        # Accept 'dv' (preferred) and fall back to nested 'variables.variable'
        variable = data.get('dv') or variables.get('variable')
        secondary_variable = variables.get('secondary_variable')
        
        # Log the request for debugging
        print(f"Running analysis: {analysis_type} on {variable} with secondary variable {secondary_variable}")
        
        # Check if we have valid parameters
        if not analysis_type or not variable:
            return jsonify({
                'ok': False,
                'error': 'Missing parameters',
                'message': 'Analysis type (test) and variable (dv) are required'
            }), 400
        
        # Special test case for debugging
        if analysis_type == 'test':
            return jsonify({
                'ok': True,
                'analysis_type': 'Test Analysis',
                'variable': variable,
                'summary': 'This is a test analysis to verify the API is working correctly.',
                'tables': [{
                    'title': 'Test Results',
                    'headers': ['Metric', 'Value'],
                    'rows': [
                        ['Mean', '4.7'],
                        ['Median', '5.0'],
                        ['Std Dev', '0.8']
                    ]
                }]
            })
        
        # Attempt to load data from CSV files
        data_dir = os.path.join(os.getcwd(), 'data', 'responses')
        
        # Check if data directory exists
        if not os.path.exists(data_dir):
            return jsonify({
                'ok': False,
                'error': 'Data directory not found',
                'message': f'Could not find data directory at {data_dir}'
            }), 500
        
        # Check if there are any CSV files
        csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
        if not csv_files:
            return jsonify({
                'ok': False,
                'error': 'No data files',
                'message': 'No CSV files found in data directory'
            }), 404
            
        # Load data from CSV files
        all_data = {'columns': [], 'rows': []}
        column_names = set()
        error_files = []
        processed_files = 0
        
        print(f"Processing {len(csv_files)} CSV files from {data_dir}")
        
        # First pass: collect all column names
        for csv_file in csv_files:
            file_path = os.path.join(data_dir, csv_file)
            try:
                with open(file_path, 'r', newline='') as f:
                    reader = csv.reader(f)
                    headers = next(reader, None)
                    if headers:
                        for header in headers:
                            column_names.add(header.strip())
                        processed_files += 1
                    else:
                        error_files.append(f"{csv_file} (empty or no headers)")
            except Exception as e:
                error_files.append(f"{csv_file} ({str(e)})")
                print(f"Error reading headers from {csv_file}: {str(e)}")
                
        print(f"Found {len(column_names)} unique columns across {processed_files} files")
        if error_files:
            print(f"Warning: Could not process {len(error_files)} files: {', '.join(error_files[:5])}{'...' if len(error_files) > 5 else ''}")
            
        # Check if we have required columns for the selected analysis type
        required_columns = get_required_columns(analysis_type, variable, secondary_variable)
        missing_columns = [col for col in required_columns if col not in column_names]
        
        if missing_columns:
            return jsonify({
                'ok': False,
                'error': 'Missing required columns',
                'message': f"The following required columns are missing from your data: {', '.join(missing_columns)}"
            }), 400
        
        # Convert to sorted list for consistent ordering
        all_data['columns'] = sorted(list(column_names))
        
        # Second pass: read all data rows
        for csv_file in csv_files:
            file_path = os.path.join(data_dir, csv_file)
            try:
                with open(file_path, 'r', newline='') as f:
                    reader = csv.reader(f)
                    file_headers = next(reader, None)
                    if not file_headers:
                        continue
                        
                    # Create header index mapping
                    header_indices = {h.strip(): i for i, h in enumerate(file_headers)}
                    
                    # Read each row
                    for row in reader:
                        # Create a row with all columns (filling missing values with None)
                        new_row = [None] * len(all_data['columns'])
                        
                        # Fill in values from this CSV
                        for col_idx, col_name in enumerate(all_data['columns']):
                            if col_name in header_indices:
                                file_col_idx = header_indices[col_name]
                                if file_col_idx < len(row):
                                    new_row[col_idx] = row[file_col_idx]
                        
                        all_data['rows'].append(new_row)
            except Exception as e:
                print(f"Error reading data from {csv_file}: {str(e)}")
        
        # Check if we have any data
        if not all_data['rows']:
            return jsonify({
                'ok': False,
                'error': 'Empty dataset',
                'message': 'No data rows found in CSV files'
            }), 404
        
        # Initialize R analytics module
        r_analytics = RAnalytics()
        
        # Map analysis types to R functions
        r_analysis_type_map = {
            'descriptive': 'descriptive',
            'ttest': 'paired_ttest',
            'independent_ttest': 'independent_ttest',
            'anova': 'one_way_anova',
            'repeated_measures_anova': 'repeated_measures_anova',
            'correlation': 'correlation'
        }
        
        # Get the R analysis type
        r_analysis_type = r_analysis_type_map.get(analysis_type, 'descriptive')
        
        # Prepare variables list
        variables = [variable]
        if secondary_variable:
            variables.append(secondary_variable)
        
        # Run the analysis
        result = r_analytics.run_analysis(r_analysis_type, all_data, variables)
        
        # Check for errors
        if 'error' in result:
            return jsonify({
                'ok': False,
                'error': result.get('error', 'Unknown error'),
                'message': result.get('message', 'An error occurred during analysis')
            }), 400
        
        # Format the result for the frontend
        formatted_result = {
            'ok': True,
            'analysis_type': result.get('test', analysis_type.capitalize()),
            'variable': variable,
            'secondary_variable': secondary_variable,
            'summary': _get_analysis_summary(result, analysis_type, variable, secondary_variable),
            'tables': _format_tables_from_r_result(result, analysis_type)
        }
        
        return jsonify(formatted_result)
            
    except Exception as e:
        import traceback
        print(f"Error in run_analysis: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'ok': False,
            'error': 'Server error',
            'message': f'An error occurred while processing the analysis: {str(e)}'
        }), 500

# Alias to support dashed path
@api_bp.route('/api/run-analysis', methods=['POST'])
def run_analysis_alias():
    return run_analysis()

"""
API routes for Face Viewer Dashboard
"""

from flask import Blueprint, jsonify
from utils.dashboard_stats_no_pandas import get_summary_stats
import os

# Create blueprint
api_bp = Blueprint('api', __name__)

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

@api_bp.route('/api/run_analysis')
def run_analysis():
    """
    API endpoint to run analysis on face data
    Returns JSON data for analytics charts
    """
    data_dir = os.path.join(os.getcwd(), 'data', 'responses')
    
    # Demo data for now - will be replaced with actual data processing
    response = {
        "gender_labels": ["Male", "Female"],
        "gender_data": [4.5, 5.1],
        "side_labels": ["Left", "Right"],
        "side_data": [4.7, 4.8],
        "participant_ids": ["P001", "P002", "P003"],
        "participant_averages": [4.6, 5.0, 4.9],
        "participant_stddevs": [0.5, 0.7, 0.3]
    }
    
    return jsonify(response)

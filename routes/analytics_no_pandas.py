"""
Analytics routes for Face Viewer Dashboard (pandas-free version)
Handles advanced analytics and data visualization
"""

from flask import Blueprint, render_template, request, jsonify, send_file
import os
import json
import csv
from datetime import datetime
from utils.cache import cached, clear_cache, cache
from utils.dashboard_stats_no_pandas import get_summary_stats

# Create blueprint
analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
def dashboard():
    """Display the analytics dashboard"""
    # Get summary statistics
    stats = get_summary_stats()
    
    # Format for template
    summary_stats = {
        'total_participants': stats.get('n_participants', 0),
        'total_responses': stats.get('n_responses', 0),
        'avg_trust_rating': stats.get('trust_mean', 0),
        'std_trust_rating': stats.get('trust_sd', 0),
    }
    
    # Mock available analyses for demo
    available_analyses = [
        {'id': 'trust_by_face', 'name': 'Trust Rating by Face Type'},
        {'id': 'masc_by_side', 'name': 'Masculinity by Face Side'},
        {'id': 'symmetry_analysis', 'name': 'Symmetry Score Analysis'},
        {'id': 'trust_masc_correlation', 'name': 'Trust-Masculinity Correlation'}
    ]
    
    # Mock columns for data analysis
    columns = [
        {'id': 'participant_id', 'name': 'Participant ID', 'type': 'string'},
        {'id': 'face_id', 'name': 'Face ID', 'type': 'string'},
        {'id': 'face_type', 'name': 'Face Type', 'type': 'categorical'},
        {'id': 'trust_rating', 'name': 'Trust Rating', 'type': 'numeric'},
        {'id': 'masculinity_score', 'name': 'Masculinity Score', 'type': 'numeric'},
        {'id': 'symmetry_score', 'name': 'Symmetry Score', 'type': 'numeric'},
        {'id': 'response_time', 'name': 'Response Time (ms)', 'type': 'numeric'}
    ]
    
    # Render analytics template
    return render_template(
        'analytics.html',
        title='Face Viewer Analytics',
        summary_stats=summary_stats,
        available_analyses=available_analyses,
        columns=columns
    )

@analytics_bp.route('/api/run_analysis', methods=['GET', 'POST'])
def run_analysis():
    """API endpoint to run statistical analysis"""
    # Get request data
    if request.method == 'POST':
        data = request.json
        analysis_type = data.get('analysis_type')
    else:  # GET method
        analysis_type = request.args.get('analysis_type', 'trust_by_face')
    
    # Mock analysis results
    results = {
        'success': True,
        'analysis_type': analysis_type,
        'timestamp': datetime.now().isoformat(),
        'summary': f"Analysis completed for {analysis_type}",
        'charts': [
            {
                'type': 'bar',
                'title': 'Trust Ratings by Face Type',
                'data': {
                    'labels': ['Full Face', 'Left Half', 'Right Half'],
                    'datasets': [
                        {
                            'label': 'Average Trust Rating',
                            'data': [5.56, 4.79, 4.49]
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
                    ['Mean Difference (Full-Left)', '0.77', '0.023'],
                    ['Mean Difference (Full-Right)', '1.07', '0.008'],
                    ['Mean Difference (Left-Right)', '0.30', '0.412']
                ]
            }
        ]
    }
    
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

"""
Analytics routes for Face Viewer Dashboard
Provides analytics dashboard and related functionality
"""
import os
import json
import logging
from flask import Blueprint, render_template, jsonify, request

# Create blueprint
analytics = Blueprint('analytics', __name__, template_folder='../templates/analytics')

# Set up logging
logger = logging.getLogger(__name__)

@analytics.route('/dashboard')
def dashboard():
    """Analytics dashboard route"""
    try:
        # Load data for analytics
        # In a production app, this would load from database or files
        # For now, we'll use demo data
        
        stats = {
            'total_participants': 42,
            'total_responses': 126,
            'avg_trust_rating': 5.2,
            'std_trust_rating': 1.3,
            'trust_by_version': {
                'Full Face': 5.4,
                'Left Half': 4.9,
                'Right Half': 5.3
            }
        }
        
        # Sample data for charts
        trust_distribution = [5, 8, 12, 20, 35, 30, 16]  # Count of ratings 1-7
        symmetry_labels = ['Face 1', 'Face 2', 'Face 3', 'Face 4', 'Face 5']
        symmetry_data = [0.85, 0.76, 0.92, 0.88, 0.79]
        masculinity_labels = ['Face 1', 'Face 2', 'Face 3', 'Face 4', 'Face 5']
        masculinity_left = [0.65, 0.72, 0.58, 0.63, 0.70]
        masculinity_right = [0.68, 0.75, 0.55, 0.60, 0.73]
        
        return render_template(
            'analytics/dashboard.html',
            title='Analytics Dashboard',
            stats=stats,
            trust_distribution=trust_distribution,
            symmetry_labels=symmetry_labels,
            symmetry_data=symmetry_data,
            masculinity_labels=masculinity_labels,
            masculinity_left=masculinity_left,
            masculinity_right=masculinity_right
        )
    except Exception as e:
        logger.error(f"Error rendering analytics dashboard: {str(e)}")
        return render_template('../templates/error.html', error=str(e))

@analytics.route('/reports')
def reports():
    """Analytics reports route"""
    return render_template('analytics/reports.html', title='Analytics Reports')

@analytics.route('/export')
def export():
    """Data export route"""
    return render_template('analytics/export.html', title='Export Data')

@analytics.route('/r_tools')
def r_tools():
    """R analysis tools route"""
    return render_template('analytics/r_tools.html', title='R Analysis Tools')

@analytics.route('/spss_tools')
def spss_tools():
    """SPSS analysis tools route"""
    return render_template('analytics/spss_tools.html', title='SPSS Analysis Tools')

@analytics.route('/api/run_analysis', methods=['POST'])
def run_analysis():
    """API endpoint to run statistical analysis"""
    try:
        data = request.json
        analysis_type = data.get('analysis_type')
        variables = data.get('variables', [])
        
        # In a real app, this would run actual analysis
        # For now, return mock results
        
        result = {
            'summary': f"Successfully ran {analysis_type} analysis on {len(variables)} variables.",
            'tables': [
                {
                    'title': 'Descriptive Statistics',
                    'headers': ['Variable', 'N', 'Mean', 'Std Dev', 'Min', 'Max'],
                    'rows': [
                        ['Trust Rating', '126', '5.2', '1.3', '1', '7'],
                        ['Symmetry Score', '42', '0.84', '0.08', '0.65', '0.95'],
                        ['Masculinity (Left)', '42', '0.66', '0.12', '0.45', '0.85'],
                        ['Masculinity (Right)', '42', '0.68', '0.14', '0.42', '0.88']
                    ]
                }
            ]
        }
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error running analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500

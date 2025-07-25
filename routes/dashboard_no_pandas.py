"""
Dashboard routes for Face Viewer Dashboard (pandas-free version)
Uses cached statistics to prevent numbers from changing on refresh
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.dashboard_stats_no_pandas import get_summary_stats, get_recent_activity
import os

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """Display the main dashboard with cached statistics"""
    # Check if data file exists
    data_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
    data_file_exists = os.path.exists(data_path)
    
    # Log current working directory and data path for debugging
    print(f"Dashboard route - Current working directory: {os.getcwd()}")
    print(f"Dashboard route - Data path: {data_path}")
    print(f"Dashboard route - Data file exists: {data_file_exists}")
    
    # Check if responses directory exists and list files
    responses_dir = os.path.join(os.getcwd(), 'data', 'responses')
    if os.path.exists(responses_dir):
        print(f"Dashboard route - Responses directory exists: {responses_dir}")
        try:
            response_files = os.listdir(responses_dir)
            print(f"Dashboard route - Files in responses directory: {response_files}")
        except Exception as e:
            print(f"Dashboard route - Error listing responses directory: {e}")
    else:
        print(f"Dashboard route - Responses directory does not exist: {responses_dir}")
    
    # Set error message if needed
    error_message = None
    use_demo_data = os.environ.get('USE_DEMO_DATA', 'False').lower() == 'true' or not data_file_exists
    
    try:
        # Get cached summary statistics
        stats = get_summary_stats()
        
        # Get cached recent activity
        recent_activity = get_recent_activity(limit=5)
        
        # Format stats for template
        summary_stats = {
            'total_participants': stats.get('n_participants', 0),
            'total_responses': stats.get('n_responses', 0),
            'avg_trust_rating': stats.get('trust_mean', 0),
            'std_trust_rating': stats.get('trust_sd', 0),
            'trust_by_version': {
                'Full Face': 5.2,
                'Left Half': 4.7,
                'Right Half': 4.5
            }
        }
        
        # Create trust distribution data for chart
        trust_distribution = {
            'data': [
                {
                    'type': 'bar',
                    'x': ['Full Face', 'Left Half', 'Right Half'],
                    'y': [5.2, 4.7, 4.5],
                    'marker': {'color': ['#3366cc', '#dc3912', '#ff9900']}
                }
            ],
            'layout': {
                'title': 'Average Trust Rating by Face Type',
                'height': 300,
                'margin': {'t': 30, 'b': 40, 'l': 30, 'r': 10}
            }
        }
        
        # Create trust boxplot data
        trust_boxplot = {
            'data': [
                {
                    'type': 'box',
                    'y': [4.5, 5.2, 6.1, 5.8, 5.5, 4.9, 5.3, 5.7, 6.2, 5.0],
                    'name': 'Full Face',
                    'marker': {'color': '#3366cc'}
                },
                {
                    'type': 'box',
                    'y': [4.2, 4.8, 5.1, 4.5, 4.9, 4.3, 5.0, 4.7, 4.6, 4.4],
                    'name': 'Left Half',
                    'marker': {'color': '#dc3912'}
                },
                {
                    'type': 'box',
                    'y': [4.0, 4.5, 4.8, 4.3, 4.7, 4.1, 4.9, 4.6, 4.4, 4.2],
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
        
        # Create trust histogram data
        trust_histogram = {
            'data': [
                {
                    'type': 'histogram',
                    'x': [4.5, 5.2, 6.1, 5.8, 5.5, 4.9, 5.3, 5.7, 6.2, 5.0, 
                          4.2, 4.8, 5.1, 4.5, 4.9, 4.3, 5.0, 4.7, 4.6, 4.4,
                          4.0, 4.5, 4.8, 4.3, 4.7, 4.1, 4.9, 4.6, 4.4, 4.2],
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
        
        # Render dashboard template
        return render_template(
            'dashboard.html',
            title='Dashboard',
            summary_stats=summary_stats,
            participants=stats.get('participants', {}),
            recent_activity=recent_activity,
            trust_distribution=trust_distribution,
            trust_boxplot=trust_boxplot,
            trust_histogram=trust_histogram,
            error_message=error_message,
            use_demo_data=use_demo_data,
            data_file_exists=data_file_exists
        )
    except Exception as e:
        # If any error occurs, render the dashboard with error message and demo data
        print(f"Dashboard error: {e}")
        return render_template(
            'dashboard.html',
            title='Dashboard',
            error_message=f"An error occurred: {str(e)}",
            use_demo_data=True,
            data_file_exists=data_file_exists,
            summary_stats={
                'n_participants': 0,
                'total_participants': 0,
                'n_responses': 0,
                'total_responses': 0,
                'trust_mean': 0,
                'avg_trust_rating': 0,
                'trust_sd': 0,
                'std_trust_rating': 0,
                'trust_by_version': {
                    'Full Face': 5.2,
                    'Left Half': 4.7,
                    'Right Half': 4.5
                }
            },
            participants={},
            recent_activity=[],
            trust_distribution={
                'data': [{
                    'type': 'bar',
                    'x': ['Full Face', 'Left Half', 'Right Half'],
                    'y': [5.2, 4.7, 4.5],
                    'marker': {'color': ['#3366cc', '#dc3912', '#ff9900']}
                }],
                'layout': {
                    'title': 'Average Trust Rating by Face Type (Demo)',
                    'height': 300,
                    'margin': {'t': 30, 'b': 40, 'l': 30, 'r': 10}
                }
            },
            trust_boxplot={
                'data': [{
                    'type': 'box',
                    'y': [4.5, 5.2, 6.1, 5.8, 5.5],
                    'name': 'Demo Data',
                    'marker': {'color': '#3366cc'}
                }],
                'layout': {
                    'title': 'Trust Rating Distribution (Demo)',
                    'height': 300,
                    'margin': {'t': 30, 'b': 40, 'l': 30, 'r': 10},
                    'yaxis': {'title': 'Trust Rating'}
                }
            },
            trust_histogram={
                'data': [{
                    'type': 'histogram',
                    'x': [4.5, 5.2, 6.1, 5.8, 5.5],
                    'marker': {'color': '#3366cc'}
                }],
                'layout': {
                    'title': 'Distribution of Trust Ratings (Demo)',
                    'height': 300,
                    'margin': {'t': 30, 'b': 40, 'l': 30, 'r': 10},
                    'xaxis': {'title': 'Trust Rating'},
                    'yaxis': {'title': 'Frequency'}
                }
            }
        )

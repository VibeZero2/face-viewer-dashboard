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
    # Get cached summary statistics
    stats = get_summary_stats()
    
    # Get cached recent activity
    recent_activity = get_recent_activity(limit=5)
    
    # Check if we should use demo data
    use_demo_data = os.environ.get('USE_DEMO_DATA', 'False').lower() == 'true'
    
    # Format stats for template
    summary_stats = {
        'total_participants': stats.get('n_participants', 0),
        'total_responses': stats.get('n_responses', 0),
        'avg_trust_rating': stats.get('trust_mean', 0),
        'std_trust_rating': stats.get('trust_sd', 0),
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
        trust_histogram=trust_histogram
    )

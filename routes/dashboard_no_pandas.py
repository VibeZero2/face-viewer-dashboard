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
    
    # Render dashboard template
    return render_template(
        'dashboard.html',
        title='Dashboard',
        summary_stats=stats,
        participants=stats.get('participants', {}),
        recent_activity=recent_activity,
        trust_distribution=stats.get('trust_distribution', {}),
        trust_boxplot=stats.get('trust_boxplot', {}),
        trust_histogram=stats.get('trust_histogram', {})
    )

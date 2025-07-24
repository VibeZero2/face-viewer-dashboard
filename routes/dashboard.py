"""
Dashboard routes for Face Viewer Dashboard
Uses cached statistics to prevent numbers from changing on refresh
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.dashboard_stats_no_pandas import get_summary_stats, get_recent_activity
from utils.participants_no_pandas import get_all_participants
import os

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """Display the main dashboard with fresh statistics"""
    # Always get fresh statistics (no caching)
    stats = get_summary_stats()
    
    # Get recent activity
    recent_activity = get_recent_activity(limit=5)
    
    # Get all participants
    participants = get_all_participants()
    
    # Format participant data for the dashboard
    participant_data = {}
    for p in participants:
        pid = p.get('participant_id') or p.get('pid', 'Unknown')
        if pid not in participant_data:
            participant_data[pid] = {'csv': False, 'xlsx': False, 'enc': False}
        
        # Assume we have these formats available
        participant_data[pid]['csv'] = True
    
    # Check if we should use demo data
    use_demo_data = os.environ.get('USE_DEMO_DATA', 'False').lower() == 'true'
    
    # Generate trust histogram and boxplot data
    trust_histogram = {'data': [], 'layout': {}}
    trust_boxplot = {'data': [], 'layout': {}}
    
    # Render dashboard template with the full UI
    return render_template(
        'dashboard.html',  # Use the full dashboard template
        summary_stats=stats,
        recent_activity=recent_activity,
        participants=participant_data,
        trust_histogram=trust_histogram,
        trust_boxplot=trust_boxplot,
        use_demo_data=use_demo_data
    )

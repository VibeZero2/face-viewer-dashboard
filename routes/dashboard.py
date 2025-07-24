"""
Dashboard routes for Face Viewer Dashboard
Uses cached statistics to prevent numbers from changing on refresh
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.dashboard_stats_no_pandas import get_summary_stats, get_recent_activity
from utils.participants_no_pandas import get_all_participants
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """Display the main dashboard with fresh statistics"""
    try:
        # Check if data directory exists
        data_dir = os.path.join(os.getcwd(), 'data')
        data_file = os.path.join(data_dir, 'working_data.csv')
        
        # Create data directory if it doesn't exist
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created data directory at {data_dir}")
        
        # Check if data file exists
        data_file_exists = os.path.exists(data_file)
        if not data_file_exists:
            logger.warning(f"Data file not found: {data_file}")
            
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
        use_demo_data = os.environ.get('USE_DEMO_DATA', 'False').lower() == 'true' or not data_file_exists
        
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
            use_demo_data=use_demo_data,
            data_file_exists=data_file_exists
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        # Return a simplified error template with error details
        return render_template(
            'dashboard.html',
            summary_stats={
                "n_participants": 0,
                "n_responses": 0,
                "trust_mean": 0,
                "trust_sd": 0
            },
            recent_activity=[],
            participants={},
            trust_histogram={'data': [], 'layout': {}},
            trust_boxplot={'data': [], 'layout': {}},
            use_demo_data=True,
            error_message=f"An error occurred: {str(e)}"
        )

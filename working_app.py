"""
Simplified Face Viewer Dashboard application
Designed to run reliably on port 8080
"""
import os
import logging
from flask import Flask, redirect, render_template, request, url_for
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Configure secret key
app.secret_key = os.environ.get('DASHBOARD_SECRET_KEY', os.environ.get('FLASK_SECRET_KEY', os.urandom(24).hex()))

# Ensure data directory exists
data_dir = os.path.join(os.getcwd(), 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    logger.info(f"Created data directory at {data_dir}")

# Root route redirects to dashboard
@app.route('/')
def index():
    return redirect('/dashboard')

# Simple dashboard route
@app.route('/dashboard')
def dashboard():
    try:
        # Check if data directory exists
        data_dir = os.path.join(os.getcwd(), 'data')
        data_file = os.path.join(data_dir, 'working_data.csv')
        
        # Check if data file exists
        data_file_exists = os.path.exists(data_file)
        if not data_file_exists:
            logger.warning(f"Data file not found: {data_file}")
        
        # Use demo data if no real data exists
        use_demo_data = not data_file_exists
        
        # Mock statistics for initial view
        stats = {
            "n_participants": 0 if use_demo_data else 42,
            "n_responses": 0 if use_demo_data else 126,
            "trust_mean": 0 if use_demo_data else 5.2,
            "trust_sd": 0 if use_demo_data else 1.3
        }
        
        # Render dashboard template
        return render_template(
            'dashboard.html',
            summary_stats=stats,
            recent_activity=[],
            participants={},
            trust_histogram={'data': [], 'layout': {}},
            trust_boxplot={'data': [], 'layout': {}},
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

# Health check endpoint
@app.route('/health')
def health():
    return {"status": "healthy"}

if __name__ == '__main__':
    # Log startup information
    logger.info("Starting Face Viewer Dashboard on port 8080")
    logger.info("Access the dashboard at: http://localhost:8080")
    
    # Print user-friendly message
    print("=" * 50)
    print("Starting Face Viewer Dashboard")
    print("=" * 50)
    print("Server will be available at: http://localhost:8080")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Run the Flask app on port 8080
        app.run(host='localhost', port=8080, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        print(f"ERROR: Failed to start server: {str(e)}")

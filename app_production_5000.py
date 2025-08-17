"""
Face Viewer Dashboard - Production App
Running on port 5000 with error handling and logging
"""
import os
import sys
import json
import logging
from datetime import datetime
from flask import Flask, redirect, render_template, url_for, jsonify, request

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure secret key from environment or generate one
app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24).hex())

# Register blueprints
from admin import auth_bp
from routes.admin_tools import admin_tools as admin_tools_bp
from routes.analytics import analytics as analytics_bp

app.register_blueprint(auth_bp, url_prefix='/admin')
app.register_blueprint(admin_tools_bp, url_prefix='/admin')
app.register_blueprint(analytics_bp, url_prefix='/analytics')

# Data directory setup
DATA_DIR = os.environ.get('FACE_VIEWER_DATA_DIR', os.path.join(os.getcwd(), 'data'))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    logger.info(f"Created data directory at {DATA_DIR}")

# Root route redirects to dashboard
@app.route('/')
def index():
    return redirect('/dashboard')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    try:
        logger.info("Dashboard route accessed")
        
        # Check if data directory exists and has files
        data_file_exists = False
        data_files = []
        
        try:
            if os.path.exists(DATA_DIR):
                data_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.csv')]
                data_file_exists = len(data_files) > 0
                logger.info(f"Found {len(data_files)} data files in {DATA_DIR}")
        except Exception as e:
            logger.error(f"Error checking data directory: {str(e)}")
        
        # Use demo data if no real data exists
        use_demo_data = not data_file_exists
        
        # Create stats dictionary with demo values
        stats = {
            'n_participants': 42,
            'n_responses': 126,
            'trust_mean': 5.2,
            'trust_sd': 1.3,
            'trust_by_version': {
                'Full_Face': 5.4,
                'Left_Half': 4.9,
                'Right_Half': 5.3
            }
        }
        
        # Create empty chart data structures for Plotly
        trust_distribution = {
            'data': [
                {
                    'type': 'bar',
                    'x': ['Full Face', 'Left Half', 'Right Half'],
                    'y': [5.4, 4.9, 5.3],
                    'marker': {'color': ['#3366cc', '#dc3912', '#ff9900']}
                }
            ],
            'layout': {
                'title': 'Average Trust Rating by Face Type',
                'height': 300,
                'margin': {'t': 30, 'b': 40, 'l': 30, 'r': 10}
            }
        }
        
        trust_boxplot = {
            'data': [
                {
                    'type': 'box',
                    'y': [5, 6, 5, 6, 5, 4, 6],
                    'name': 'Full Face',
                    'marker': {'color': '#3366cc'}
                },
                {
                    'type': 'box',
                    'y': [5, 4, 5, 6, 4, 5, 5],
                    'name': 'Left Half',
                    'marker': {'color': '#dc3912'}
                },
                {
                    'type': 'box',
                    'y': [6, 5, 5, 6, 5, 5, 5],
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
        
        trust_histogram = {
            'data': [
                {
                    'type': 'histogram',
                    'x': [5, 6, 5, 6, 5, 4, 6, 5, 4, 5, 6, 4, 5, 5, 6, 5, 5, 6, 5, 5, 5],
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
        
        # Create sample data for charts
        trustRatingsData = {
            'labels': ['Full Face', 'Left Half', 'Right Half'],
            'datasets': [{
                'label': 'Average Trust Rating',
                'data': [5.4, 4.9, 5.3],
                'backgroundColor': ['#3366cc', '#dc3912', '#ff9900']
            }]
        }
        
        symmetryChartData = {
            'labels': ['Face 1', 'Face 2', 'Face 3', 'Face 4', 'Face 5'],
            'datasets': [{
                'label': 'Symmetry Score',
                'data': [0.85, 0.76, 0.92, 0.88, 0.79],
                'borderColor': '#3366cc',
                'backgroundColor': 'rgba(51, 102, 204, 0.2)',
                'fill': True
            }]
        }
        
        masculinityChartData = {
            'labels': ['Face 1', 'Face 2', 'Face 3', 'Face 4', 'Face 5'],
            'datasets': [
                {
                    'label': 'Left Side',
                    'data': [0.65, 0.72, 0.58, 0.63, 0.70],
                    'borderColor': '#dc3912',
                    'backgroundColor': 'rgba(220, 57, 18, 0.2)'
                },
                {
                    'label': 'Right Side',
                    'data': [0.68, 0.75, 0.55, 0.60, 0.73],
                    'borderColor': '#ff9900',
                    'backgroundColor': 'rgba(255, 153, 0, 0.2)'
                }
            ]
        }
        
        femininityChartData = {
            'labels': ['Face 1', 'Face 2', 'Face 3', 'Face 4', 'Face 5'],
            'datasets': [
                {
                    'label': 'Left Side',
                    'data': [0.35, 0.28, 0.42, 0.37, 0.30],
                    'borderColor': '#990099',
                    'backgroundColor': 'rgba(153, 0, 153, 0.2)'
                },
                {
                    'label': 'Right Side',
                    'data': [0.32, 0.25, 0.45, 0.40, 0.27],
                    'borderColor': '#109618',
                    'backgroundColor': 'rgba(16, 150, 24, 0.2)'
                }
            ]
        }
        
        # Sample participant data
        participants = [
            {'id': 'P001', 'responses': 7, 'avg_trust': 5.4, 'last_active': '2025-08-16'},
            {'id': 'P002', 'responses': 7, 'avg_trust': 4.9, 'last_active': '2025-08-16'},
            {'id': 'P003', 'responses': 7, 'avg_trust': 5.3, 'last_active': '2025-08-17'}
        ]
        
        # Sample recent activity
        recent_activity = [
            {'participant': 'P003', 'action': 'Submitted rating', 'time': '10 minutes ago'},
            {'participant': 'P002', 'action': 'Completed session', 'time': '1 hour ago'},
            {'participant': 'P001', 'action': 'Started session', 'time': '2 hours ago'}
        ]
        
        # Render dashboard template
        return render_template(
            'dashboard.html',
            title='Face Viewer Dashboard', 
            stats=stats, 
            summary_stats=stats,
            participants=participants,
            responses=[],
            total_responses=stats['n_responses'],
            total_participants=stats['n_participants'],
            avg_trust=stats['trust_mean'],
            std_trust=stats['trust_sd'],
            recent_activity=recent_activity,
            # JSON serialized chart data for JavaScript
            trust_ratings_json=json.dumps(trustRatingsData),
            symmetry_chart_json=json.dumps(symmetryChartData),
            masculinity_chart_json=json.dumps(masculinityChartData),
            femininity_chart_json=json.dumps(femininityChartData),
            trust_distribution_json=json.dumps(trust_distribution),
            trust_boxplot_json=json.dumps(trust_boxplot),
            trust_histogram_json=json.dumps(trust_histogram),
            # Raw data for additional processing
            trust_hist=json.dumps({str(i): [5, 8, 12, 20, 35, 30, 16][i-1] for i in range(1, 8)}),
            avg_symmetry=json.dumps({'Face 1': 0.85, 'Face 2': 0.76, 'Face 3': 0.92, 'Face 4': 0.88, 'Face 5': 0.79}),
            avg_masc=json.dumps({'Full Face': 0.68, 'Left Half': 0.66, 'Right Half': 0.67}),
            avg_fem=json.dumps({'Full Face': 0.32, 'Left Half': 0.34, 'Right Half': 0.33}),
            error_message=None,
            use_demo_data=True,
            data_file_exists=data_file_exists,
            server_port=5000
        )
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        return render_template(
            'dashboard.html',
            title='Face Viewer Dashboard - Error', 
            stats={
                'total_participants': 0,
                'total_responses': 0,
                'trust_mean': 0,
                'trust_std': 0,
                'trust_by_version': {
                    'Full_Face': 0,
                    'Left_Half': 0,
                    'Right_Half': 0
                }
            }, 
            summary_stats={
                'n_participants': 0,
                'n_responses': 0,
                'trust_mean': 0,
                'trust_sd': 0
            },
            participants=[],
            responses=[],
            total_responses=0,
            total_participants=0,
            avg_trust=0,
            std_trust=0,
            recent_activity=[],
            # JSON serialized chart data for JavaScript
            trust_ratings_json=json.dumps({'labels': [], 'datasets': []}),
            symmetry_chart_json=json.dumps({'labels': [], 'datasets': []}),
            masculinity_chart_json=json.dumps({'labels': [], 'datasets': []}),
            femininity_chart_json=json.dumps({'labels': [], 'datasets': []}),
            trust_distribution_json=json.dumps({'data': [], 'layout': {}}),
            trust_boxplot_json=json.dumps({'data': [], 'layout': {}}),
            trust_histogram_json=json.dumps({'data': [], 'layout': {}}),
            # Raw data for additional processing
            trust_hist=json.dumps({}),
            avg_symmetry=json.dumps({}),
            avg_masc=json.dumps({}),
            avg_fem=json.dumps({}),
            error_message=f"An error occurred: {str(e)}",
            use_demo_data=True,
            data_file_exists=False,
            server_port=5000
        )

# Analytics route
@app.route('/analytics')
def analytics():
    logger.info("Analytics route accessed, redirecting to analytics blueprint")
    return redirect('/analytics/dashboard')

# Login route (redirect to admin login)
@app.route('/login')
def login():
    return redirect('/admin/login')

# Register route (redirect to admin register)
@app.route('/register')
def register():
    return redirect('/admin/register')

# Health check
@app.route('/health')
def health():
    return {"status": "healthy", "port": 5000}

# This is the standard WSGI application variable that Gunicorn looks for
application = app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Face Viewer Dashboard on port {port}...")
    print(f"Server will be available at: http://localhost:{port}")
    logger.info("Starting Face Viewer Dashboard on port 5000")
    logger.info(f"Data directory: {DATA_DIR}")
    
    # Print user-friendly message
    print("=" * 50)
    print("Starting Face Viewer Dashboard")
    print("=" * 50)
    print("Server will be available at: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        # Run the Flask app on port 5000
        app.run(host='localhost', port=5000, debug=True)
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        print(f"ERROR: Failed to start server: {str(e)}")

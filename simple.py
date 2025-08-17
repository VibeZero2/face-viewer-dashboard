"""
Minimal Flask application for Face Viewer Dashboard
This is a simplified version that uses minimal dependencies
"""
from flask import Flask, render_template_string, render_template
import os
import sys
import logging
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Direct import of API blueprints to ensure they're registered
from routes.api import api_bp
from routes.api_variables import api_variables_bp

# Import blueprints
from routes.dashboard_no_pandas import dashboard_bp
from routes.analytics_no_pandas import analytics_bp
from routes.export_no_pandas import export_bp
from routes.participants_no_pandas import participants_bp
from routes.admin_tools import admin_tools
from admin.routes import admin_bp

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('DASHBOARD_SECRET_KEY', os.urandom(24).hex())

# Initialize admin authentication
from admin.auth import AdminAuth
from admin.audit import AuditLog
admin_auth = AdminAuth(app)
audit_log = AuditLog(app)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Check and setup environment variables
from utils.env_checker import setup_environment
env_status = setup_environment()

# Setup API logging middleware
from utils.api_logger import setup_api_logging
app = setup_api_logging(app)

# Register blueprints
app.register_blueprint(dashboard_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(export_bp)
app.register_blueprint(participants_bp)
app.register_blueprint(api_bp)
app.register_blueprint(api_variables_bp)
app.register_blueprint(admin_tools)
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.route('/')
def index():
    """Render the dashboard page with login option"""
    # Import the dashboard function from the dashboard blueprint
    from routes.dashboard_no_pandas import dashboard
    # Call the dashboard function directly
    return dashboard()

@app.route('/login')
def login_redirect():
    """Redirect to admin login page"""
    return redirect(url_for('admin.login'))

@app.route('/register')
def register_redirect():
    """Redirect to admin registration page"""
    return redirect(url_for('admin.register'))
    
# Legacy index page, keeping for reference
def legacy_index():
    """Render the legacy index page"""
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Face Viewer Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
            }
            .success {
                color: green;
                font-weight: bold;
            }
            .info {
                background-color: #f0f0f0;
                padding: 10px;
                border-radius: 4px;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Face Viewer Dashboard</h1>
            <p class="success">✅ Application is running successfully!</p>
            
            <h2>Environment Information</h2>
            <div class="info">
                <p><strong>Python Version:</strong> {{ python_version }}</p>
                <p><strong>Working Directory:</strong> {{ working_dir }}</p>
                <p><strong>Environment Variables:</strong></p>
                <ul>
                    {% for key, value in env_vars.items() %}
                    <li>{{ key }}: {% if "SECRET" in key or "KEY" in key %}[HIDDEN]{% else %}{{ value }}{% endif %}</li>
                    {% endfor %}
                </ul>
            </div>
        </div>
    </body>
    </html>
    """, 
    python_version=sys.version,
    working_dir=os.getcwd(),
    env_vars={k: v for k, v in os.environ.items() if k.startswith(('FLASK', 'DASHBOARD', 'FACE', 'PORT'))}
    )

@app.route('/health')
@app.route('/api/health')
@app.route('/api/ping')
def health():
    """Health check endpoint for Render"""
    return {"status": "ok", "message": "Face Viewer Dashboard is running"}

# Direct API endpoints to ensure they're registered
@app.route('/api/dashboard/stats', methods=['GET'])
def direct_dashboard_stats():
    """Direct dashboard stats endpoint to bypass blueprint issues"""
    try:
        # Get cached summary statistics
        from utils.dashboard_stats_no_pandas import get_summary_stats
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
            },
            'success': True
        }
        
        from flask import jsonify
        return jsonify(response)
    
    except Exception as e:
        # Return error response
        from flask import jsonify
        return jsonify({
            'error': str(e),
            'message': 'Error retrieving dashboard statistics',
            'success': False
        }), 500

@app.route('/api/analytics/variables')
def direct_analytics_variables():
    """Direct analytics variables endpoint to bypass blueprint issues"""
    try:
        import os
        import logging
        import pandas as pd
        from flask import jsonify
        from utils.csv_loader import load_all_data
        
        log = logging.getLogger(__name__)
        log.info("Direct analytics_variables endpoint called")
        
        # Get column mapping from environment variables or use defaults
        column_mapping = {
            'trust_left': os.environ.get('COL_TRUST_LEFT', 'Trust Left'),
            'trust_right': os.environ.get('COL_TRUST_RIGHT', 'Trust Right'),
            'trust_full': os.environ.get('COL_TRUST_FULL', 'Trust Full'),
            'gender': os.environ.get('COL_GENDER', 'Gender'),
            'age': os.environ.get('COL_AGE', 'Age'),
            'timestamp': os.environ.get('COL_TIMESTAMP', 'Timestamp'),
            'symmetry': os.environ.get('COL_SYMMETRY', 'Symmetry'),
            'face_ratio': os.environ.get('COL_FACE_RATIO', 'Face Ratio'),
            'quality': os.environ.get('COL_QUALITY', 'Quality')
        }
        
        # Load data to get actual columns
        df, error = load_all_data()
        
        if error:
            log.warning(f"Error loading data for variables: {error}")
            # Return default variables if data can't be loaded
            variables = [
                {'key': column_mapping['trust_left'], 'label': 'Trust Left'},
                {'key': column_mapping['trust_right'], 'label': 'Trust Right'},
                {'key': column_mapping['trust_full'], 'label': 'Trust Full'},
                {'key': column_mapping['symmetry'], 'label': 'Symmetry'},
                {'key': column_mapping['face_ratio'], 'label': 'Face Ratio'},
                {'key': column_mapping['quality'], 'label': 'Quality'}
            ]
            return jsonify(variables)
        
        # Get actual columns from data
        columns = df.columns.tolist()
        
        # Create variables list with friendly labels
        variables = []
        
        # Add mapped columns first
        for key, col_name in column_mapping.items():
            if col_name in columns:
                # Convert key to friendly label (e.g., trust_left -> Trust Left)
                label = ' '.join(word.capitalize() for word in key.split('_'))
                variables.append({'key': col_name, 'label': label})
        
        # Add any numeric columns not already included
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            if col not in [v['key'] for v in variables]:
                variables.append({'key': col, 'label': col})
        
        log.info(f"Returning {len(variables)} variables for analytics")
        return jsonify(variables)
        
    except Exception as e:
        log.error(f"Error in direct_analytics_variables: {str(e)}", exc_info=True)
        return jsonify([
            {'key': 'Trust Left', 'label': 'Trust Left'},
            {'key': 'Trust Right', 'label': 'Trust Right'},
            {'key': 'Trust Full', 'label': 'Trust Full'}
        ])

@app.route('/api/run_analysis', methods=['POST'])
@app.route('/api/run-analysis', methods=['POST'])
def direct_run_analysis():
    """Direct run analysis endpoint to bypass blueprint issues"""
    try:
        from flask import request, jsonify
        import os
        import logging
        from utils.analysis import run_analysis
        
        log = logging.getLogger(__name__)
        log.info("Direct run_analysis endpoint called")
        
        # Get request data
        data = request.get_json() or {}
        analysis_type = data.get('test') or data.get('analysis_type')
        dv = data.get('dv')
        variables = data.get('variables', {})
        filters = data.get('filters', {})
        
        # Log the request details
        log.info(f"Analysis request: type={analysis_type}, dv={dv}, variables={variables}, filters={filters}")
        
        if not analysis_type:
            return jsonify({
                'ok': False,
                'error': 'Missing analysis type',
                'message': 'Please specify a test type'
            }), 400
            
        if not dv and not variables.get('variable'):
            return jsonify({
                'ok': False,
                'error': 'Missing dependent variable',
                'message': 'Please specify a dependent variable'
            }), 400
        
        # Use dv if provided, otherwise fall back to variables.variable
        variable = dv or variables.get('variable')
        secondary_variable = variables.get('secondary_variable')
        
        # Run the analysis using our new module
        result = run_analysis(
            test_type=analysis_type,
            variable=variable,
            filters=filters,
            secondary_variable=secondary_variable
        )
        
        # Add analysis metadata
        result['analysis_type'] = analysis_type.capitalize()
        result['variable'] = variable
        if secondary_variable:
            result['secondary_variable'] = secondary_variable
        
        return jsonify(result)
            
    except Exception as e:
        import traceback
        print(f"Error in direct_run_analysis: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'ok': False,
            'error': 'Server error',
            'message': f'An error occurred while processing the analysis: {str(e)}'
        }), 500

@app.route('/analytics/data.csv')
def analytics_csv_export():
    """Export analytics data as CSV"""
    try:
        from flask import request, Response
        import csv
        import io
        import logging
        from datetime import datetime
        from utils.csv_loader import load_csv_files, filter_data
        
        log = logging.getLogger(__name__)
        log.info("Analytics CSV export endpoint called")
        
        # Get query parameters
        test = request.args.get('test', '')
        dv = request.args.get('dv', '')
        
        # Build filters from query parameters
        filters = {}
        
        # Gender filter
        gender = request.args.get('gender', '')
        if gender and gender.lower() != 'all':
            filters['gender'] = gender
        
        # Age range filters
        age_min = request.args.get('age_min', '')
        if age_min:
            filters['age_min'] = age_min
            
        age_max = request.args.get('age_max', '')
        if age_max:
            filters['age_max'] = age_max
        
        # Date range filters
        date_from = request.args.get('date_from', '')
        if date_from:
            filters['date_from'] = date_from
            
        date_to = request.args.get('date_to', '')
        if date_to:
            filters['date_to'] = date_to
        
        # Log the request
        log.info(f"CSV export request: test={test}, dv={dv}, filters={filters}")
        
        # Load and filter data
        data = load_csv_files()
        if filters:
            data = filter_data(data, filters)
        
        if not data:
            log.warning("No data found matching the specified filters")
            return "No data found matching the specified filters", 404
        
        # Create a string buffer for the CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Get all unique keys across all dictionaries
        all_keys = set()
        for row in data:
            all_keys.update(row.keys())
        
        # Write headers - sort them for consistency
        writer.writerow(sorted(all_keys))
        
        # Write data rows
        for row in data:
            # Create a row with all columns, using empty string for missing values
            csv_row = [row.get(key, '') for key in sorted(all_keys)]
            writer.writerow(csv_row)
        
        # Prepare the response
        output.seek(0)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"face_analysis_{timestamp}.csv"
        
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
        
    except Exception as e:
        log.error(f"Error in analytics_csv_export: {str(e)}", exc_info=True)
        return f"Error generating CSV: {str(e)}", 500

@app.route('/analytics/report.html')
def analytics_html_report():
    """Generate HTML report for analytics"""
    try:
        from flask import request, Response
        import logging
        from utils.report_generator import generate_html_report
        
        log = logging.getLogger(__name__)
        log.info("Analytics HTML report endpoint called")
        
        # Get query parameters
        test = request.args.get('test', '')
        dv = request.args.get('dv', '')
        
        # Build filters from query parameters
        filters = {}
        
        # Gender filter
        gender = request.args.get('gender', '')
        if gender and gender.lower() != 'all':
            filters['gender'] = gender
        
        # Age range filters
        age_min = request.args.get('age_min', '')
        if age_min:
            filters['age_min'] = age_min
            
        age_max = request.args.get('age_max', '')
        if age_max:
            filters['age_max'] = age_max
        
        # Date range filters
        date_from = request.args.get('date_from', '')
        if date_from:
            filters['date_from'] = date_from
            
        date_to = request.args.get('date_to', '')
        if date_to:
            filters['date_to'] = date_to
            
        # Secondary variable (for correlation)
        secondary_variable = request.args.get('secondary_variable', None)
        
        # Log the request
        log.info(f"HTML report request: test={test}, dv={dv}, filters={filters}, secondary_variable={secondary_variable}")
        
        if not test or not dv:
            return "Missing required parameters: test and dv", 400
        
        # Generate HTML report
        html_content = generate_html_report(test, dv, filters, secondary_variable)
        
        return html_content
        
    except Exception as e:
        log.error(f"Error in analytics_html_report: {str(e)}", exc_info=True)
        return f"Error generating HTML report: {str(e)}", 500

@app.route('/analytics/report.pdf')
def analytics_pdf_report():
    """Generate PDF report for analytics"""
    try:
        from flask import request, Response
        import logging
        from utils.report_generator import generate_pdf_report
        
        log = logging.getLogger(__name__)
        log.info("Analytics PDF report endpoint called")
        
        # Get query parameters
        test = request.args.get('test', '')
        dv = request.args.get('dv', '')
        
        # Build filters from query parameters
        filters = {}
        
        # Gender filter
        gender = request.args.get('gender', '')
        if gender and gender.lower() != 'all':
            filters['gender'] = gender
        
        # Age range filters
        age_min = request.args.get('age_min', '')
        if age_min:
            filters['age_min'] = age_min
            
        age_max = request.args.get('age_max', '')
        if age_max:
            filters['age_max'] = age_max
        
        # Date range filters
        date_from = request.args.get('date_from', '')
        if date_from:
            filters['date_from'] = date_from
            
        date_to = request.args.get('date_to', '')
        if date_to:
            filters['date_to'] = date_to
            
        # Secondary variable (for correlation)
        secondary_variable = request.args.get('secondary_variable', None)
        
        # Log the request
        log.info(f"PDF report request: test={test}, dv={dv}, filters={filters}, secondary_variable={secondary_variable}")
        
        if not test or not dv:
            return "Missing required parameters: test and dv", 400
        
        # Generate PDF report
        pdf_content = generate_pdf_report(test, dv, filters, secondary_variable)
        
        if not pdf_content:
            return "Error generating PDF report", 500
        
        # Prepare the response
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"face_analysis_report_{timestamp}.pdf"
        
        return Response(
            pdf_content,
            mimetype="application/pdf",
            headers={"Content-Disposition": f"attachment;filename={filename}"}
        )
        
    except Exception as e:
        log.error(f"Error in analytics_pdf_report: {str(e)}", exc_info=True)
        return f"Error generating PDF report: {str(e)}", 500

# This is the standard WSGI application variable that Gunicorn looks for
application = app

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=True)

"""
Face Viewer Dashboard - Pandas-Free App
This file provides a minimal Flask app without pandas dependencies.
"""
import os
import json
import random
import csv
import io
from datetime import datetime
from flask import Flask, render_template, jsonify, send_from_directory, redirect, url_for, request, Response, send_file

# Import analytics modules
from analytics.spss_export import SPSSExporter
from analytics.r_integration import RAnalytics

# Create a Flask app
app = Flask(__name__)

# Configure the app
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['DATA_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

# Ensure directories exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['DATA_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Mock data generation functions
def generate_mock_data():
    """Generate mock data for dashboard demonstration"""
    # Mock summary statistics
    summary_stats = {
        'total_participants': random.randint(30, 100),
        'total_responses': random.randint(500, 2000),
        'avg_trust_rating': round(random.uniform(3.5, 5.5), 2),
        'std_trust_rating': round(random.uniform(0.8, 1.5), 2),
        'trust_by_version': {
            'Full Face': round(random.uniform(3.8, 5.8), 2),
            'Left Half': round(random.uniform(3.2, 5.2), 2),
            'Right Half': round(random.uniform(3.5, 5.5), 2)
        }
    }
    
    # Mock participant data
    participants = {}
    for i in range(1, 11):  # Generate 10 mock participants
        pid = f'P{i:03d}'
        participants[pid] = {
            'csv': random.choice([True, True, False]),  # More likely to have CSV
            'xlsx': random.choice([True, False, False]),  # Less likely to have Excel
            'enc': random.choice([False, False, True])   # Rare to have encrypted
        }
    
    # Mock face analysis results
    face_analysis = {
        'symmetry_scores': [round(random.uniform(0.7, 0.98), 2) for _ in range(30)],
        'masculinity_scores': {
            'left': [round(random.uniform(0.3, 0.8), 2) for _ in range(30)],
            'right': [round(random.uniform(0.3, 0.8), 2) for _ in range(30)]
        },
        'trust_ratings': [random.randint(1, 7) for _ in range(100)]
    }
    
    return {
        'summary_stats': summary_stats,
        'participants': participants,
        'face_analysis': face_analysis
    }

# Define routes
@app.route('/')
def index():
    return render_template('index.html', title='Face Viewer Dashboard')

@app.route('/dashboard')
def dashboard():
    # Generate mock data for demonstration
    data = generate_mock_data()
    
    # Prepare chart data
    trust_distribution = {
        'labels': ['1', '2', '3', '4', '5', '6', '7'],
        'datasets': [{
            'label': 'Trust Ratings',
            'data': [data['face_analysis']['trust_ratings'].count(i) for i in range(1, 8)],
            'backgroundColor': 'rgba(255, 193, 7, 0.5)',
            'borderColor': 'rgba(255, 193, 7, 1)',
            'borderWidth': 1
        }]
    }
    
    symmetry_data = {
        'labels': [f'Face {i+1}' for i in range(len(data['face_analysis']['symmetry_scores']))],
        'datasets': [{
            'label': 'Symmetry Score',
            'data': data['face_analysis']['symmetry_scores'],
            'backgroundColor': 'rgba(13, 110, 253, 0.5)',
            'borderColor': 'rgba(13, 110, 253, 1)',
            'borderWidth': 1
        }]
    }
    
    masculinity_data = {
        'labels': [f'Face {i+1}' for i in range(len(data['face_analysis']['masculinity_scores']['left']))],
        'datasets': [
            {
                'label': 'Left Side',
                'data': data['face_analysis']['masculinity_scores']['left'],
                'backgroundColor': 'rgba(220, 53, 69, 0.5)',
                'borderColor': 'rgba(220, 53, 69, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Right Side',
                'data': data['face_analysis']['masculinity_scores']['right'],
                'backgroundColor': 'rgba(25, 135, 84, 0.5)',
                'borderColor': 'rgba(25, 135, 84, 1)',
                'borderWidth': 1
            }
        ]
    }
    
    return render_template(
        'dashboard_simple.html', 
        title='Dashboard',
        summary_stats=data['summary_stats'],
        participants=data['participants'],
        trust_distribution=json.dumps(trust_distribution),
        symmetry_data=json.dumps(symmetry_data),
        masculinity_data=json.dumps(masculinity_data)
    )

@app.route('/health')
@app.route('/healthz')
def health():
    return jsonify({"status": "healthy", "message": "Face Viewer Dashboard is running without pandas"})

# Analytics routes
@app.route('/analytics')
def analytics():
    """Analytics dashboard page"""
    # Get available analyses from R integration
    r_analytics = RAnalytics()
    available_analyses = r_analytics.available_analyses()
    
    # Generate mock data for demonstration
    data = generate_mock_data()
    
    # Get column names from mock data
    columns = [
        {'id': 'participant_id', 'name': 'Participant ID'},
        {'id': 'age', 'name': 'Age'},
        {'id': 'gender', 'name': 'Gender'},
        {'id': 'trust_rating', 'name': 'Trust Rating'},
        {'id': 'symmetry_score', 'name': 'Symmetry Score'},
        {'id': 'masculinity_left', 'name': 'Masculinity (Left)'},
        {'id': 'masculinity_right', 'name': 'Masculinity (Right)'},
        {'id': 'completion_time', 'name': 'Completion Time'}
    ]
    
    return render_template(
        'analytics.html',
        title='Analytics',
        available_analyses=available_analyses,
        columns=columns,
        summary_stats=data['summary_stats']
    )

@app.route('/api/run_analysis', methods=['POST'])
def run_analysis():
    """API endpoint to run R analysis"""
    # Get analysis parameters from request
    analysis_type = request.json.get('analysis_type')
    variables = request.json.get('variables', [])
    
    # Generate mock data for demonstration
    data = generate_mock_data()
    
    # Create mock tabular data
    mock_data = {
        'columns': ['participant_id', 'age', 'gender', 'trust_rating', 'symmetry_score', 
                   'masculinity_left', 'masculinity_right', 'completion_time'],
        'rows': []
    }
    
    # Generate 30 mock participants
    for i in range(1, 31):
        pid = f'P{i:03d}'
        age = random.randint(18, 65)
        gender = random.choice(['M', 'F', 'Other'])
        trust_rating = random.randint(1, 7)
        symmetry_score = round(random.uniform(0.7, 0.98), 2)
        masculinity_left = round(random.uniform(0.3, 0.8), 2)
        masculinity_right = round(random.uniform(0.3, 0.8), 2)
        completion_time = random.randint(60, 300)
        
        mock_data['rows'].append([
            pid, age, gender, trust_rating, symmetry_score, 
            masculinity_left, masculinity_right, completion_time
        ])
    
    # Run analysis
    r_analytics = RAnalytics()
    results = r_analytics.run_analysis(analysis_type, mock_data, variables)
    
    return jsonify(results)

@app.route('/api/export_spss', methods=['POST'])
def export_spss():
    """API endpoint to export data to SPSS format"""
    # Get export parameters from request
    include_labels = request.json.get('include_labels', True)
    
    # Generate mock data for demonstration
    mock_data = {
        'columns': ['participant_id', 'age', 'gender', 'trust_rating', 'symmetry_score', 
                   'masculinity_left', 'masculinity_right', 'completion_time'],
        'rows': []
    }
    
    # Generate 30 mock participants
    for i in range(1, 31):
        pid = f'P{i:03d}'
        age = random.randint(18, 65)
        gender = random.choice(['M', 'F', 'Other'])
        trust_rating = random.randint(1, 7)
        symmetry_score = round(random.uniform(0.7, 0.98), 2)
        masculinity_left = round(random.uniform(0.3, 0.8), 2)
        masculinity_right = round(random.uniform(0.3, 0.8), 2)
        completion_time = random.randint(60, 300)
        
        mock_data['rows'].append([
            pid, age, gender, trust_rating, symmetry_score, 
            masculinity_left, masculinity_right, completion_time
        ])
    
    # Export to SPSS format
    spss_exporter = SPSSExporter()
    output = spss_exporter.generate_sav_file(mock_data)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'face_data_export_{timestamp}.sav'
    
    # Return file for download
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/octet-stream'
    )

@app.route('/api/export_csv', methods=['POST'])
def export_csv():
    """API endpoint to export data to CSV format"""
    # Generate mock data for demonstration
    mock_data = {
        'columns': ['participant_id', 'age', 'gender', 'trust_rating', 'symmetry_score', 
                   'masculinity_left', 'masculinity_right', 'completion_time'],
        'rows': []
    }
    
    # Generate 30 mock participants
    for i in range(1, 31):
        pid = f'P{i:03d}'
        age = random.randint(18, 65)
        gender = random.choice(['M', 'F', 'Other'])
        trust_rating = random.randint(1, 7)
        symmetry_score = round(random.uniform(0.7, 0.98), 2)
        masculinity_left = round(random.uniform(0.3, 0.8), 2)
        masculinity_right = round(random.uniform(0.3, 0.8), 2)
        completion_time = random.randint(60, 300)
        
        mock_data['rows'].append([
            pid, age, gender, trust_rating, symmetry_score, 
            masculinity_left, masculinity_right, completion_time
        ])
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(mock_data['columns'])
    
    # Write data rows
    for row in mock_data['rows']:
        writer.writerow(row)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'face_data_export_{timestamp}.csv'
    
    # Return CSV for download
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment;filename={filename}'}
    )

# This ensures that if anything imports from this file, it gets the pandas-free version
print("Using completely pandas-free app")

if __name__ == '__main__':
    app.run(debug=True)

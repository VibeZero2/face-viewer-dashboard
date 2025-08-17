"""
Face Viewer Dashboard - Simplified App
No login required, minimal dependencies
"""
from flask import Flask, redirect, render_template, url_for, jsonify

# Initialize Flask app
app = Flask(__name__)

# No dashboard integration - direct implementation

# Root route redirects to dashboard
@app.route('/')
def index():
    return redirect('/dashboard')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    # Create empty stats dictionary with default values to prevent template errors
    stats = {
        'total_participants': 0,
        'total_responses': 0,
        'trust_mean': 0,
        'trust_std': 0,
        'trust_by_version': {
            'Full_Face': 0,
            'Left_Half': 0,
            'Right_Half': 0
        },
        'trust_distribution': {}
    }
    
    # Create empty chart data structures
    trust_ratings_chart = {
        'labels': ['1', '2', '3', '4', '5', '6', '7'],
        'datasets': [{'label': 'Trust Ratings', 'data': [0, 0, 0, 0, 0, 0, 0], 'backgroundColor': '#f9e076'}]
    }
    
    symmetry_chart = {
        'labels': ['No Data'],
        'datasets': [{'label': 'Symmetry Score', 'data': [0], 'borderColor': '#8bb9ff', 'backgroundColor': 'rgba(139, 185, 255, 0.2)', 'tension': 0.1}]
    }
    
    masculinity_chart = {
        'labels': ['Full Face', 'Left Half', 'Right Half'],
        'datasets': [{'label': 'Avg. Masculinity Score', 'data': [0, 0, 0], 'backgroundColor': '#6EC6CA'}]
    }
    
    femininity_chart = {
        'labels': ['Full Face', 'Left Half', 'Right Half'],
        'datasets': [{'label': 'Avg. Femininity Score', 'data': [0, 0, 0], 'backgroundColor': '#F78CA2'}]
    }
    
    # Serialize all chart data to JSON
    import json
    trust_ratings_json = json.dumps(trust_ratings_chart)
    symmetry_chart_json = json.dumps(symmetry_chart)
    masculinity_chart_json = json.dumps(masculinity_chart)
    femininity_chart_json = json.dumps(femininity_chart)
    trust_hist_json = json.dumps({str(i): 0 for i in range(1, 8)})
    avg_symmetry_json = json.dumps({})
    avg_masc_json = json.dumps({'Full Face': 0, 'Left Half': 0, 'Right Half': 0})
    avg_fem_json = json.dumps({'Full Face': 0, 'Left Half': 0, 'Right Half': 0})
    
    # Create empty placeholder data for Plotly charts
    trust_distribution = {
        'data': [
            {
                'type': 'bar',
                'x': ['Full Face', 'Left Half', 'Right Half'],
                'y': [0, 0, 0],
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
                'y': [],
                'name': 'Full Face',
                'marker': {'color': '#3366cc'}
            },
            {
                'type': 'box',
                'y': [],
                'name': 'Left Half',
                'marker': {'color': '#dc3912'}
            },
            {
                'type': 'box',
                'y': [],
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
                'x': [],
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
    
    trust_distribution_json = json.dumps(trust_distribution)
    trust_boxplot_json = json.dumps(trust_boxplot)
    trust_histogram_json = json.dumps(trust_histogram)
    
    return render_template('dashboard.html', 
                           title='Face Viewer Dashboard',
                           stats=stats, 
                           summary_stats=stats,
                           participants=[],
                           responses=[],
                           total_responses=0,
                           total_participants=0,
                           avg_trust=0,
                           std_trust=0,
                           recent_activity=[],
                           # JSON serialized chart data for JavaScript
                           trust_ratings_json=trust_ratings_json,
                           symmetry_chart_json=symmetry_chart_json,
                           masculinity_chart_json=masculinity_chart_json,
                           femininity_chart_json=femininity_chart_json,
                           trust_distribution_json=trust_distribution_json,
                           trust_boxplot_json=trust_boxplot_json,
                           trust_histogram_json=trust_histogram_json,
                           # Raw data for additional processing
                           trust_hist=trust_hist_json,
                           avg_symmetry=avg_symmetry_json,
                           avg_masc=avg_masc_json,
                           avg_fem=avg_fem_json,
                           error_message=None,
                           use_demo_data=False,
                           data_file_exists=False)

# Health check
@app.route('/health')
def health():
    return {"status": "healthy"}

# This is the standard WSGI application variable that Gunicorn looks for
application = app

if __name__ == '__main__':
    print("Starting server on port 8080...")
    print("Access the dashboard at: http://localhost:8080")
    app.run(host='localhost', port=8080)

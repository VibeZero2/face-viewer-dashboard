import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, send_file
import tempfile
import glob
import shutil
# Login imports removed
# from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
# from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import io
import zipfile
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('DASHBOARD_SECRET_KEY', os.urandom(24).hex())
app.config['FERNET_KEY'] = os.getenv('FERNET_KEY')

# Login functionality disabled
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

# Path constants
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv('FACE_VIEWER_DATA_DIR', BASE_DIR / 'data'))
UPLOAD_DIR = BASE_DIR / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize Fernet for decryption
fernet = Fernet(app.config['FERNET_KEY'].encode())

# Authentication removed - public access only
# Routes for dashboard access

# Helper functions for data processing
def get_participant_files():
    """Get all participant data files."""
    csv_files = list(DATA_DIR.glob('*.csv'))
    xlsx_files = list(DATA_DIR.glob('*.xlsx'))
    enc_files = list(DATA_DIR.glob('*.csv.enc'))
    
    participants = {}
    for file in csv_files:
        pid = file.stem
        if pid not in participants:
            participants[pid] = {'csv': None, 'xlsx': None, 'enc': None}
        participants[pid]['csv'] = file
    
    for file in xlsx_files:
        pid = file.stem
        if pid not in participants:
            participants[pid] = {'csv': None, 'xlsx': None, 'enc': None}
        participants[pid]['xlsx'] = file
    
    for file in enc_files:
        pid = file.stem.replace('.csv', '')
        if pid not in participants:
            participants[pid] = {'csv': None, 'xlsx': None, 'enc': None}
        participants[pid]['enc'] = file
    
    return participants

def decrypt_file(file_path):
    """Decrypt an encrypted CSV file."""
    with open(file_path, 'rb') as f:
        encrypted_data = f.read()
    
    decrypted_data = fernet.decrypt(encrypted_data).decode('utf-8')
    return decrypted_data

def load_participant_data(pid):
    """Load participant data from CSV file."""
    participants = get_participant_files()
    
    if pid not in participants:
        return None
    
    if participants[pid]['csv']:
        return pd.read_csv(participants[pid]['csv'])
    elif participants[pid]['enc']:
        decrypted_data = decrypt_file(participants[pid]['enc'])
        return pd.read_csv(io.StringIO(decrypted_data))
    else:
        return None

def get_all_participant_data():
    """Load all participant data and combine into a single DataFrame."""
    participants = get_participant_files()
    all_data = []
    
    for pid in participants:
        data = load_participant_data(pid)
        if data is not None:
            all_data.append(data)
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

def get_face_order_data():
    """Extract face order data from all participants."""
    participants = get_participant_files()
    face_orders = {}
    
    for pid in participants:
        data = load_participant_data(pid)
        if data is not None:
            # Find face order rows
            order_rows = data[data['version'] == 'order_index']
            if not order_rows.empty:
                face_orders[pid] = order_rows[['face_id', 'order_presented']].rename(
                    columns={'order_presented': 'position'}).sort_values('position')
    
    return face_orders

def generate_summary_stats():
    """Generate summary statistics for all participants."""
    all_data = get_all_participant_data()
    
    if all_data.empty:
        return None
    
    # Filter for actual ratings (not metadata)
    ratings_data = all_data[all_data['version'].isin(['left', 'right', 'full'])]
    
    # Convert trust_rating to numeric
    ratings_data['trust_rating'] = pd.to_numeric(ratings_data['trust_rating'], errors='coerce')
    
    # Summary statistics
    summary = {
        'total_participants': ratings_data['pid'].nunique(),
        'total_responses': len(ratings_data),
        'avg_trust_rating': ratings_data['trust_rating'].mean(),
        'std_trust_rating': ratings_data['trust_rating'].std(),
        'trust_by_version': ratings_data.groupby('version')['trust_rating'].mean().to_dict(),
        'masc_choice_counts': ratings_data['masc_choice'].value_counts().to_dict(),
        'fem_choice_counts': ratings_data['fem_choice'].value_counts().to_dict(),
    }
    
    return summary

def generate_trust_histogram():
    """Generate histogram of trust ratings."""
    all_data = get_all_participant_data()
    
    if all_data.empty:
        return None
    
    # Filter for actual ratings (not metadata)
    ratings_data = all_data[all_data['version'].isin(['left', 'right', 'full'])]
    
    # Convert trust_rating to numeric
    ratings_data['trust_rating'] = pd.to_numeric(ratings_data['trust_rating'], errors='coerce')
    
    # Create histogram
    fig = px.histogram(
        ratings_data, 
        x='trust_rating',
        color='version',
        barmode='group',
        title='Distribution of Trust Ratings by Face Version',
        labels={'trust_rating': 'Trust Rating', 'version': 'Face Version'},
        category_orders={'version': ['left', 'right', 'full']}
    )
    
    return fig.to_json()

def generate_trust_boxplot():
    """Generate boxplot of trust ratings by version."""
    all_data = get_all_participant_data()
    
    if all_data.empty:
        return None
    
    # Filter for actual ratings (not metadata)
    ratings_data = all_data[all_data['version'].isin(['left', 'right', 'full'])]
    
    # Convert trust_rating to numeric
    ratings_data['trust_rating'] = pd.to_numeric(ratings_data['trust_rating'], errors='coerce')
    
    # Create boxplot
    fig = px.box(
        ratings_data, 
        x='version', 
        y='trust_rating',
        title='Trust Ratings by Face Version',
        labels={'trust_rating': 'Trust Rating', 'version': 'Face Version'},
        category_orders={'version': ['left', 'right', 'full']}
    )
    
    return fig.to_json()

# Dashboard routes
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    participants = get_participant_files()
    summary_stats = generate_summary_stats()
    trust_histogram = generate_trust_histogram()
    trust_boxplot = generate_trust_boxplot()
    
    return render_template(
        'dashboard.html',
        participants=participants,
        summary_stats=summary_stats,
        trust_histogram=trust_histogram,
        trust_boxplot=trust_boxplot
    )

@app.route('/participant/<pid>')
def participant_detail(pid):
    data = load_participant_data(pid)
    
    if data is None:
        flash(f'No data found for participant {pid}')
        return redirect(url_for('dashboard'))
    
    # Extract face order if available
    face_order = None
    order_rows = data[data['version'] == 'order_index']
    if not order_rows.empty:
        face_order = order_rows[['face_id', 'order_presented']].rename(
            columns={'order_presented': 'position'}).sort_values('position')
    
    # Extract session duration if available
    duration = None
    duration_row = data[(data['version'] == 'duration') & (data['face_id'] == 'metadata')]
    if not duration_row.empty:
        duration_seconds = int(duration_row['order_presented'].iloc[0])
        duration = f"{duration_seconds // 60} minutes, {duration_seconds % 60} seconds"
    
    # Filter for actual ratings (not metadata)
    ratings_data = data[data['version'].isin(['left', 'right', 'full'])]
    
    # Convert trust_rating to numeric
    ratings_data['trust_rating'] = pd.to_numeric(ratings_data['trust_rating'], errors='coerce')
    
    # Create trust rating histogram
    trust_hist = px.histogram(
        ratings_data, 
        x='trust_rating',
        color='version',
        barmode='group',
        title=f'Trust Ratings Distribution for Participant {pid}',
        labels={'trust_rating': 'Trust Rating', 'version': 'Face Version'}
    ).to_json()
    
    # Create trust by face_id plot
    trust_by_face = px.bar(
        ratings_data.groupby(['face_id', 'version'])['trust_rating'].mean().reset_index(),
        x='face_id',
        y='trust_rating',
        color='version',
        barmode='group',
        title=f'Average Trust Rating by Face ID for Participant {pid}',
        labels={'trust_rating': 'Avg Trust Rating', 'face_id': 'Face ID', 'version': 'Face Version'}
    ).to_json()
    
    return render_template(
        'participant_detail.html',
        pid=pid,
        data=data.to_dict('records'),
        face_order=face_order.to_dict('records') if face_order is not None else None,
        duration=duration,
        trust_hist=trust_hist,
        trust_by_face=trust_by_face
    )

@app.route('/download/<pid>')
def download_participant(pid):
    participants = get_participant_files()
    
    if pid not in participants:
        flash(f'No data found for participant {pid}')
        return redirect(url_for('dashboard'))
    
    if participants[pid]['xlsx']:
        return send_file(participants[pid]['xlsx'], as_attachment=True)
    elif participants[pid]['csv']:
        return send_file(participants[pid]['csv'], as_attachment=True)
    else:
        flash(f'No downloadable file found for participant {pid}')
        return redirect(url_for('dashboard'))

@app.route('/download-all')
def download_all():
    """Download all participant data as a ZIP file"""
    # Create a temporary directory to store files for zipping
    temp_dir = tempfile.mkdtemp()
    try:
        # Copy all participant data files to the temp directory
        for file_path in glob.glob(os.path.join(DATA_DIR, '*.csv')):
            shutil.copy2(file_path, temp_dir)
        
        # Create a ZIP file
        zip_path = os.path.join(temp_dir, 'all_participant_data.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file_path in glob.glob(os.path.join(temp_dir, '*.csv')):
                zipf.write(file_path, os.path.basename(file_path))
        
        # Send the ZIP file
        return send_file(zip_path, as_attachment=True, download_name='all_participant_data.zip')
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)

@app.route('/check_abandoned_sessions')
# # @login_required - removed - removed
def check_abandoned_sessions():
    """Check for abandoned sessions by calling the Face Half Viewer backend API"""
    # Get the Face Half Viewer backend URL from environment or use default
    face_viewer_url = os.environ.get('FACE_VIEWER_BACKEND_URL', 'http://localhost:5000')
    admin_api_key = os.environ.get('ADMIN_API_KEY')
    
    if not admin_api_key:
        flash('ADMIN_API_KEY environment variable is not set. Cannot check abandoned sessions.', 'danger')
        return redirect(url_for('dashboard'))
    
    try:
        # Call the Face Half Viewer backend API to check abandoned sessions
        response = requests.get(
            f"{face_viewer_url}/admin/check-abandoned-sessions",
            headers={'Authorization': f'Bearer {admin_api_key}'}
        )
        
        if response.status_code == 200:
            result = response.json()
            abandoned_count = result.get('abandoned_count', 0)
            flash(f'Successfully checked for abandoned sessions. Found {abandoned_count} abandoned sessions.', 'success')
        else:
            flash(f'Failed to check abandoned sessions. Status code: {response.status_code}', 'danger')
    except requests.RequestException as e:
        flash(f'Error connecting to Face Half Viewer backend: {str(e)}', 'danger')
    
    return redirect(url_for('dashboard'))

@app.route('/r-analysis')
def r_analysis():
    """Run R analysis on the data."""
    try:
        import rpy2.robjects as robjects
        from rpy2.robjects import pandas2ri
        pandas2ri.activate()
        
        # Get all participant data
        all_data = get_all_participant_data()
        
        if all_data.empty:
            flash('No data available for analysis')
            return redirect(url_for('dashboard'))
        
        # Filter for actual ratings (not metadata)
        ratings_data = all_data[all_data['version'].isin(['left', 'right', 'full'])]
        
        # Convert trust_rating to numeric
        ratings_data['trust_rating'] = pd.to_numeric(ratings_data['trust_rating'], errors='coerce')
        
        # Convert to R dataframe
        r_df = pandas2ri.py2rpy(ratings_data)
        
        # Define R script
        r_script = """
        library(lme4)
        library(ggplot2)
        
        # Run mixed-effects model
        model <- lmer(trust_rating ~ version + (1|pid) + (1|face_id), data=df)
        
        # Get model summary
        summary_model <- summary(model)
        
        # Create a plot
        p <- ggplot(df, aes(x=version, y=trust_rating, fill=version)) +
             geom_boxplot() +
             theme_minimal() +
             labs(title="Trust Ratings by Face Version",
                  x="Face Version", y="Trust Rating")
        
        # Save plot to a temporary file
        temp_plot <- tempfile(fileext=".png")
        ggsave(temp_plot, p, width=8, height=6)
        
        # Return results as a list
        list(
            coefficients=summary_model$coefficients,
            plot_path=temp_plot
        )
        """
        
        # Run R script
        robjects.globalenv['df'] = r_df
        result = robjects.r(r_script)
        
        # Extract results
        coefficients = pandas2ri.rpy2py(result[0])
        plot_path = result[1][0]
        
        # Copy plot to static directory
        plot_dest = BASE_DIR / 'static' / 'r_plot.png'
        shutil.copy(plot_path, plot_dest)
        
        return render_template(
            'r_analysis.html',
            coefficients=coefficients.to_dict('records'),
            plot_url=url_for('static', filename='r_plot.png')
        )
    
    except ImportError:
        flash('R integration is not available. Please install rpy2 and R.')
        return redirect(url_for('dashboard'))
    except Exception as e:
        flash(f'Error running R analysis: {str(e)}')
        return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)

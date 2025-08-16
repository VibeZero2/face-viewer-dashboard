"""
Face Viewer Dashboard - Main App
This is the main entry point for the Flask application.
"""
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

# Path constants
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv('FACE_VIEWER_DATA_DIR', BASE_DIR / 'data'))
UPLOAD_DIR = BASE_DIR / 'uploads'
UPLOAD_DIR.mkdir(exist_ok=True)

# Initialize Fernet for decryption
fernet = Fernet(app.config['FERNET_KEY'].encode()) if app.config.get('FERNET_KEY') else None

# Import all the necessary functions from app_with_pandas
from app_with_pandas import get_participant_files, load_participant_data, generate_summary_stats
from app_with_pandas import create_age_distribution_plot, create_gender_distribution_plot
from app_with_pandas import create_test_type_distribution_plot, create_completion_time_plot

# Root route redirects to dashboard
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

# Dashboard route
@app.route('/dashboard')
def dashboard():
    participants = get_participant_files()
    
    # Generate summary statistics
    summary = generate_summary_stats(participants)
    
    # Create plots
    age_plot = create_age_distribution_plot(participants)
    gender_plot = create_gender_distribution_plot(participants)
    test_type_plot = create_test_type_distribution_plot(participants)
    completion_time_plot = create_completion_time_plot(participants)
    
    return render_template('dashboard.html', 
                          participants=participants,
                          summary=summary,
                          age_plot=age_plot,
                          gender_plot=gender_plot,
                          test_type_plot=test_type_plot,
                          completion_time_plot=completion_time_plot)

# Participant detail route
@app.route('/participant/<participant_id>')
def participant_detail(participant_id):
    participants = get_participant_files()
    if participant_id not in participants:
        flash('Participant not found', 'danger')
        return redirect(url_for('dashboard'))
    
    participant = participants[participant_id]
    data = load_participant_data(participant['file_path'])
    
    return render_template('participant_detail.html', 
                          participant=participant,
                          data=data)

# Analytics route
@app.route('/r-analysis')
def r_analysis():
    return render_template('r_analysis.html')

if __name__ == '__main__':
    app.run(debug=True)

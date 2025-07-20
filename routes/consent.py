"""
Consent routes for Face Viewer Dashboard
Handles participant consent and ID management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import os
import pandas as pd

# Create blueprint
consent_bp = Blueprint('consent', __name__)

@consent_bp.route('/consent')
def consent():
    """Display the consent form"""
    return render_template('consent.html')

@consent_bp.route('/submit_consent', methods=['POST'])
def submit_consent():
    """Process consent form submission"""
    participant_id = request.form.get('participantId')
    
    if not participant_id:
        flash("Error: No participant ID provided.", "danger")
        return redirect(url_for('consent.consent'))
    
    # Store participant ID in session
    session['participant_id'] = participant_id
    
    # Record consent in database
    try:
        # Ensure data directory exists
        data_dir = os.path.join(os.getcwd(), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Create or append to consent log
        consent_log_path = os.path.join(data_dir, 'consent_log.csv')
        
        # Prepare data
        consent_data = {
            'pid': [participant_id],
            'timestamp': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'ip_hash': [hash(request.remote_addr)],  # Hashed for privacy
            'user_agent': [request.user_agent.string]
        }
        
        # Create DataFrame
        consent_df = pd.DataFrame(consent_data)
        
        # Check if file exists
        if os.path.exists(consent_log_path):
            # Append to existing file
            existing_df = pd.read_csv(consent_log_path)
            updated_df = pd.concat([existing_df, consent_df], ignore_index=True)
            updated_df.to_csv(consent_log_path, index=False)
        else:
            # Create new file
            consent_df.to_csv(consent_log_path, index=False)
        
        # Redirect to the study start page
        return redirect(url_for('study.start'))
        
    except Exception as e:
        print(f"Error recording consent: {e}")
        flash("There was an error processing your consent. Please try again.", "danger")
        return redirect(url_for('consent.consent'))

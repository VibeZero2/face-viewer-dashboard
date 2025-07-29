import os
import csv
import random
from datetime import datetime, timedelta
from flask import Blueprint, request, redirect, url_for, flash, current_app, jsonify
from werkzeug.utils import secure_filename

admin_tools = Blueprint('admin_tools', __name__)

UPLOAD_FOLDER = 'data/responses'
ALLOWED_EXTENSIONS = {'csv'}

def allowed_file(filename):
    """Check if file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@admin_tools.route('/admin/upload', methods=['POST'])
def upload_participant():
    """Upload a participant CSV file"""
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('dashboard.dashboard'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('dashboard.dashboard'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        
        # Ensure upload directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(save_path)
        flash(f'Participant file "{filename}" uploaded successfully')
    else:
        flash('Invalid file type. Please upload a CSV file.')
    
    return redirect(url_for('dashboard.dashboard'))

@admin_tools.route('/admin/delete/<filename>', methods=['POST'])
def delete_participant(filename):
    """Delete a participant CSV file"""
    try:
        # Secure the filename to prevent path traversal
        filename = secure_filename(filename)
        target_file = os.path.join(UPLOAD_FOLDER, filename)
        
        if os.path.exists(target_file):
            os.remove(target_file)
            flash(f'Participant file "{filename}" deleted successfully')
        else:
            flash(f'Participant file "{filename}" not found')
    except Exception as e:
        flash(f'Error deleting {filename}: {str(e)}')
    
    return redirect(url_for('dashboard.dashboard'))

@admin_tools.route('/admin/clear-all', methods=['POST'])
def clear_all_data():
    """Clear all participant data files"""
    try:
        # Get confirmation from form
        confirmation = request.form.get('confirmation', '')
        if confirmation != 'DELETE_ALL_DATA':
            flash('Invalid confirmation code. Data not deleted.')
            return redirect(url_for('dashboard.dashboard'))
        
        # Delete all files in the responses directory
        count = 0
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('.csv'):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                os.remove(file_path)
                count += 1
        
        flash(f'Successfully deleted {count} participant data files')
    except Exception as e:
        flash(f'Error clearing data: {str(e)}')
    
    return redirect(url_for('dashboard.dashboard'))

@admin_tools.route('/admin/generate-test-data', methods=['GET', 'POST'])
def generate_test_data():
    """Generate test participant data files on the server"""
    # Check for admin secret key if provided as URL parameter
    admin_secret = os.getenv('ADMIN_SECRET')
    if admin_secret and request.args.get('key') != admin_secret:
        return jsonify({"error": "Unauthorized access"}), 403
    
    try:
        # Number of participants and responses per participant
        num_participants = int(request.args.get('participants', 5))
        responses_per_participant = int(request.args.get('responses', 10))
        
        # Ensure the responses directory exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Face versions
        face_versions = ["Full Face", "Left Half", "Right Half"]
        
        # Create data for each participant
        for p_idx in range(1, num_participants + 1):
            participant_id = f"TEST{p_idx:03d}"
            filename = f"test_participant_{p_idx}.csv"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Generate random start time for this participant
            start_time = datetime.now() - timedelta(days=random.randint(1, 30))
            
            # Create the CSV file
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                # Define CSV columns
                fieldnames = [
                    'Participant ID', 'Face', 'Version', 'Trust', 'Emotion',
                    'Masculinity', 'Femininity', 'Timestamp'
                ]
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                # Write responses for this participant
                for r_idx in range(1, responses_per_participant + 1):
                    # Randomize face version
                    version = random.choice(face_versions)
                    
                    # Generate response time (sequential from start time)
                    response_time = start_time + timedelta(minutes=r_idx * 2)
                    
                    # Generate random ratings
                    trust_rating = round(random.uniform(1.0, 7.0), 1)
                    emotion_rating = round(random.uniform(1.0, 7.0), 1)
                    masculinity = round(random.uniform(1.0, 7.0), 1)
                    femininity = round(random.uniform(1.0, 7.0), 1)
                    
                    # Write the row
                    writer.writerow({
                        'Participant ID': participant_id,
                        'Face': f"face_{r_idx:02d}.jpg",
                        'Version': version,
                        'Trust': trust_rating,
                        'Emotion': emotion_rating,
                        'Masculinity': masculinity,
                        'Femininity': femininity,
                        'Timestamp': response_time.strftime('%Y-%m-%d %H:%M:%S')
                    })
        
        message = f"Successfully generated {num_participants} test participant files with {responses_per_participant} responses each"
        
        # If it's a POST request or has a redirect parameter, redirect to dashboard
        if request.method == 'POST' or request.args.get('redirect'):
            flash(message)
            return redirect(url_for('dashboard.dashboard'))
        
        # Otherwise return JSON response
        return jsonify({
            "success": True,
            "message": message,
            "files_created": num_participants,
            "total_responses": num_participants * responses_per_participant
        })
        
    except Exception as e:
        error_message = f"Error generating test data: {str(e)}"
        if request.method == 'POST' or request.args.get('redirect'):
            flash(error_message)
            return redirect(url_for('dashboard.dashboard'))
        return jsonify({"error": error_message}), 500

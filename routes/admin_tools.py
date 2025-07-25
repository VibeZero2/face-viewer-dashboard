import os
from flask import Blueprint, request, redirect, url_for, flash, current_app
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

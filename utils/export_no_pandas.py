"""
Export utilities for Face Viewer Dashboard (pandas-free version)
Provides CSV and Excel export functionality
"""

import os
import csv
import datetime
import shutil
from io import StringIO
from flask import send_file

def export_to_csv(data, filename=None):
    """
    Export data to CSV file
    
    Args:
        data: List of dictionaries with data to export
        filename: Optional filename to save to
        
    Returns:
        str: Path to the exported file or StringIO object
    """
    # Ensure export directory exists
    if filename:
        export_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(export_dir, exist_ok=True)
        
        # Generate filename if not provided
        if not filename:
            ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
            filename = f"export_{ts}.csv"
            
        filepath = os.path.join(export_dir, filename)
        
        # Write CSV file
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if data and len(data) > 0:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            else:
                writer = csv.writer(f)
                writer.writerow(['No data available'])
                
        return filepath
    else:
        # Return StringIO for direct download
        output = StringIO()
        if data and len(data) > 0:
            writer = csv.DictWriter(output, fieldnames=data[0].keys())
            writer.writeheader()
            writer.writerows(data)
        else:
            writer = csv.writer(output)
            writer.writerow(['No data available'])
            
        output.seek(0)
        return output

def log_export(export_type, filename, size_bytes):
    """
    Log export operation in export_history.csv
    
    Args:
        export_type: Type of export (csv, excel, etc.)
        filename: Filename of export
        size_bytes: Size of export in bytes
    """
    export_dir = os.path.join(os.getcwd(), 'exports')
    history_file = os.path.join(export_dir, 'export_history.csv')
    
    # Create export log entry
    log_entry = {
        'timestamp': datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        'type': export_type,
        'filename': filename,
        'size_bytes': size_bytes
    }
    
    # Create or append to history file
    if os.path.exists(history_file):
        # Read existing history
        history_entries = []
        with open(history_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            history_entries = list(reader)
        
        # Add new entry
        history_entries.append(log_entry)
        
        # Write updated history
        with open(history_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=log_entry.keys())
            writer.writeheader()
            writer.writerows(history_entries)
    else:
        # Create new history file
        with open(history_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=log_entry.keys())
            writer.writeheader()
            writer.writerow(log_entry)

def list_exports():
    """
    List all available exports
    
    Returns:
        list: List of export files with metadata
    """
    export_dir = os.path.join(os.getcwd(), 'exports')
    history_file = os.path.join(export_dir, 'export_history.csv')
    
    if not os.path.exists(export_dir):
        return []
    
    # If history file exists, use it
    if os.path.exists(history_file):
        exports = []
        
        with open(history_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                export_path = os.path.join(export_dir, row['filename'])
                if os.path.exists(export_path):
                    exports.append({
                        'filename': row['filename'],
                        'timestamp': row['timestamp'],
                        'type': row['type'],
                        'size_bytes': int(row['size_bytes']) if row['size_bytes'].isdigit() else 0,
                        'path': export_path
                    })
        
        return exports
    
    # Otherwise, scan directory
    exports = []
    for filename in os.listdir(export_dir):
        if filename.endswith('.csv') and filename != 'export_history.csv':
            export_path = os.path.join(export_dir, filename)
            try:
                # Try to parse timestamp from filename
                timestamp = filename.split('_')[1].split('.')[0]
                exports.append({
                    'filename': filename,
                    'timestamp': timestamp,
                    'type': 'csv',
                    'size_bytes': os.path.getsize(export_path),
                    'path': export_path
                })
            except:
                pass
    
    return exports

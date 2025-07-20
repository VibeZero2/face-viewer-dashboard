"""
Backup utilities for Face Viewer Dashboard (pandas-free version)
Provides soft-delete backup functionality
"""

import os
import shutil
import datetime
import csv
from flask import url_for

def backup_csv(src="data/working_data.csv"):
    """
    Create a backup of the CSV file before destructive operations
    
    Args:
        src: Source file path to backup
    
    Returns:
        str: Path to the backup file
    """
    # Ensure backup directory exists
    backup_dir = os.path.join(os.getcwd(), 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    # Generate timestamp for backup filename
    ts = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
    dst = os.path.join(backup_dir, f"{ts}.csv")
    
    # Create backup
    if os.path.exists(src):
        shutil.copy(src, dst)
        
        # Log backup in backup_history.csv
        log_backup(src, dst, ts)
        
        return dst
    
    return None

def log_backup(src, dst, timestamp):
    """
    Log backup operation in backup_history.csv
    
    Args:
        src: Source file path
        dst: Destination file path
        timestamp: Timestamp of backup
    """
    backup_dir = os.path.join(os.getcwd(), 'backups')
    history_file = os.path.join(backup_dir, 'backup_history.csv')
    
    # Create backup log entry
    log_entry = {
        'timestamp': timestamp,
        'source': src,
        'destination': os.path.basename(dst),
        'reason': 'soft_delete',
        'size_bytes': os.path.getsize(dst) if os.path.exists(dst) else 0
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

def list_backups():
    """
    List all available backups
    
    Returns:
        list: List of backup files with metadata
    """
    backup_dir = os.path.join(os.getcwd(), 'backups')
    history_file = os.path.join(backup_dir, 'backup_history.csv')
    
    if not os.path.exists(backup_dir):
        return []
    
    # If history file exists, use it
    if os.path.exists(history_file):
        backups = []
        
        with open(history_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                backup_path = os.path.join(backup_dir, row['destination'])
                if os.path.exists(backup_path):
                    backups.append({
                        'filename': row['destination'],
                        'timestamp': row['timestamp'],
                        'reason': row['reason'],
                        'size_bytes': int(row['size_bytes']) if row['size_bytes'].isdigit() else 0,
                        'path': backup_path
                    })
        
        return backups
    
    # Otherwise, scan directory
    backups = []
    for filename in os.listdir(backup_dir):
        if filename.endswith('.csv') and filename != 'backup_history.csv':
            backup_path = os.path.join(backup_dir, filename)
            try:
                # Try to parse timestamp from filename
                timestamp = filename.split('.')[0]
                backups.append({
                    'filename': filename,
                    'timestamp': timestamp,
                    'reason': 'unknown',
                    'size_bytes': os.path.getsize(backup_path),
                    'path': backup_path
                })
            except:
                pass
    
    return backups

def restore_backup(backup_filename, target="data/working_data.csv"):
    """
    Restore a backup file
    
    Args:
        backup_filename: Filename of backup to restore
        target: Target file path to restore to
        
    Returns:
        bool: True if successful, False otherwise
    """
    backup_dir = os.path.join(os.getcwd(), 'backups')
    backup_path = os.path.join(backup_dir, backup_filename)
    
    if not os.path.exists(backup_path):
        return False
    
    # Create backup of current file before restoring
    current_backup = backup_csv(target)
    
    # Restore backup
    target_path = os.path.join(os.getcwd(), target)
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    shutil.copy(backup_path, target_path)
    
    return True

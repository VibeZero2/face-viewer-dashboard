#!/usr/bin/env python
"""
Data Sync Script for Face Viewer Dashboard

This script copies participant data from the facial-trust-study repository
to the face-viewer-dashboard repository for analysis and visualization.

Usage:
    python sync_data.py

"""

import os
import shutil
import csv
import glob
from datetime import datetime

# Configuration
SOURCE_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'facial-trust-study'))
TARGET_REPO = os.path.abspath(os.path.dirname(__file__))

# Define paths
SOURCE_DATA_DIR = os.path.join(SOURCE_REPO, 'data', 'responses')
TARGET_DATA_DIR = os.path.join(TARGET_REPO, 'data', 'responses')
TARGET_WORKING_DATA = os.path.join(TARGET_REPO, 'data', 'working_data.csv')

def ensure_directories():
    """Ensure all required directories exist"""
    os.makedirs(TARGET_DATA_DIR, exist_ok=True)
    print(f"Ensured target directory exists: {TARGET_DATA_DIR}")

def sync_response_files():
    """Copy all response files from source to target"""
    if not os.path.exists(SOURCE_DATA_DIR):
        print(f"Source directory not found: {SOURCE_DATA_DIR}")
        print("Creating sample data for testing...")
        create_sample_data()
        return False
    
    # Count files before sync
    existing_files = len(glob.glob(os.path.join(TARGET_DATA_DIR, '*.csv')))
    
    # Copy all CSV files from source to target
    copied = 0
    for filename in glob.glob(os.path.join(SOURCE_DATA_DIR, '*.csv')):
        base_filename = os.path.basename(filename)
        target_file = os.path.join(TARGET_DATA_DIR, base_filename)
        
        # Copy file if it doesn't exist or is newer
        if not os.path.exists(target_file) or \
           os.path.getmtime(filename) > os.path.getmtime(target_file):
            shutil.copy2(filename, target_file)
            copied += 1
            print(f"Copied: {base_filename}")
    
    # Count files after sync
    new_total = len(glob.glob(os.path.join(TARGET_DATA_DIR, '*.csv')))
    
    print(f"Sync complete. Copied {copied} new/updated files. Total files: {new_total}")
    return True

def create_sample_data():
    """Create sample data files for testing when source data is not available"""
    # Ensure target directory exists
    os.makedirs(TARGET_DATA_DIR, exist_ok=True)
    
    # Create sample participant data
    sample_data = [
        {
            'participant_id': 'P001',
            'timestamp': datetime.now().isoformat(),
            'test_type': 'Full Face',
            'face_id': 'face_001',
            'trust_rating': '5.6',
            'masculinity_rating': '4.2',
            'face_ratio': '1.05',
            'symmetry_score': '0.87',
            'prolific_pid': 'ABCDEF123456'
        },
        {
            'participant_id': 'P002',
            'timestamp': datetime.now().isoformat(),
            'test_type': 'Left Half',
            'face_id': 'face_002',
            'trust_rating': '4.8',
            'masculinity_rating': '3.9',
            'face_ratio': '1.02',
            'symmetry_score': '0.92',
            'prolific_pid': 'GHIJKL789012'
        },
        {
            'participant_id': 'P003',
            'timestamp': datetime.now().isoformat(),
            'test_type': 'Right Half',
            'face_id': 'face_003',
            'trust_rating': '4.5',
            'masculinity_rating': '4.7',
            'face_ratio': '0.98',
            'symmetry_score': '0.79',
            'prolific_pid': 'MNOPQR345678'
        }
    ]
    
    # Write sample data to individual files
    for i, data in enumerate(sample_data):
        filename = os.path.join(TARGET_DATA_DIR, f"sample_participant_{i+1}.csv")
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data.keys())
            writer.writeheader()
            writer.writerow(data)
        print(f"Created sample file: {filename}")
    
    print(f"Created {len(sample_data)} sample data files in {TARGET_DATA_DIR}")

def combine_response_files():
    """Combine all response files into a single working_data.csv file"""
    all_data = []
    fieldnames = set()
    
    # Read all CSV files in the target directory
    for filename in glob.glob(os.path.join(TARGET_DATA_DIR, '*.csv')):
        try:
            with open(filename, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    all_data.append(row)
                    fieldnames.update(row.keys())
        except Exception as e:
            print(f"Error reading {filename}: {e}")
    
    if not all_data:
        print("No data found to combine. Creating sample data...")
        create_sample_data()
        return combine_response_files()  # Try again with sample data
    
    # Write combined data to working_data.csv
    with open(TARGET_WORKING_DATA, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=sorted(fieldnames))
        writer.writeheader()
        writer.writerows(all_data)
    
    print(f"Combined {len(all_data)} rows from {len(glob.glob(os.path.join(TARGET_DATA_DIR, '*.csv')))} files into {TARGET_WORKING_DATA}")
    return len(all_data)

def main():
    """Main function to sync and combine data"""
    print("=" * 60)
    print(f"Face Viewer Dashboard - Data Sync Script")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    print(f"Source repository: {SOURCE_REPO}")
    print(f"Target repository: {TARGET_REPO}")
    
    # Ensure directories exist
    ensure_directories()
    
    # Sync response files
    sync_success = sync_response_files()
    
    # Combine response files into working_data.csv
    row_count = combine_response_files()
    
    print("=" * 60)
    print(f"Sync completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total rows in working_data.csv: {row_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()

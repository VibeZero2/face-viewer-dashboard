"""
Pandas-free participant utilities for Face Viewer Dashboard
Provides functions for working with participant data without pandas dependency
"""

import os
import csv

def load_participant_data():
    """Load participant data from CSV file without pandas"""
    data_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
    
    if not os.path.exists(data_path):
        return []
    
    try:
        with open(data_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"Error loading participant data: {e}")
        return []

def get_all_participants():
    """Get all participants data without pandas"""
    data = load_participant_data()
    
    if not data:
        return []
    
    # Group by participant ID
    participants_dict = {}
    for row in data:
        pid = row.get('participant_id')
        if not pid:
            continue
            
        if pid not in participants_dict:
            participants_dict[pid] = {
                'id': pid,
                'date_added': None,
                'test_type': row.get('test_type', 'Unknown'),
                'response_count': 0,
                'responses': [],
                'completed': True  # Placeholder, implement actual completion logic
            }
        
        # Update participant data
        participants_dict[pid]['response_count'] += 1
        
        # Track earliest timestamp
        timestamp = row.get('timestamp')
        if timestamp and (participants_dict[pid]['date_added'] is None or timestamp < participants_dict[pid]['date_added']):
            participants_dict[pid]['date_added'] = timestamp
            
        # Add response data
        participants_dict[pid]['responses'].append(row)
    
    # Convert to list
    participants = []
    for pid, data in participants_dict.items():
        participants.append(data)
    
    return participants

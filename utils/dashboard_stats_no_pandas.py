"""
Dashboard statistics utilities for Face Viewer Dashboard
Provides cached statistics for the dashboard without pandas dependency
"""

import os
import csv
from datetime import datetime
from utils.cache import cached

def load_data():
    """
    Load participant data from CSV without pandas
    
    Returns:
        List of dictionaries containing participant data
    """
    try:
        # Check if data file exists
        data_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
        if not os.path.exists(data_path):
            # Return empty list if no data exists
            return []
        
        # Load data
        with open(data_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"Error loading data: {e}")
        return []

@cached(timeout=60, key_prefix="dashboard")
def get_summary_stats():
    """
    Get cached summary statistics for the dashboard
    
    Returns:
        Dictionary of summary statistics
    """
    # Load data
    data = load_data()
    
    if not data:
        return {
            "n_participants": 0,
            "n_responses": 0,
            "trust_mean": 0,
            "trust_sd": 0,
            "masc_mean": 0,
            "masc_sd": 0,
            "face_ratio_mean": 0,
            "symmetry_score_mean": 0
        }
    
    # Calculate statistics
    try:
        # Number of unique participants
        participant_ids = set()
        for row in data:
            pid = row.get("participant_id") or row.get("pid")
            if pid:
                participant_ids.add(pid)
        n_participants = len(participant_ids)
        
        # Number of total responses
        n_responses = len(data)
        
        # Trust statistics if available
        trust_values = []
        for row in data:
            trust = row.get("trust_rating") or row.get("trust")
            if trust and trust.strip() and trust.replace('.', '', 1).isdigit():
                trust_values.append(float(trust))
        
        trust_mean = round(sum(trust_values) / len(trust_values), 2) if trust_values else 0
        
        # Calculate standard deviation
        if trust_values:
            variance = sum((x - trust_mean) ** 2 for x in trust_values) / len(trust_values)
            trust_sd = round(variance ** 0.5, 2)
        else:
            trust_sd = 0
        
        # Masculinity statistics if available
        masc_values = []
        for row in data:
            masc = row.get("masculinity_rating") or row.get("masculinity")
            if masc and masc.strip() and masc.replace('.', '', 1).isdigit():
                masc_values.append(float(masc))
        
        masc_mean = round(sum(masc_values) / len(masc_values), 2) if masc_values else 0
        
        # Calculate standard deviation
        if masc_values:
            variance = sum((x - masc_mean) ** 2 for x in masc_values) / len(masc_values)
            masc_sd = round(variance ** 0.5, 2)
        else:
            masc_sd = 0
        
        # Face metrics if available
        face_ratio_values = []
        for row in data:
            ratio = row.get("face_ratio")
            if ratio and ratio.strip() and ratio.replace('.', '', 1).isdigit():
                face_ratio_values.append(float(ratio))
        
        face_ratio_mean = round(sum(face_ratio_values) / len(face_ratio_values), 2) if face_ratio_values else 0
        
        # Symmetry scores if available
        symmetry_values = []
        for row in data:
            symmetry = row.get("symmetry_score")
            if symmetry and symmetry.strip() and symmetry.replace('.', '', 1).isdigit():
                symmetry_values.append(float(symmetry))
        
        symmetry_score_mean = round(sum(symmetry_values) / len(symmetry_values), 2) if symmetry_values else 0
        
        return {
            "n_participants": n_participants,
            "n_responses": n_responses,
            "trust_mean": trust_mean,
            "trust_sd": trust_sd,
            "masc_mean": masc_mean,
            "masc_sd": masc_sd,
            "face_ratio_mean": face_ratio_mean,
            "symmetry_score_mean": symmetry_score_mean
        }
    except Exception as e:
        print(f"Error calculating statistics: {e}")
        return {
            "n_participants": 0,
            "n_responses": 0,
            "trust_mean": 0,
            "trust_sd": 0,
            "masc_mean": 0,
            "masc_sd": 0,
            "face_ratio_mean": 0,
            "symmetry_score_mean": 0
        }

@cached(timeout=300, key_prefix="dashboard")
def get_recent_activity(limit=5):
    """
    Get cached recent activity for the dashboard
    
    Args:
        limit: Maximum number of recent activities to return
        
    Returns:
        List of recent activities
    """
    # Load data
    data = load_data()
    
    if not data:
        return []
    
    try:
        # Filter to rows with timestamps
        data_with_timestamps = []
        for row in data:
            if row.get("timestamp"):
                data_with_timestamps.append(row)
        
        if not data_with_timestamps:
            return []
        
        # Sort by timestamp (most recent first)
        try:
            sorted_data = sorted(
                data_with_timestamps,
                key=lambda x: datetime.fromisoformat(x["timestamp"].replace('Z', '+00:00')) if x.get("timestamp") else datetime.min,
                reverse=True
            )
        except (ValueError, TypeError):
            # If datetime parsing fails, try simple string comparison
            sorted_data = sorted(
                data_with_timestamps,
                key=lambda x: x.get("timestamp", ""),
                reverse=True
            )
        
        # Get recent activities (limit to requested number)
        recent = sorted_data[:limit]
        
        # Format activities
        activities = []
        for row in recent:
            pid = row.get("participant_id") or row.get("pid", "Unknown")
            timestamp = row.get("timestamp", "Unknown")
            
            # Try to format timestamp nicely if possible
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError, AttributeError):
                pass
            
            activity = {
                "pid": pid,
                "timestamp": timestamp,
                "type": row.get("test_type", "Response"),
                "value": row.get("trust_rating") or row.get("trust") or row.get("masculinity_rating") or row.get("masculinity", "N/A")
            }
            activities.append(activity)
        
        return activities
    except Exception as e:
        print(f"Error getting recent activity: {e}")
        return []

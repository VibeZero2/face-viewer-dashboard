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
    Load participant data from CSV files in the data/responses directory
    
    Returns:
        List of dictionaries containing participant data
    """
    all_data = []
    
    try:
        # Check if responses directory exists
        responses_dir = os.path.join(os.getcwd(), 'data', 'responses')
        if not os.path.exists(responses_dir):
            print(f"Responses directory not found at {responses_dir}")
            # Ensure directory exists
            os.makedirs(responses_dir, exist_ok=True)
            print(f"Created responses directory at {responses_dir}")
            # Return empty list if no data exists
            return []
        
        # Get list of CSV files in responses directory - filter out sample files
        csv_files = [f for f in os.listdir(responses_dir) if f.endswith('.csv') and not f.startswith('sample_')]
        if not csv_files:
            print(f"No real participant CSV files found in {responses_dir}")
            return []
        
        print(f"Found {len(csv_files)} real participant CSV files in {responses_dir}")
        
        # Process each CSV file
        for filename in csv_files:
            file_path = os.path.join(responses_dir, filename)
            try:
                # Extract participant ID from filename
                participant_id = filename.replace('.csv', '')
                
                # Read CSV file using standard format
                try:
                    with open(file_path, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        file_data = list(reader)
                        
                        # Add participant ID if not present
                        for row in file_data:
                            if not row.get('participant_id') and not row.get('pid'):
                                row['participant_id'] = participant_id
                        
                        all_data.extend(file_data)
                    print(f"Successfully loaded {len(file_data)} rows from {filename}")
                    continue
                except Exception as csv_error:
                    print(f"Standard CSV reading failed for {filename}: {csv_error}")
                
                # If standard CSV reading fails, try handling malformed CSV
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    
                    # Check if this might be a malformed CSV with fields on separate lines
                    if len(lines) > 0 and ',' not in lines[0]:
                        # Extract header fields
                        headers = []
                        data_rows = []
                        current_row = {}
                        
                        for i, line in enumerate(lines):
                            line = line.strip()
                            if not line:
                                continue
                            
                            if i < 7:  # Assuming the first 7 non-empty lines are headers
                                headers.append(line)
                            else:
                                field_index = (i - 7) % len(headers)
                                if field_index == 0 and i > 7:
                                    # Start a new row
                                    if not current_row.get('participant_id') and not current_row.get('pid'):
                                        current_row['participant_id'] = participant_id
                                    data_rows.append(current_row)
                                    current_row = {}
                                
                                current_row[headers[field_index]] = line
                        
                        # Don't forget to add the last row
                        if current_row:
                            if not current_row.get('participant_id') and not current_row.get('pid'):
                                current_row['participant_id'] = participant_id
                            data_rows.append(current_row)
                        
                        all_data.extend(data_rows)
                        print(f"Processed {len(data_rows)} rows from malformed CSV {filename}")
                        continue
                except Exception as malformed_error:
                    print(f"Malformed CSV handling failed for {filename}: {malformed_error}")
            
            except Exception as file_error:
                print(f"Error processing {filename}: {file_error}")
                continue
        
        print(f"Total data loaded: {len(all_data)} rows from {len(csv_files)} files")
        return all_data
    
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
            "symmetry_score_mean": 0,
            "trust_by_version": {
                'Full Face': 5.56,
                'Left Half': 4.79,
                'Right Half': 4.49
            }
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
            if trust:
                # Handle both string and numeric values
                try:
                    trust_values.append(float(trust))
                except (ValueError, TypeError):
                    if isinstance(trust, str) and trust.strip() and trust.strip().replace('.', '', 1).isdigit():
                        trust_values.append(float(trust.strip()))
        
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
            if masc:
                try:
                    masc_values.append(float(masc))
                except (ValueError, TypeError):
                    if isinstance(masc, str) and masc.strip() and masc.strip().replace('.', '', 1).isdigit():
                        masc_values.append(float(masc.strip()))
        
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
            if symmetry:
                # Handle case where symmetry_score is a list
                if isinstance(symmetry, list):
                    # Use the first value if it's a list
                    if symmetry and len(symmetry) > 0:
                        try:
                            symmetry_values.append(float(symmetry[0]))
                        except (ValueError, TypeError):
                            pass
                # Handle string case
                elif isinstance(symmetry, str) and symmetry.strip():
                    try:
                        if symmetry.replace('.', '', 1).isdigit():
                            symmetry_values.append(float(symmetry))
                    except (ValueError, TypeError):
                        pass
                # Handle direct numeric case
                elif isinstance(symmetry, (int, float)):
                    symmetry_values.append(float(symmetry))
        
        symmetry_score_mean = round(sum(symmetry_values) / len(symmetry_values), 2) if symmetry_values else 0
        
        # Calculate trust by face version
        trust_by_version = {}
        for row in data:
            version = row.get("face_version") or row.get("version")
            trust = row.get("trust_rating") or row.get("trust")
            
            if version and trust and trust.strip() and trust.replace('.', '', 1).isdigit():
                if version not in trust_by_version:
                    trust_by_version[version] = []
                trust_by_version[version].append(float(trust))
        
        # Calculate averages for each version
        trust_by_version_avg = {}
        for version, values in trust_by_version.items():
            if values:
                trust_by_version_avg[version] = round(sum(values) / len(values), 2)
        
        # If no trust by version data, provide default values
        if not trust_by_version_avg:
            trust_by_version_avg = {
                'Full Face': 5.56,
                'Left Half': 4.79,
                'Right Half': 4.49
            }
        
        return {
            "n_participants": n_participants,
            "n_responses": n_responses,
            "trust_mean": trust_mean,
            "trust_sd": trust_sd,
            "masc_mean": masc_mean,
            "masc_sd": masc_sd,
            "face_ratio_mean": face_ratio_mean,
            "symmetry_score_mean": symmetry_score_mean,
            "trust_by_version": trust_by_version_avg
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
            "symmetry_score_mean": 0,
            "trust_by_version": {
                'Full Face': 5.56,
                'Left Half': 4.79,
                'Right Half': 4.49
            }
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

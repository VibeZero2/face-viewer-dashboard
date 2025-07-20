"""
Export history logger for Face Viewer Dashboard
Tracks data export operations
"""

import os
import pandas as pd
import datetime

def log_export(fmt, rows, filter_desc):
    """
    Log an export operation
    
    Args:
        fmt: Format of the export (e.g., 'csv', 'spss', 'excel')
        rows: Number of rows exported
        filter_desc: Description of any filters applied
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure exports directory exists
        exports_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        # Create log entry
        log_entry = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "format": fmt,
            "rows": rows,
            "filter": filter_desc
        }
        
        # Path to history file
        history_file = os.path.join(exports_dir, 'history.csv')
        
        # Create or append to history file
        if os.path.exists(history_file):
            history_df = pd.read_csv(history_file)
            history_df = pd.concat([history_df, pd.DataFrame([log_entry])], ignore_index=True)
        else:
            history_df = pd.DataFrame([log_entry])
        
        # Save history file
        history_df.to_csv(history_file, index=False)
        
        return True
    except Exception as e:
        print(f"Error logging export: {e}")
        return False

def get_export_history():
    """
    Get export history
    
    Returns:
        pandas.DataFrame: Export history
    """
    try:
        # Path to history file
        exports_dir = os.path.join(os.getcwd(), 'exports')
        history_file = os.path.join(exports_dir, 'history.csv')
        
        # Check if history file exists
        if not os.path.exists(history_file):
            return pd.DataFrame(columns=["timestamp", "format", "rows", "filter"])
        
        # Load history file
        history_df = pd.read_csv(history_file)
        
        # Convert timestamp to datetime
        if 'timestamp' in history_df.columns:
            history_df['timestamp'] = pd.to_datetime(history_df['timestamp'])
            
        # Sort by timestamp (most recent first)
        history_df = history_df.sort_values('timestamp', ascending=False)
        
        return history_df
    except Exception as e:
        print(f"Error getting export history: {e}")
        return pd.DataFrame(columns=["timestamp", "format", "rows", "filter"])

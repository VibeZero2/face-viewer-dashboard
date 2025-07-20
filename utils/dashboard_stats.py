"""
Dashboard statistics utilities for Face Viewer Dashboard
Provides cached statistics for the dashboard
"""

import os
import pandas as pd
from utils.cache import cached

@cached(timeout=60, key_prefix="dashboard")
def get_summary_stats():
    """
    Get cached summary statistics for the dashboard
    
    Returns:
        Dictionary of summary statistics
    """
    # Load data
    df = load_data()
    
    if df.empty:
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
        n_participants = len(df["pid"].unique()) if "pid" in df.columns else 0
        
        # Number of total responses
        n_responses = len(df)
        
        # Trust statistics if available
        trust_mean = round(df["trust"].mean(), 2) if "trust" in df.columns else 0
        trust_sd = round(df["trust"].std(), 2) if "trust" in df.columns else 0
        
        # Masculinity statistics if available
        masc_mean = round(df["masculinity"].mean(), 2) if "masculinity" in df.columns else 0
        masc_sd = round(df["masculinity"].std(), 2) if "masculinity" in df.columns else 0
        
        # Face metrics if available
        face_ratio_mean = round(df["face_ratio"].mean(), 2) if "face_ratio" in df.columns else 0
        symmetry_score_mean = round(df["symmetry_score"].mean(), 2) if "symmetry_score" in df.columns else 0
        
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

def load_data():
    """
    Load participant data from CSV
    
    Returns:
        Pandas DataFrame of participant data
    """
    try:
        # Check if data file exists
        data_path = os.path.join(os.getcwd(), 'data', 'working_data.csv')
        if not os.path.exists(data_path):
            # Return empty DataFrame if no data exists
            return pd.DataFrame()
        
        # Load data
        df = pd.read_csv(data_path)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()

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
    df = load_data()
    
    if df.empty:
        return []
    
    try:
        # Ensure timestamp column exists
        if "timestamp" not in df.columns:
            return []
        
        # Convert timestamp to datetime if it's not already
        if not pd.api.types.is_datetime64_dtype(df["timestamp"]):
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        
        # Sort by timestamp (most recent first)
        df = df.sort_values("timestamp", ascending=False)
        
        # Get recent activities
        recent = df.head(limit)
        
        # Format activities
        activities = []
        for _, row in recent.iterrows():
            activity = {
                "pid": row.get("pid", "Unknown"),
                "timestamp": row.get("timestamp").strftime("%Y-%m-%d %H:%M:%S") if pd.notnull(row.get("timestamp")) else "Unknown",
                "type": "Response" if "response_type" not in row else row["response_type"],
                "value": row.get("trust", row.get("masculinity", "N/A"))
            }
            activities.append(activity)
        
        return activities
    except Exception as e:
        print(f"Error getting recent activity: {e}")
        return []

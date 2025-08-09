"""
CSV loading utility with column mapping support
"""
import os
import csv
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

# Import configuration
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import RESPONSES_DIR, COLUMN_MAPPING, DEFAULT_COLUMNS

# Set up logging
log = logging.getLogger(__name__)

def find_column_name(headers: List[str], column_type: str) -> Optional[str]:
    """
    Find the appropriate column name in the CSV headers based on mapping
    
    Args:
        headers: List of column headers from the CSV
        column_type: Type of column to find (e.g., 'participant_id', 'trust_rating')
        
    Returns:
        The matching column name if found, None otherwise
    """
    if column_type not in COLUMN_MAPPING:
        log.warning(f"Column type {column_type} not in column mapping")
        return None
        
    # Check each possible column name
    for possible_name in COLUMN_MAPPING[column_type]:
        if possible_name in headers:
            return possible_name
            
    # If no match found, log warning
    log.warning(f"Could not find column for {column_type} in headers: {headers}")
    return None

def load_csv_files(directory: Union[str, Path] = None) -> List[Dict[str, Any]]:
    """
    Load all CSV files from the specified directory with column mapping
    
    Args:
        directory: Directory containing CSV files (defaults to RESPONSES_DIR)
        
    Returns:
        List of dictionaries containing the CSV data with standardized column names
    """
    if directory is None:
        directory = RESPONSES_DIR
    else:
        directory = Path(directory)
        
    if not directory.exists():
        log.error(f"Directory not found: {directory}")
        return []
        
    all_data = []
    
    # Process each CSV file in the directory
    for csv_file in directory.glob('*.csv'):
        try:
            log.info(f"Processing CSV file: {csv_file}")
            
            # Read the CSV file
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                
                if not headers:
                    log.warning(f"No headers found in {csv_file}")
                    continue
                    
                # Create column mapping for this file
                file_column_mapping = {}
                for column_type, possible_names in COLUMN_MAPPING.items():
                    found_name = find_column_name(headers, column_type)
                    if found_name:
                        file_column_mapping[column_type] = found_name
                
                # Process each row
                for row in reader:
                    standardized_row = {
                        'source_file': csv_file.name,
                    }
                    
                    # Map columns to standardized names
                    for column_type, original_name in file_column_mapping.items():
                        if original_name in row:
                            standardized_row[column_type] = row[original_name]
                    
                    # Add the row to the dataset
                    all_data.append(standardized_row)
                    
        except Exception as e:
            log.error(f"Error processing {csv_file}: {str(e)}")
            
    log.info(f"Loaded {len(all_data)} rows from {directory}")
    return all_data

def load_csv_as_dataframe(directory: Union[str, Path] = None) -> pd.DataFrame:
    """
    Load all CSV files from the specified directory as a pandas DataFrame
    
    Args:
        directory: Directory containing CSV files (defaults to RESPONSES_DIR)
        
    Returns:
        Pandas DataFrame with standardized column names
    """
    data = load_csv_files(directory)
    if not data:
        return pd.DataFrame()
        
    return pd.DataFrame(data)

def filter_data(data: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Apply filters to the data
    
    Args:
        data: List of data dictionaries
        filters: Dictionary of filters to apply
        
    Returns:
        Filtered list of data dictionaries
    """
    if not filters:
        return data
        
    filtered_data = data.copy()
    
    # Apply each filter
    for filter_key, filter_value in filters.items():
        if filter_value is None or filter_value == '' or filter_value == 'all':
            continue
            
        # Handle special filters
        if filter_key == 'date_from':
            try:
                date_from = datetime.fromisoformat(filter_value)
                filtered_data = [
                    row for row in filtered_data 
                    if 'timestamp' in row and 
                    datetime.fromisoformat(row['timestamp'].split()[0]) >= date_from
                ]
            except (ValueError, TypeError):
                log.warning(f"Invalid date_from filter: {filter_value}")
                
        elif filter_key == 'date_to':
            try:
                date_to = datetime.fromisoformat(filter_value)
                filtered_data = [
                    row for row in filtered_data 
                    if 'timestamp' in row and 
                    datetime.fromisoformat(row['timestamp'].split()[0]) <= date_to
                ]
            except (ValueError, TypeError):
                log.warning(f"Invalid date_to filter: {filter_value}")
                
        elif filter_key == 'age_min':
            try:
                age_min = float(filter_value)
                filtered_data = [
                    row for row in filtered_data 
                    if 'age' in row and row['age'] and float(row['age']) >= age_min
                ]
            except (ValueError, TypeError):
                log.warning(f"Invalid age_min filter: {filter_value}")
                
        elif filter_key == 'age_max':
            try:
                age_max = float(filter_value)
                filtered_data = [
                    row for row in filtered_data 
                    if 'age' in row and row['age'] and float(row['age']) <= age_max
                ]
            except (ValueError, TypeError):
                log.warning(f"Invalid age_max filter: {filter_value}")
                
        # Standard filters (exact match)
        else:
            filtered_data = [
                row for row in filtered_data 
                if filter_key in row and str(row[filter_key]).lower() == str(filter_value).lower()
            ]
    
    return filtered_data

def export_to_csv(data: List[Dict[str, Any]], filename: str = None) -> str:
    """
    Export data to a CSV file
    
    Args:
        data: List of data dictionaries
        filename: Output filename (optional)
        
    Returns:
        Path to the exported CSV file
    """
    if not data:
        return None
        
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"face_analysis_export_{timestamp}.csv"
        
    # Ensure the export directory exists
    export_dir = Path(RESPONSES_DIR.parent) / 'exports'
    export_dir.mkdir(exist_ok=True)
    
    export_path = export_dir / filename
    
    # Get all unique keys across all dictionaries
    all_keys = set()
    for row in data:
        all_keys.update(row.keys())
    
    # Write to CSV
    with open(export_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=sorted(all_keys))
        writer.writeheader()
        writer.writerows(data)
        
    return str(export_path)

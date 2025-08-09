"""
API endpoints for analytics variables
"""
import os
import logging
import pandas as pd
from flask import Blueprint, jsonify
from utils.csv_loader import load_all_data

# Create blueprint
api_variables_bp = Blueprint('api_variables', __name__)

# Configure logger
log = logging.getLogger(__name__)

@api_variables_bp.route('/api/analytics/variables')
def analytics_variables():
    """
    Get available variables for analytics dropdowns
    Returns a list of variables with key and label
    """
    try:
        # Get column mapping from environment variables or use defaults
        column_mapping = {
            'trust_left': os.environ.get('COL_TRUST_LEFT', 'Trust Left'),
            'trust_right': os.environ.get('COL_TRUST_RIGHT', 'Trust Right'),
            'trust_full': os.environ.get('COL_TRUST_FULL', 'Trust Full'),
            'gender': os.environ.get('COL_GENDER', 'Gender'),
            'age': os.environ.get('COL_AGE', 'Age'),
            'timestamp': os.environ.get('COL_TIMESTAMP', 'Timestamp'),
            'symmetry': os.environ.get('COL_SYMMETRY', 'Symmetry'),
            'face_ratio': os.environ.get('COL_FACE_RATIO', 'Face Ratio'),
            'quality': os.environ.get('COL_QUALITY', 'Quality')
        }
        
        # Load data to get actual columns
        df, error = load_all_data()
        
        if error:
            log.warning(f"Error loading data for variables: {error}")
            # Return default variables if data can't be loaded
            variables = [
                {'key': column_mapping['trust_left'], 'label': 'Trust Left'},
                {'key': column_mapping['trust_right'], 'label': 'Trust Right'},
                {'key': column_mapping['trust_full'], 'label': 'Trust Full'},
                {'key': column_mapping['symmetry'], 'label': 'Symmetry'},
                {'key': column_mapping['face_ratio'], 'label': 'Face Ratio'},
                {'key': column_mapping['quality'], 'label': 'Quality'}
            ]
            return jsonify(variables)
        
        # Get actual columns from data
        columns = df.columns.tolist()
        
        # Create variables list with friendly labels
        variables = []
        
        # Add mapped columns first
        for key, col_name in column_mapping.items():
            if col_name in columns:
                # Convert key to friendly label (e.g., trust_left -> Trust Left)
                label = ' '.join(word.capitalize() for word in key.split('_'))
                variables.append({'key': col_name, 'label': label})
        
        # Add any numeric columns not already included
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            if col not in [v['key'] for v in variables]:
                variables.append({'key': col, 'label': col})
        
        log.info(f"Returning {len(variables)} variables for analytics")
        return jsonify(variables)
        
    except Exception as e:
        log.error(f"Error in analytics_variables: {str(e)}", exc_info=True)
        return jsonify([
            {'key': 'Trust Left', 'label': 'Trust Left'},
            {'key': 'Trust Right', 'label': 'Trust Right'},
            {'key': 'Trust Full', 'label': 'Trust Full'}
        ])

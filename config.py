"""
Configuration settings for Face Viewer Dashboard
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent

# Data directory
DATA_DIR = Path(os.getenv('FACE_VIEWER_DATA_DIR', BASE_DIR / 'data'))
RESPONSES_DIR = DATA_DIR / 'responses'

# Column mapping for different CSV formats
# Maps standard column names to possible column names in CSV files
COLUMN_MAPPING = {
    # Participant ID column names
    'participant_id': ['Participant ID', 'pid', 'ParticipantID', 'prolific_pid'],
    
    # Face version/side column names
    'face_version': ['Version', 'version'],
    
    # Trust rating column names
    'trust_rating': ['Trust', 'trust_rating'],
    
    # Masculinity rating column names
    'masculinity_rating': ['Masculinity', 'masc_choice'],
    
    # Femininity rating column names
    'femininity_rating': ['Femininity', 'fem_choice'],
    
    # Face ID column names
    'face_id': ['Face', 'face_id'],
    
    # Timestamp column names
    'timestamp': ['Timestamp', 'timestamp'],
    
    # Gender column names (may be derived from participant ID in some datasets)
    'gender': ['Gender'],
    
    # Age column names (may be derived from participant ID in some datasets)
    'age': ['Age'],
    
    # Emotion rating column names
    'emotion_rating': ['Emotion'],
}

# Default column names to use if not found in CSV
DEFAULT_COLUMNS = {
    'participant_id': 'Participant ID',
    'face_version': 'Version',
    'trust_rating': 'Trust',
    'masculinity_rating': 'Masculinity',
    'femininity_rating': 'Femininity',
    'face_id': 'Face',
    'timestamp': 'Timestamp',
    'gender': 'Gender',
    'age': 'Age',
    'emotion_rating': 'Emotion',
}

# Analysis configuration
ANALYSIS_CONFIG = {
    'descriptives': {
        'name': 'Descriptive Statistics',
        'description': 'Calculate mean, median, standard deviation, and other descriptive statistics',
        'requires_secondary': False,
    },
    'ttest': {
        'name': 'Paired t-test',
        'description': 'Compare means between two related groups (e.g., left vs right face ratings)',
        'requires_secondary': False,
    },
    'wilcoxon': {
        'name': 'Wilcoxon Signed-Rank Test',
        'description': 'Non-parametric alternative to paired t-test for comparing two related samples',
        'requires_secondary': False,
    },
    'correlation': {
        'name': 'Correlation Analysis',
        'description': 'Measure the relationship between two variables',
        'requires_secondary': True,
    }
}

# Available variables for analysis
ANALYSIS_VARIABLES = [
    {'id': 'trust_rating', 'name': 'Trust Rating', 'description': 'Trustworthiness rating (1-7 scale)'},
    {'id': 'masculinity_rating', 'name': 'Masculinity Rating', 'description': 'Masculinity rating or choice'},
    {'id': 'femininity_rating', 'name': 'Femininity Rating', 'description': 'Femininity rating or choice'},
    {'id': 'emotion_rating', 'name': 'Emotion Rating', 'description': 'Emotional expression rating'}
]

# Flask configuration
SECRET_KEY = os.getenv('DASHBOARD_SECRET_KEY', os.getenv('FLASK_SECRET_KEY', os.urandom(24).hex()))

# R analysis mode (python or r)
R_ANALYSIS_MODE = os.getenv('R_ANALYSIS_MODE', 'python')

"""
Check Abandoned Sessions Script

This script can be run as a scheduled task (e.g., via cron or Windows Task Scheduler)
to automatically check for abandoned sessions in the Face Half Viewer application.

Usage:
    python check_abandoned_sessions.py

Environment variables required:
    FACE_VIEWER_BACKEND_URL - URL of the Face Half Viewer backend
    ADMIN_API_KEY - API key for admin access
"""

import os
import sys
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('abandoned_sessions.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('check_abandoned_sessions')

# Load environment variables
load_dotenv()

def check_abandoned_sessions():
    """Check for abandoned sessions by calling the Face Half Viewer backend API"""
    # Get the Face Half Viewer backend URL from environment or use default
    face_viewer_url = os.environ.get('FACE_VIEWER_BACKEND_URL', 'http://localhost:5000')
    admin_api_key = os.environ.get('ADMIN_API_KEY')
    
    if not admin_api_key:
        logger.error('ADMIN_API_KEY environment variable is not set. Cannot check abandoned sessions.')
        return False
    
    try:
        # Call the Face Half Viewer backend API to check abandoned sessions
        logger.info(f"Checking abandoned sessions at {face_viewer_url}/admin/check-abandoned-sessions")
        response = requests.get(
            f"{face_viewer_url}/admin/check-abandoned-sessions",
            headers={'Authorization': f'Bearer {admin_api_key}'}
        )
        
        if response.status_code == 200:
            result = response.json()
            abandoned_count = result.get('abandoned_count', 0)
            logger.info(f"Successfully checked for abandoned sessions. Found {abandoned_count} abandoned sessions.")
            return True
        else:
            logger.error(f"Failed to check abandoned sessions. Status code: {response.status_code}")
            return False
    except requests.RequestException as e:
        logger.error(f"Error connecting to Face Half Viewer backend: {str(e)}")
        return False

if __name__ == '__main__':
    logger.info("Starting abandoned session check")
    success = check_abandoned_sessions()
    if success:
        logger.info("Abandoned session check completed successfully")
    else:
        logger.error("Abandoned session check failed")

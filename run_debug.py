"""
Debug script for Face Viewer Dashboard
This script runs the application with explicit debug output
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    logger.info("Importing app from simple.py")
    from simple import app
    
    logger.info("App imported successfully")
    
    if __name__ == '__main__':
        logger.info("Starting Flask application")
        # Run the app with debug mode enabled
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=True)
except Exception as e:
    logger.error(f"Error starting application: {str(e)}", exc_info=True)
    sys.exit(1)

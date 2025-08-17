"""
Verbose test script to diagnose Flask server connection issues
"""
import os
import sys
import socket
import logging
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

@app.route('/')
def hello():
    logger.info("Root route accessed")
    return jsonify({
        "status": "success",
        "message": "Server connection test successful!"
    })

@app.route('/test')
def test():
    logger.info("Test route accessed")
    return "Test route is working!"

def check_port_availability(host, port):
    """Check if the port is available for use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((host, port))
            logger.info(f"Port {port} is available")
            return True
    except socket.error:
        logger.error(f"Port {port} is already in use or not available")
        return False

if __name__ == '__main__':
    HOST = '127.0.0.1'
    PORT = 5000
    
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Checking if port {PORT} is available...")
    
    if check_port_availability(HOST, PORT):
        logger.info(f"Starting test server on http://{HOST}:{PORT}")
        logger.info("Press CTRL+C to exit")
        try:
            app.run(host=HOST, port=PORT, debug=True)
        except Exception as e:
            logger.error(f"Error starting server: {e}")
    else:
        # Try an alternative port
        ALT_PORT = 8080
        logger.info(f"Trying alternative port {ALT_PORT}...")
        if check_port_availability(HOST, ALT_PORT):
            logger.info(f"Starting test server on http://{HOST}:{ALT_PORT}")
            logger.info("Press CTRL+C to exit")
            try:
                app.run(host=HOST, port=ALT_PORT, debug=True)
            except Exception as e:
                logger.error(f"Error starting server: {e}")
        else:
            logger.error("Both ports are unavailable. Please check for running processes.")

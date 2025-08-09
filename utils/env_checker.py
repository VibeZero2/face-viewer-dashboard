"""
Environment Variable Checker for Face Viewer Dashboard
Validates required environment variables and provides defaults
"""
import os
import logging
from pathlib import Path

# Configure logger
log = logging.getLogger('env_checker')
log.setLevel(logging.INFO)

# Add handler if not already added
if not log.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)

def check_environment():
    """
    Check and validate environment variables
    Returns a dictionary of environment variables with their status
    """
    env_vars = {}
    
    # Check FACE_VIEWER_DATA_DIR
    data_dir = os.getenv('FACE_VIEWER_DATA_DIR')
    if not data_dir:
        default_data_dir = os.path.join(os.getcwd(), 'data', 'responses')
        log.warning(f"FACE_VIEWER_DATA_DIR not set, using default: {default_data_dir}")
        os.environ['FACE_VIEWER_DATA_DIR'] = default_data_dir
        env_vars['FACE_VIEWER_DATA_DIR'] = {
            'value': default_data_dir,
            'status': 'default',
            'message': f"Using default data directory: {default_data_dir}"
        }
    else:
        # Check if directory exists
        if not os.path.isdir(data_dir):
            try:
                Path(data_dir).mkdir(parents=True, exist_ok=True)
                log.info(f"Created data directory: {data_dir}")
                env_vars['FACE_VIEWER_DATA_DIR'] = {
                    'value': data_dir,
                    'status': 'created',
                    'message': f"Created data directory: {data_dir}"
                }
            except Exception as e:
                log.error(f"Failed to create data directory {data_dir}: {str(e)}")
                env_vars['FACE_VIEWER_DATA_DIR'] = {
                    'value': data_dir,
                    'status': 'error',
                    'message': f"Failed to create data directory: {str(e)}"
                }
        else:
            log.info(f"Using data directory: {data_dir}")
            env_vars['FACE_VIEWER_DATA_DIR'] = {
                'value': data_dir,
                'status': 'ok',
                'message': f"Using data directory: {data_dir}"
            }
    
    # Check FLASK_SECRET_KEY or DASHBOARD_SECRET_KEY
    secret_key = os.getenv('FLASK_SECRET_KEY') or os.getenv('DASHBOARD_SECRET_KEY')
    if not secret_key:
        default_secret = os.urandom(24).hex()
        log.warning(f"Neither FLASK_SECRET_KEY nor DASHBOARD_SECRET_KEY set, using random secret")
        os.environ['DASHBOARD_SECRET_KEY'] = default_secret
        env_vars['DASHBOARD_SECRET_KEY'] = {
            'value': '[REDACTED]',
            'status': 'default',
            'message': "Using randomly generated secret key"
        }
    else:
        log.info("Secret key is set")
        env_vars['SECRET_KEY'] = {
            'value': '[REDACTED]',
            'status': 'ok',
            'message': "Secret key is set"
        }
    
    # Check R_ANALYSIS_MODE
    r_mode = os.getenv('R_ANALYSIS_MODE')
    if not r_mode:
        log.info("R_ANALYSIS_MODE not set, using Python analysis")
        env_vars['R_ANALYSIS_MODE'] = {
            'value': 'python',
            'status': 'default',
            'message': "Using Python analysis (R_ANALYSIS_MODE not set)"
        }
    else:
        if r_mode.lower() == 'r':
            log.info("Using R for analysis")
            env_vars['R_ANALYSIS_MODE'] = {
                'value': 'r',
                'status': 'ok',
                'message': "Using R for analysis"
            }
        else:
            log.info(f"Using Python analysis (R_ANALYSIS_MODE={r_mode})")
            env_vars['R_ANALYSIS_MODE'] = {
                'value': r_mode,
                'status': 'ok',
                'message': f"Using Python analysis (R_ANALYSIS_MODE={r_mode})"
            }
    
    return env_vars

def setup_environment():
    """
    Setup environment variables with defaults if not set
    """
    env_vars = check_environment()
    
    # Log environment status
    log.info("Environment setup complete")
    for var_name, var_info in env_vars.items():
        if var_info['status'] == 'error':
            log.error(f"{var_name}: {var_info['message']}")
        elif var_info['status'] == 'default':
            log.warning(f"{var_name}: {var_info['message']}")
        else:
            log.info(f"{var_name}: {var_info['message']}")
    
    return env_vars

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Check environment
    env_vars = check_environment()
    
    # Print results
    print("\nEnvironment Variable Status:")
    print("===========================")
    for var_name, var_info in env_vars.items():
        status_symbol = "✅" if var_info['status'] in ['ok', 'created'] else "⚠️" if var_info['status'] == 'default' else "❌"
        print(f"{status_symbol} {var_name}: {var_info['message']}")

"""
API Logger Middleware for Face Viewer Dashboard
Logs all API calls with request details
"""
import logging
import time
import json
from flask import request, g
from functools import wraps

# Configure logger
log = logging.getLogger('api_logger')
log.setLevel(logging.INFO)

# Add handler if not already added
if not log.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)

def log_api_call(f):
    """
    Decorator to log API calls with request details
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Start timer
        start_time = time.time()
        
        # Store request start time
        g.request_start_time = start_time
        
        # Get request details
        method = request.method
        path = request.path
        remote_addr = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Log request start
        log.info(f"API Request: {method} {path} from {remote_addr} - {user_agent}")
        
        # Log request parameters
        if request.args:
            log.info(f"Query Parameters: {dict(request.args)}")
        
        # Log request body for POST/PUT requests
        if method in ['POST', 'PUT'] and request.is_json:
            # Sanitize any sensitive data
            body = request.get_json()
            sanitized_body = sanitize_sensitive_data(body)
            log.info(f"Request Body: {sanitized_body}")
        
        # Execute the actual view function
        response = f(*args, **kwargs)
        
        # Calculate request duration
        duration = time.time() - start_time
        
        # Log response
        status_code = getattr(response, 'status_code', 200)
        log.info(f"API Response: {status_code} - Completed in {duration:.4f}s")
        
        return response
    
    return decorated_function

def sanitize_sensitive_data(data):
    """
    Sanitize sensitive data from logs
    """
    if not data:
        return data
    
    # Create a copy to avoid modifying the original
    if isinstance(data, dict):
        sanitized = data.copy()
        
        # List of sensitive fields to mask
        sensitive_fields = ['password', 'token', 'secret', 'key', 'auth']
        
        # Mask sensitive fields
        for key in sanitized:
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = '[REDACTED]'
            elif isinstance(sanitized[key], dict):
                sanitized[key] = sanitize_sensitive_data(sanitized[key])
            elif isinstance(sanitized[key], list):
                sanitized[key] = [sanitize_sensitive_data(item) if isinstance(item, dict) else item for item in sanitized[key]]
        
        return sanitized
    
    return data

def setup_api_logging(app):
    """
    Setup API logging middleware for Flask app
    """
    # Log all API requests
    @app.before_request
    def log_request_info():
        # Only log API routes
        if request.path.startswith('/api/'):
            # Start timer
            g.request_start_time = time.time()
            
            # Get request details
            method = request.method
            path = request.path
            remote_addr = request.remote_addr
            user_agent = request.headers.get('User-Agent', 'Unknown')
            
            # Log request start
            log.info(f"API Request: {method} {path} from {remote_addr} - {user_agent}")
            
            # Log request parameters
            if request.args:
                log.info(f"Query Parameters: {dict(request.args)}")
            
            # Log request body for POST/PUT requests
            if method in ['POST', 'PUT'] and request.is_json:
                try:
                    # Sanitize any sensitive data
                    body = request.get_json()
                    sanitized_body = sanitize_sensitive_data(body)
                    log.info(f"Request Body: {sanitized_body}")
                except Exception as e:
                    log.warning(f"Could not log request body: {str(e)}")
    
    # Log response details
    @app.after_request
    def log_response_info(response):
        # Only log API routes
        if request.path.startswith('/api/'):
            # Calculate request duration if start time was set
            if hasattr(g, 'request_start_time'):
                duration = time.time() - g.request_start_time
                
                # Log response
                status_code = response.status_code
                log.info(f"API Response: {status_code} - Completed in {duration:.4f}s")
                
                # Log response body for JSON responses (limited to avoid huge logs)
                if response.content_type and 'application/json' in response.content_type:
                    try:
                        response_data = json.loads(response.get_data(as_text=True))
                        # Truncate large responses
                        if isinstance(response_data, dict):
                            truncated_data = {k: str(v)[:100] + '...' if isinstance(v, str) and len(str(v)) > 100 else v 
                                            for k, v in response_data.items()}
                            log.debug(f"Response Body (truncated): {truncated_data}")
                    except Exception as e:
                        log.warning(f"Could not log response body: {str(e)}")
        
        return response
    
    return app

"""
Test script for core AdminAuth functionality
"""
import os
import sys
import json
import logging
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

# Create a minimal Flask app for testing
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test_secret_key'

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Initialize admin authentication
from admin.auth import AdminAuth
admin_auth = AdminAuth(app)

def test_create_user():
    """Test user creation functionality"""
    logger.info("Testing user creation...")
    
    # Create a test user
    username = "testuser"
    password = "testpassword"
    role = "admin"
    
    # Delete user if it already exists
    users_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'users.json')
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r') as f:
                users = json.load(f)
            if username in users:
                logger.info(f"User {username} already exists, deleting...")
                del users[username]
                with open(users_file, 'w') as f:
                    json.dump(users, f, indent=2)
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    # Create the user
    result = admin_auth.create_user(username, password, role=role)
    logger.info(f"User creation result: {result}")
    
    # Verify user was created
    try:
        with open(users_file, 'r') as f:
            users = json.load(f)
        if username in users:
            logger.info(f"User {username} exists in users.json")
            logger.info(f"User data: {users[username]}")
        else:
            logger.error(f"User {username} not found in users.json")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.error(f"Error reading users.json: {str(e)}")
    
    return result

def test_authenticate():
    """Test user authentication functionality"""
    logger.info("Testing user authentication...")
    
    # Ensure test user exists
    username = "testuser"
    password = "testpassword"
    
    # Try to authenticate
    result = admin_auth.authenticate(username, password)
    logger.info(f"Authentication result: {result}")
    
    return result

def test_is_authenticated():
    """Test authentication status check"""
    logger.info("Testing authentication status...")
    
    result = admin_auth.is_authenticated()
    logger.info(f"Is authenticated: {result}")
    
    return result

def test_current_user():
    """Test current user retrieval"""
    logger.info("Testing current user retrieval...")
    
    user = admin_auth.current_user()
    if user:
        logger.info(f"Current user: {user['username']}, role: {user['role']}")
    else:
        logger.info("No current user")
    
    return user

def test_logout():
    """Test user logout functionality"""
    logger.info("Testing user logout...")
    
    admin_auth.logout()
    is_authenticated = admin_auth.is_authenticated()
    logger.info(f"After logout, is_authenticated: {is_authenticated}")
    
    return not is_authenticated

def run_tests():
    """Run all tests"""
    logger.info("Starting AdminAuth core functionality tests")
    
    # Test user creation
    create_result = test_create_user()
    logger.info(f"User creation test {'PASSED' if create_result else 'FAILED'}")
    
    # Test authentication
    auth_result = test_authenticate()
    logger.info(f"Authentication test {'PASSED' if auth_result else 'FAILED'}")
    
    # Test authentication status
    is_auth_result = test_is_authenticated()
    logger.info(f"Authentication status test {'PASSED' if is_auth_result else 'FAILED'}")
    
    # Test current user
    user = test_current_user()
    current_user_result = user is not None
    logger.info(f"Current user test {'PASSED' if current_user_result else 'FAILED'}")
    
    # Test logout
    logout_result = test_logout()
    logger.info(f"Logout test {'PASSED' if logout_result else 'FAILED'}")
    
    # Overall result
    all_passed = create_result and auth_result and is_auth_result and current_user_result and logout_result
    logger.info(f"All tests {'PASSED' if all_passed else 'FAILED'}")
    
    return all_passed

if __name__ == "__main__":
    run_tests()

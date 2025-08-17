"""
Initialize admin user for Face Viewer Dashboard
"""
import os
import json
import hashlib
import secrets
import datetime

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_admin_user():
    """Initialize admin user"""
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Path to admin users file
    users_file = os.path.join(data_dir, 'admin_users.json')
    
    # Create default admin user
    default_password = "admin123"  # Simple password for testing
    users = {
        'admin': {
            'username': 'admin',
            'password_hash': hash_password(default_password),
            'role': 'admin',
            'created_at': datetime.datetime.now().isoformat(),
            'last_login': None
        }
    }
    
    # Save users to file
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)
    
    print(f"Created default admin user with username: admin and password: {default_password}")
    print("Please change this password after first login")
    
    # Also create permissions file
    permissions_file = os.path.join(data_dir, 'permissions.json')
    permissions = {
        'roles': {
            'admin': {
                'description': 'Administrator with full access',
                'permissions': ['*']  # Wildcard for all permissions
            },
            'researcher': {
                'description': 'Researcher with data access',
                'permissions': [
                    'view_dashboard',
                    'view_analytics',
                    'run_analysis',
                    'export_data',
                    'view_health'
                ]
            },
            'viewer': {
                'description': 'Basic viewer with limited access',
                'permissions': [
                    'view_dashboard',
                    'view_health'
                ]
            }
        },
        'permissions': {
            'view_dashboard': 'Access to view the main dashboard',
            'view_analytics': 'Access to view analytics page',
            'run_analysis': 'Ability to run statistical analyses',
            'export_data': 'Ability to export data in various formats',
            'view_health': 'Access to view system health information',
            'manage_users': 'Ability to manage user accounts',
            'manage_permissions': 'Ability to manage roles and permissions',
            'view_audit_logs': 'Access to view audit logs',
            'delete_data': 'Ability to delete data from the system'
        }
    }
    
    # Save permissions to file
    with open(permissions_file, 'w') as f:
        json.dump(permissions, f, indent=2)
    
    print("Created permissions file with default roles and permissions")

if __name__ == "__main__":
    init_admin_user()

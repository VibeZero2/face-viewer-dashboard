"""
Permissions module for Face Viewer Dashboard admin
Handles role-based access control and permissions management
"""
import os
import json
from functools import wraps
from flask import session, abort, flash

class Permissions:
    def __init__(self, app=None, permissions_file=None):
        """Initialize the permissions module"""
        self.app = app
        self.permissions_file = permissions_file or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'permissions.json')
        self._ensure_permissions_file()
        
        if app:
            self.init_app(app)
            
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
    def _ensure_permissions_file(self):
        """Ensure the permissions file exists"""
        os.makedirs(os.path.dirname(self.permissions_file), exist_ok=True)
        
        if not os.path.exists(self.permissions_file):
            # Create default permissions
            self._save_permissions({
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
            })
            
    def _load_permissions(self):
        """Load permissions from file"""
        try:
            with open(self.permissions_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'roles': {}, 'permissions': {}}
            
    def _save_permissions(self, permissions):
        """Save permissions to file"""
        with open(self.permissions_file, 'w') as f:
            json.dump(permissions, f, indent=2)
            
    def get_roles(self):
        """Get all roles"""
        permissions = self._load_permissions()
        return permissions.get('roles', {})
        
    def get_permissions(self):
        """Get all permissions"""
        permissions = self._load_permissions()
        return permissions.get('permissions', {})
        
    def get_role_permissions(self, role):
        """Get permissions for a specific role"""
        roles = self.get_roles()
        return roles.get(role, {}).get('permissions', [])
        
    def has_permission(self, permission):
        """Check if the current user has a specific permission"""
        if 'admin_role' not in session:
            return False
            
        role = session['admin_role']
        role_permissions = self.get_role_permissions(role)
        
        # Check for wildcard permission
        if '*' in role_permissions:
            return True
            
        return permission in role_permissions
        
    def add_role(self, role_name, description, permissions):
        """Add a new role"""
        all_permissions = self._load_permissions()
        
        if role_name in all_permissions['roles']:
            return False
            
        all_permissions['roles'][role_name] = {
            'description': description,
            'permissions': permissions
        }
        
        self._save_permissions(all_permissions)
        return True
        
    def update_role(self, role_name, description=None, permissions=None):
        """Update an existing role"""
        all_permissions = self._load_permissions()
        
        if role_name not in all_permissions['roles']:
            return False
            
        if description is not None:
            all_permissions['roles'][role_name]['description'] = description
            
        if permissions is not None:
            all_permissions['roles'][role_name]['permissions'] = permissions
            
        self._save_permissions(all_permissions)
        return True
        
    def delete_role(self, role_name):
        """Delete a role"""
        all_permissions = self._load_permissions()
        
        if role_name not in all_permissions['roles']:
            return False
            
        del all_permissions['roles'][role_name]
        self._save_permissions(all_permissions)
        return True
        
    def add_permission(self, permission_name, description):
        """Add a new permission"""
        all_permissions = self._load_permissions()
        
        if permission_name in all_permissions['permissions']:
            return False
            
        all_permissions['permissions'][permission_name] = description
        self._save_permissions(all_permissions)
        return True
        
    def delete_permission(self, permission_name):
        """Delete a permission"""
        all_permissions = self._load_permissions()
        
        if permission_name not in all_permissions['permissions']:
            return False
            
        # Remove from permissions list
        del all_permissions['permissions'][permission_name]
        
        # Remove from all roles
        for role in all_permissions['roles']:
            if permission_name in all_permissions['roles'][role]['permissions']:
                all_permissions['roles'][role]['permissions'].remove(permission_name)
                
        self._save_permissions(all_permissions)
        return True
        
    def permission_required(self, permission):
        """Decorator to require a specific permission for a route"""
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not self.has_permission(permission):
                    flash('You do not have permission to access this page', 'danger')
                    abort(403)
                return f(*args, **kwargs)
            return decorated_function
        return decorator

"""
Admin routes for Face Viewer Dashboard
Handles all admin-related routes and functionality
"""
import os
import json
import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, abort, send_file
from werkzeug.utils import secure_filename
from .auth import AdminAuth
from .permissions import Permissions
from .audit import AuditLog

# Create Blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize modules
from flask import current_app
admin_auth = None
permissions = None
audit_log = None

# Create a function to get permissions that will work even before initialization
def get_permissions():
    global permissions
    if permissions is None:
        from admin.permissions import Permissions
        app = current_app._get_current_object()
        permissions = Permissions(app)
    return permissions

def init_admin(app):
    """Initialize admin module with Flask app"""
    global admin_auth, permissions, audit_log
    
    admin_auth = AdminAuth(app)
    permissions = Permissions(app)
    audit_log = AuditLog(app)
    
    # Register blueprint with app
    app.register_blueprint(admin_bp)
    
    # Set up error handlers
    @admin_bp.errorhandler(403)
    def forbidden(e):
        return render_template('admin/error.html', error_code=403, error_message="Forbidden: You don't have permission to access this resource"), 403
        
    @admin_bp.errorhandler(404)
    def not_found(e):
        return render_template('admin/error.html', error_code=404, error_message="Not Found: The requested resource was not found"), 404
        
    @admin_bp.errorhandler(500)
    def server_error(e):
        return render_template('admin/error.html', error_code=500, error_message="Server Error: An internal error occurred"), 500

# Authentication routes
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login route"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if admin_auth.authenticate(username, password):
            next_url = request.args.get('next', url_for('admin.dashboard'))
            audit_log.log_action(
                action_type='authentication',
                description=f"User {username} logged in successfully"
            )
            flash('Login successful', 'success')
            return redirect(next_url)
        else:
            audit_log.log_action(
                action_type='authentication',
                description=f"Failed login attempt for user {username}",
                details={'ip_address': request.remote_addr}
            )
            flash('Invalid username or password', 'danger')
            
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout route"""
    username = session.get('admin_user', 'Unknown')
    admin_auth.logout()
    audit_log.log_action(
        action_type='authentication',
        description=f"User {username} logged out"
    )
    flash('You have been logged out', 'info')
    return redirect(url_for('admin.login'))

@admin_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate input
        if not username or not password:
            flash('Username and password are required', 'danger')
            return render_template('admin/register.html')
            
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return render_template('admin/register.html')
        
        # Create user
        if admin_auth.create_user(username, password, role='admin'):
            audit_log.log_action(
                action_type='registration',
                description=f"User {username} registered successfully"
            )
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('admin.login'))
        else:
            flash('Username already exists', 'danger')
    
    return render_template('admin/register.html')

# Dashboard routes
@admin_bp.route('/')
def dashboard():
    """Admin dashboard route"""
    # Get user count
    users = admin_auth._load_users()
    user_count = len(users)
    
    # Get last user update
    last_user = max(users.values(), key=lambda x: x.get('created_at', '')) if users else None
    last_user_update = last_user.get('created_at', 'Never') if last_user else 'Never'
    
    # Get system status
    system_status = "Healthy"
    last_health_check = datetime.datetime.now().isoformat()
    
    # Get recent activity
    logs = audit_log.get_logs(limit=10)
    recent_activity_count = len([log for log in logs if 
                               datetime.datetime.fromisoformat(log['timestamp']) > 
                               datetime.datetime.now() - datetime.timedelta(days=1)])
    
    last_activity = logs[0] if logs else None
    last_activity_time = last_activity['timestamp'] if last_activity else 'Never'
    
    return render_template('admin/dashboard.html',
                          user_count=user_count,
                          last_user_update=last_user_update,
                          system_status=system_status,
                          last_health_check=last_health_check,
                          recent_activity_count=recent_activity_count,
                          last_activity_time=last_activity_time,
                          recent_logs=logs)

# User management routes
@admin_bp.route('/users')
@get_permissions().permission_required('manage_users')
def users():
    """Admin user management route"""
    users = admin_auth._load_users()
    roles = permissions.get_roles()
    
    return render_template('admin/users.html', users=users, roles=roles.keys())

@admin_bp.route('/users/add', methods=['POST'])
@get_permissions().permission_required('manage_users')
def add_user():
    """Add a new user"""
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    if admin_auth.create_user(username, password, role):
        audit_log.log_action(
            action_type='user_management',
            description=f"Created new user: {username}",
            details={'role': role}
        )
        flash(f'User {username} created successfully', 'success')
    else:
        flash(f'Failed to create user {username}. Username may already exist.', 'danger')
        
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/edit', methods=['POST'])
@get_permissions().permission_required('manage_users')
def edit_user():
    """Edit an existing user"""
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')
    
    users = admin_auth._load_users()
    if username not in users:
        flash(f'User {username} not found', 'danger')
        return redirect(url_for('admin.users'))
        
    # Update role
    users[username]['role'] = role
    
    # Update password if provided
    if password:
        users[username]['password_hash'] = admin_auth._hash_password(password)
        
    admin_auth._save_users(users)
    
    audit_log.log_action(
        action_type='user_management',
        description=f"Updated user: {username}",
        details={'role': role, 'password_changed': bool(password)}
    )
    
    flash(f'User {username} updated successfully', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/users/delete', methods=['POST'])
@get_permissions().permission_required('manage_users')
def delete_user():
    """Delete a user"""
    username = request.form.get('username')
    
    # Prevent deleting yourself
    if username == session.get('admin_user'):
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin.users'))
        
    if admin_auth.delete_user(username):
        audit_log.log_action(
            action_type='user_management',
            description=f"Deleted user: {username}"
        )
        flash(f'User {username} deleted successfully', 'success')
    else:
        flash(f'Failed to delete user {username}', 'danger')
        
    return redirect(url_for('admin.users'))

# Roles and permissions routes
@admin_bp.route('/roles')
@get_permissions().permission_required('manage_permissions')
def roles():
    """Admin roles and permissions management route"""
    roles = permissions.get_roles()
    all_permissions = permissions.get_permissions()
    
    return render_template('admin/roles.html', roles=roles, permissions=all_permissions)

@admin_bp.route('/roles/add', methods=['POST'])
@get_permissions().permission_required('manage_permissions')
def add_role():
    """Add a new role"""
    role_name = request.form.get('role_name')
    description = request.form.get('description')
    all_permissions = request.form.get('all_permissions') == 'on'
    
    if all_permissions:
        role_permissions = ['*']
    else:
        role_permissions = request.form.getlist('permissions')
        
    if permissions.add_role(role_name, description, role_permissions):
        audit_log.log_action(
            action_type='permission_management',
            description=f"Created new role: {role_name}",
            details={'permissions': role_permissions}
        )
        flash(f'Role {role_name} created successfully', 'success')
    else:
        flash(f'Failed to create role {role_name}. Role may already exist.', 'danger')
        
    return redirect(url_for('admin.roles'))

@admin_bp.route('/roles/edit', methods=['POST'])
@get_permissions().permission_required('manage_permissions')
def edit_role():
    """Edit an existing role"""
    role_name = request.form.get('role_name')
    description = request.form.get('description')
    all_permissions = request.form.get('all_permissions') == 'on'
    
    if all_permissions:
        role_permissions = ['*']
    else:
        role_permissions = request.form.getlist('permissions')
        
    if permissions.update_role(role_name, description, role_permissions):
        audit_log.log_action(
            action_type='permission_management',
            description=f"Updated role: {role_name}",
            details={'permissions': role_permissions}
        )
        flash(f'Role {role_name} updated successfully', 'success')
    else:
        flash(f'Failed to update role {role_name}', 'danger')
        
    return redirect(url_for('admin.roles'))

@admin_bp.route('/roles/delete', methods=['POST'])
@get_permissions().permission_required('manage_permissions')
def delete_role():
    """Delete a role"""
    role_name = request.form.get('role_name')
    
    # Prevent deleting admin role
    if role_name == 'admin':
        flash('Cannot delete the admin role', 'danger')
        return redirect(url_for('admin.roles'))
        
    if permissions.delete_role(role_name):
        audit_log.log_action(
            action_type='permission_management',
            description=f"Deleted role: {role_name}"
        )
        flash(f'Role {role_name} deleted successfully', 'success')
    else:
        flash(f'Failed to delete role {role_name}', 'danger')
        
    return redirect(url_for('admin.roles'))

@admin_bp.route('/permissions/add', methods=['POST'])
@get_permissions().permission_required('manage_permissions')
def add_permission():
    """Add a new permission"""
    permission_name = request.form.get('permission_name')
    description = request.form.get('description')
    
    if permissions.add_permission(permission_name, description):
        audit_log.log_action(
            action_type='permission_management',
            description=f"Created new permission: {permission_name}"
        )
        flash(f'Permission {permission_name} created successfully', 'success')
    else:
        flash(f'Failed to create permission {permission_name}. Permission may already exist.', 'danger')
        
    return redirect(url_for('admin.roles'))

@admin_bp.route('/permissions/delete', methods=['POST'])
@get_permissions().permission_required('manage_permissions')
def delete_permission():
    """Delete a permission"""
    permission_name = request.form.get('permission_name')
    
    # Prevent deleting essential permissions
    essential_permissions = ['view_dashboard', 'manage_users', 'manage_permissions']
    if permission_name in essential_permissions:
        flash(f'Cannot delete essential permission: {permission_name}', 'danger')
        return redirect(url_for('admin.roles'))
        
    if permissions.delete_permission(permission_name):
        audit_log.log_action(
            action_type='permission_management',
            description=f"Deleted permission: {permission_name}"
        )
        flash(f'Permission {permission_name} deleted successfully', 'success')
    else:
        flash(f'Failed to delete permission {permission_name}', 'danger')
        
    return redirect(url_for('admin.roles'))

# Audit log routes
@admin_bp.route('/audit-logs')
@get_permissions().permission_required('view_audit_logs')
def audit_logs():
    """Admin audit logs route"""
    page = int(request.args.get('page', 1))
    per_page = 20
    offset = (page - 1) * per_page
    
    # Get filter parameters
    action_type = request.args.get('action_type')
    user = request.args.get('user')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Get logs with filters
    logs = audit_log.get_logs(
        limit=per_page,
        offset=offset,
        action_type=action_type,
        user=user,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get total count for pagination
    all_logs = audit_log.get_logs(
        limit=10000,  # Large number to get all logs
        action_type=action_type,
        user=user,
        start_date=start_date,
        end_date=end_date
    )
    total_logs = len(all_logs)
    total_pages = (total_logs + per_page - 1) // per_page
    
    # Get unique action types and users for filters
    action_types = audit_log.get_action_types()
    users_list = audit_log.get_users()
    
    return render_template('admin/audit_logs.html',
                          logs=logs,
                          page=page,
                          total_pages=total_pages,
                          action_types=action_types,
                          users_list=users_list)

@admin_bp.route('/api/logs/<log_id>')
@get_permissions().permission_required('view_audit_logs')
def get_log_details(log_id):
    """API endpoint to get log details"""
    log = audit_log.get_log_by_id(log_id)
    if log:
        return jsonify(log)
    else:
        return jsonify({'error': 'Log not found'}), 404

@admin_bp.route('/export-logs')
@get_permissions().permission_required('view_audit_logs')
def export_logs():
    """Export audit logs to CSV"""
    # Get filter parameters
    action_type = request.args.get('action_type')
    user = request.args.get('user')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Create temporary file for CSV export
    export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    export_file = os.path.join(export_dir, f'audit_logs_{timestamp}.csv')
    
    # Export logs to CSV
    count = audit_log.export_logs_csv(
        export_file,
        action_type=action_type,
        user=user,
        start_date=start_date,
        end_date=end_date
    )
    
    audit_log.log_action(
        action_type='data_export',
        description=f"Exported {count} audit logs to CSV",
        details={
            'filters': {
                'action_type': action_type,
                'user': user,
                'start_date': start_date,
                'end_date': end_date
            }
        }
    )
    
    return send_file(export_file, as_attachment=True, download_name=f'audit_logs_{timestamp}.csv')

# Settings routes
@admin_bp.route('/settings')
@get_permissions().permission_required('manage_users')
def settings():
    """Admin settings route"""
    # Load settings from file
    settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'settings.json')
    
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    else:
        # Default settings
        settings = {
            'site_title': 'Face Viewer Dashboard',
            'session_timeout': 120,
            'maintenance_mode': False,
            'force_ssl': False,
            'enable_2fa': False,
            'max_login_attempts': 5,
            'data_directory': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'),
            'backup_directory': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups'),
            'auto_backup': True,
            'backup_frequency': 7,
            'r_path': '',
            'spss_path': '',
            'enable_r_analytics': True,
            'enable_spss_export': True
        }
        
        # Save default settings
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
    
    return render_template('admin/settings.html', settings=settings)

@admin_bp.route('/settings/update', methods=['POST'])
@get_permissions().permission_required('manage_users')
def update_settings():
    """Update admin settings"""
    settings_type = request.form.get('settings_type')
    settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'settings.json')
    
    # Load current settings
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    else:
        settings = {}
    
    # Update settings based on type
    if settings_type == 'general':
        settings['site_title'] = request.form.get('site_title')
        settings['session_timeout'] = int(request.form.get('session_timeout'))
        settings['maintenance_mode'] = request.form.get('maintenance_mode') == 'on'
    elif settings_type == 'security':
        settings['force_ssl'] = request.form.get('force_ssl') == 'on'
        settings['enable_2fa'] = request.form.get('enable_2fa') == 'on'
        settings['max_login_attempts'] = int(request.form.get('max_login_attempts'))
    elif settings_type == 'data':
        settings['data_directory'] = request.form.get('data_directory')
        settings['backup_directory'] = request.form.get('backup_directory')
        settings['auto_backup'] = request.form.get('auto_backup') == 'on'
        settings['backup_frequency'] = int(request.form.get('backup_frequency'))
    elif settings_type == 'analytics':
        settings['r_path'] = request.form.get('r_path')
        settings['spss_path'] = request.form.get('spss_path')
        settings['enable_r_analytics'] = request.form.get('enable_r_analytics') == 'on'
        settings['enable_spss_export'] = request.form.get('enable_spss_export') == 'on'
    
    # Save updated settings
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)
    
    audit_log.log_action(
        action_type='settings_update',
        description=f"Updated {settings_type} settings",
        details={k: v for k, v in request.form.items() if k != 'settings_type'}
    )
    
    flash(f'{settings_type.capitalize()} settings updated successfully', 'success')
    return redirect(url_for('admin.settings'))

# Health check route
@admin_bp.route('/health')
def health():
    """Admin health check route"""
    # Get system health information
    health_info = {
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'python_version': os.sys.version,
        'disk_usage': {
            'total': 0,
            'used': 0,
            'free': 0
        },
        'memory_usage': {
            'total': 0,
            'used': 0,
            'free': 0
        }
    }
    
    # Try to get disk usage
    try:
        import shutil
        disk = shutil.disk_usage('/')
        health_info['disk_usage'] = {
            'total': disk.total,
            'used': disk.used,
            'free': disk.free
        }
    except:
        pass
    
    # Try to get memory usage
    try:
        import psutil
        memory = psutil.virtual_memory()
        health_info['memory_usage'] = {
            'total': memory.total,
            'used': memory.used,
            'free': memory.available
        }
    except:
        pass
    
    return jsonify(health_info)

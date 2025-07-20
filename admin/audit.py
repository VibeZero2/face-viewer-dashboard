"""
Audit logging module for Face Viewer Dashboard admin
Records and manages audit logs for security and compliance
"""
import os
import json
import datetime
import uuid
import csv
from flask import request, session

class AuditLog:
    def __init__(self, app=None, log_file=None):
        """Initialize the audit logging module"""
        self.app = app
        self.log_file = log_file or os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'audit_log.json')
        self._ensure_log_file()
        
        if app:
            self.init_app(app)
            
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        
        # Set up request handlers for automatic logging
        @app.before_request
        def before_request():
            # Skip logging for static files and certain paths
            if request.path.startswith('/static/') or request.path == '/favicon.ico':
                return
                
            # Log admin actions only
            if request.path.startswith('/admin/') and session.get('admin_user'):
                self.log_action(
                    action_type='page_view',
                    description=f"Viewed {request.path}",
                    details={
                        'method': request.method,
                        'path': request.path,
                        'remote_addr': request.remote_addr
                    }
                )
                
    def _ensure_log_file(self):
        """Ensure the log file exists"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)
                
    def _load_logs(self):
        """Load logs from file"""
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
            
    def _save_logs(self, logs):
        """Save logs to file"""
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=2)
            
    def log_action(self, action_type, description, details=None):
        """Log an action"""
        logs = self._load_logs()
        
        log_entry = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.datetime.now().isoformat(),
            'user': session.get('admin_user', 'system'),
            'action_type': action_type,
            'description': description,
            'details': details or {},
            'ip_address': request.remote_addr if request else None
        }
        
        logs.append(log_entry)
        self._save_logs(logs)
        return log_entry
        
    def get_logs(self, limit=100, offset=0, action_type=None, user=None, start_date=None, end_date=None):
        """Get logs with optional filtering"""
        logs = self._load_logs()
        
        # Apply filters
        if action_type:
            logs = [log for log in logs if log['action_type'] == action_type]
            
        if user:
            logs = [log for log in logs if log['user'] == user]
            
        if start_date:
            start_date = datetime.datetime.fromisoformat(start_date)
            logs = [log for log in logs if datetime.datetime.fromisoformat(log['timestamp']) >= start_date]
            
        if end_date:
            end_date = datetime.datetime.fromisoformat(end_date)
            logs = [log for log in logs if datetime.datetime.fromisoformat(log['timestamp']) <= end_date]
            
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Apply pagination
        return logs[offset:offset + limit]
        
    def get_log_by_id(self, log_id):
        """Get a specific log entry by ID"""
        logs = self._load_logs()
        for log in logs:
            if log['id'] == log_id:
                return log
        return None
        
    def get_action_types(self):
        """Get all unique action types"""
        logs = self._load_logs()
        return list(set(log['action_type'] for log in logs))
        
    def get_users(self):
        """Get all unique users"""
        logs = self._load_logs()
        return list(set(log['user'] for log in logs))
        
    def export_logs_csv(self, output_file, action_type=None, user=None, start_date=None, end_date=None):
        """Export logs to CSV file"""
        logs = self.get_logs(limit=10000, action_type=action_type, user=user, 
                            start_date=start_date, end_date=end_date)
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow(['ID', 'Timestamp', 'User', 'Action Type', 'Description', 'IP Address'])
            
            # Write data
            for log in logs:
                writer.writerow([
                    log['id'],
                    log['timestamp'],
                    log['user'],
                    log['action_type'],
                    log['description'],
                    log['ip_address'] or 'N/A'
                ])
                
        return len(logs)
        
    def clear_logs(self, before_date=None):
        """Clear logs, optionally before a specific date"""
        if before_date is None:
            # Clear all logs
            self._save_logs([])
            return True
            
        logs = self._load_logs()
        before_date = datetime.datetime.fromisoformat(before_date)
        
        # Keep only logs after the specified date
        new_logs = [log for log in logs if datetime.datetime.fromisoformat(log['timestamp']) > before_date]
        
        self._save_logs(new_logs)
        return len(logs) - len(new_logs)  # Return number of deleted logs

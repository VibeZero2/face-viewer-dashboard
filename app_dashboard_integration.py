"""
Dashboard integration code for Face Viewer Dashboard
Import this in your main app.py to integrate dashboard components
"""

def integrate_dashboard(app):
    """
    Integrate dashboard components into the Flask app
    
    Args:
        app: Flask application instance
    """
    # Import dashboard blueprint
    from routes.dashboard import dashboard_bp
    
    # Register blueprint
    app.register_blueprint(dashboard_bp)
    
    # Add URL rule for convenience
    app.add_url_rule('/dashboard', 'dashboard', 
                    dashboard_bp.view_functions['dashboard'])
    
    # Configure app settings for caching
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    
    return app

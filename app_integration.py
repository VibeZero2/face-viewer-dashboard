"""
Integration code for Face Viewer Dashboard
Import this in your main app.py to integrate all components
"""

def integrate_participant_management(app):
    """
    Integrate participant management components into the Flask app
    
    Args:
        app: Flask application instance
    """
    # Import blueprints
    from routes.participants import participants_bp
    from routes.consent import consent_bp
    
    # Register blueprints
    app.register_blueprint(participants_bp)
    app.register_blueprint(consent_bp)
    
    # Add URL rules for convenience
    app.add_url_rule('/participants', 'participants_list', 
                    participants_bp.view_functions['participants_list'])
    app.add_url_rule('/participant/<pid>', 'participant_detail', 
                    participants_bp.view_functions['participant_detail'])
    app.add_url_rule('/admin/delete', 'admin_delete_participant', 
                    participants_bp.view_functions['admin_delete_participant'], 
                    methods=['POST'])
    app.add_url_rule('/consent', 'consent', 
                    consent_bp.view_functions['consent'])
    app.add_url_rule('/submit_consent', 'submit_consent', 
                    consent_bp.view_functions['submit_consent'], 
                    methods=['POST'])
    
    # Add a placeholder study start route if it doesn't exist
    if 'study.start' not in app.view_functions:
        @app.route('/study/start')
        def study_start():
            from flask import render_template, session
            participant_id = session.get('participant_id', 'Unknown')
            return render_template('study_start.html', participant_id=participant_id)
        
    return app

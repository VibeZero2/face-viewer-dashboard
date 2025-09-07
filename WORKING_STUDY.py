#!/usr/bin/env python3
"""
WORKING_STUDY.py - Simple HTTP server for the facial trust study
This is a backup/alternative way to run the study if the main Flask app has issues.
"""

import http.server
import socketserver
import os
import json
from datetime import datetime
import urllib.parse

# Configuration
PORT = 3000
STUDY_DIR = "../facial-trust-study"

class StudyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STUDY_DIR, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.path = '/templates/index.html'
        elif self.path == '/consent':
            self.path = '/templates/consent.html'
        elif self.path == '/instructions':
            self.path = '/templates/instructions.html'
        elif self.path == '/task':
            self.path = '/templates/task.html'
        elif self.path == '/survey':
            self.path = '/templates/survey.html'
        elif self.path == '/done':
            self.path = '/templates/done.html'
        
        return super().do_GET()
    
    def do_POST(self):
        if self.path == '/submit_response':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Simple response saving (basic implementation)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/responses/participant_{timestamp}.csv"
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Save basic data
            with open(filename, 'w') as f:
                f.write("participant_id,response,timestamp\n")
                f.write(f"{data.get('participant_id', ['unknown'])[0]},{data.get('response', [''])[0]},{timestamp}\n")
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')
        else:
            super().do_POST()

if __name__ == "__main__":
    print(f"Starting study server on port {PORT}")
    print(f"Serving from directory: {STUDY_DIR}")
    print(f"Study accessible at: http://localhost:{PORT}")
    
    with socketserver.TCPServer(("", PORT), StudyHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down study server...")
            httpd.shutdown()
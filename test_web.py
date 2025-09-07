#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import threading
import time

PORT = 8080

class TestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            response = f"""
            <html>
            <head><title>Web Server Test</title></head>
            <body>
            <h1>Web Server is Working!</h1>
            <p>Port: {PORT}</p>
            <p>If you can see this, web servers work on this system.</p>
            <p>Time: {time.strftime('%H:%M:%S')}</p>
            </body>
            </html>
            """
            self.wfile.write(response.encode())
        else:
            super().do_GET()

def open_browser():
    time.sleep(1)
    webbrowser.open(f'http://localhost:{PORT}')

if __name__ == "__main__":
    print(f"Starting test web server on port {PORT}...")
    print(f"URL: http://localhost:{PORT}")
    
    # Open browser automatically
    threading.Thread(target=open_browser, daemon=True).start()
    
    with socketserver.TCPServer(("", PORT), TestHandler) as httpd:
        print(f"Server started at http://localhost:{PORT}")
        httpd.serve_forever()

import socket
import sys
import os

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def main():
    port = 8080
    print(f"Checking if port {port} is in use...")
    
    if is_port_in_use(port):
        print(f"ERROR: Port {port} is already in use by another process!")
        print("Please close any applications that might be using this port.")
        print("Common applications that use port 8080:")
        print("- Other Flask applications")
        print("- Apache Tomcat")
        print("- Development servers")
        return False
    else:
        print(f"SUCCESS: Port {port} is available!")
        return True

if __name__ == "__main__":
    if main():
        print("\nStarting a test Flask server on port 8080...")
        try:
            from flask import Flask
            app = Flask(__name__)
            
            @app.route('/')
            def hello():
                return "Port 8080 test successful!"
            
            print("Flask is available and the server is starting...")
            print("=" * 50)
            print(f"Test server will be available at: http://localhost:8080")
            print("=" * 50)
            
            # Only run for 10 seconds as a test
            app.run(host='0.0.0.0', port=8080, debug=False)
        except ImportError:
            print("ERROR: Flask is not installed. Please install it with:")
            print("pip install flask")
        except Exception as e:
            print(f"ERROR starting Flask: {str(e)}")
    
    input("\nPress Enter to exit...")

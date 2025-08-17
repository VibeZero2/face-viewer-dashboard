import os
import sys
from app import app

if __name__ == '__main__':
    print("Starting server on port 8080...")
    print("Access the dashboard at: http://localhost:8080")
    app.run(host='localhost', port=8080, debug=True)

#!/usr/bin/env python3
import os
import sys
import traceback

print("Starting debug script...")

try:
    print("Importing app...")
    import app
    print("App imported successfully")
    
    print("Checking app object...")
    print(f"App type: {type(app.app)}")
    print(f"App name: {app.app.name}")
    
    print("Setting up environment...")
    os.environ["PORT"] = "5001"
    port = int(os.environ.get("PORT", 5001))
    print(f"Port: {port}")
    
    print("Starting Flask app...")
    app.app.run(host="127.0.0.1", port=port, debug=False)
    
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
    sys.exit(1)

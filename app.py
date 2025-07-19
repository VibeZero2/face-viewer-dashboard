"""
Face Viewer Dashboard - Simple App Wrapper
This file serves as a wrapper to import the simplified app without pandas dependencies.
"""
# Import everything from the simple app
from simple import *

# This ensures that if anything imports from app.py, it gets the pandas-free version
print("Using simplified app without pandas dependencies")

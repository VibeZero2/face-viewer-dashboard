"""
Face Viewer Dashboard - App Wrapper
This file serves as a wrapper to import the pandas-enabled app.
"""
# Import everything from the pandas-enabled app
from app_with_pandas import *

# This ensures that if anything imports from app.py, it gets the pandas-enabled version
print("Using app with pandas dependencies")

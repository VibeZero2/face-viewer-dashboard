#!/bin/bash
# Simple clean build script for Face Viewer Dashboard with pandas support
set -x  # Print each command for debugging
set -e  # Exit on error

echo "===== CLEAN BUILD INFO ====="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version 2>&1)"
echo "Pip version: $(pip --version 2>&1)"

# Update pip
echo "Updating pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Clean build completed successfully!"

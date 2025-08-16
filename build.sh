#!/bin/bash
# Simple build script for Face Viewer Dashboard with pandas support
set -x  # Print each command for debugging
set -e  # Exit on error

echo "===== BUILD INFO ====="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version 2>&1)"
echo "Pip version: $(pip --version 2>&1)"

# Ensure data directory exists
echo "Ensuring data directory structure exists..."
mkdir -p "$(pwd)/data/responses"
touch "$(pwd)/data/responses/.gitkeep"

# Ensure static directory exists
echo "Ensuring static directory exists..."
mkdir -p "$(pwd)/static"
touch "$(pwd)/static/.gitkeep"

# Update pip
echo "Updating pip..."
pip install --upgrade pip

# Explicitly install build dependencies first
echo "Explicitly installing build dependencies..."
pip install setuptools==69.0.3 wheel==0.42.0
pip install meson-python==0.15.0 ninja==1.11.1

# Install dependencies from requirements.txt
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Explicitly install pandas
echo "Explicitly installing pandas..."
pip install pandas==2.0.3

echo "Build completed successfully!"

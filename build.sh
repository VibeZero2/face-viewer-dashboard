#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "Starting build process for Face Viewer Dashboard..."

# Update pip first
echo "Updating pip..."
pip install --upgrade pip

# Install core dependencies explicitly
echo "Installing core dependencies explicitly..."
pip install pandas==2.0.3
pip install Flask==2.3.3
pip install gunicorn==21.2.0

# Install all other dependencies
echo "Installing remaining dependencies..."
pip install -r requirements.txt

echo "Verifying pandas installation..."
pip show pandas

echo "Build completed successfully!"

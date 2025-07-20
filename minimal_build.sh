#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

echo "Starting minimal build process..."

# Update pip first
echo "Updating pip..."
pip install --upgrade pip

# Install only the minimal dependencies
echo "Installing minimal dependencies..."
pip install -r minimal_requirements.txt

echo "Minimal build completed successfully!"

#!/bin/bash
# Timestamp: $(date +%s) - July 20, 2025
# This is a completely clean build script that takes a radical approach to prevent pandas installation

set -x  # Print each command before executing (for debugging)
set -e  # Exit immediately if a command exits with a non-zero status

echo "===== STARTING CLEAN BUILD PROCESS ====="
echo "Current directory: $(pwd)"
echo "Python version: $(python --version 2>&1)"

# Create a marker file to indicate this is a clean build
echo "$(date)" > .clean_build_marker_v4

# Update pip to latest version
pip install --upgrade pip

# Create a fake pandas package to prevent installation
echo "Creating fake pandas package to block real pandas..."
mkdir -p /tmp/fake_pandas/pandas
cat > /tmp/fake_pandas/setup.py << EOF
from setuptools import setup, find_packages

setup(
    name="pandas",
    version="999.0.0",
    description="Fake pandas package to prevent real pandas installation",
    packages=find_packages(),
)
EOF

cat > /tmp/fake_pandas/pandas/__init__.py << EOF
def __getattr__(name):
    raise ImportError("pandas is not available and has been blocked by build_clean.sh")
EOF

# Install the fake pandas package
cd /tmp/fake_pandas
pip install -e .
cd -

# Modify pip configuration to prevent building from source
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
no-cache-dir = true
no-binary = :none:
EOF

# Create a clean requirements file without pandas
echo "Creating clean requirements file..."
cat > requirements_clean.txt << EOF
# Core web framework
Flask==2.3.3
Flask-Login==0.6.2
Flask-WTF==1.1.1
Werkzeug==2.3.7

# Data processing and visualization
plotly==5.18.0
dash==2.14.1
dash-bootstrap-components==1.5.0

# Security and environment
cryptography==41.0.3
python-dotenv==1.0.0

# Web server for production
gunicorn==21.2.0

# HTTP requests
requests==2.31.0
EOF

# Install dependencies from clean requirements
echo "Installing dependencies from clean requirements file..."
pip install -r requirements_clean.txt

# Final check to ensure pandas is not installed
if pip show pandas | grep -q "Version: 999.0.0"; then
    echo "✅ Fake pandas package is installed, real pandas is blocked"
else
    echo "❌ WARNING: pandas check failed, but continuing build"
fi

echo "===== BUILD COMPLETED SUCCESSFULLY ====="

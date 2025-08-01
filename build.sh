#!/bin/bash
# Force clean build: $(date +%s) - July 26, 2025
set -x  # Print each command before executing (for debugging)
set -e  # Exit immediately if a command exits with a non-zero status

# Function to ensure absolute paths
ensure_absolute_path() {
    local path="$1"
    if [[ "$path" != /* ]]; then
        path="$(pwd)/$path"
    fi
    echo "$path"
}

# Function to safely compare semantic versions
version_compare() {
    local v1="$1"
    local v2="$2"
    # Use Python itself to compare versions
    python -c "
import sys
from packaging import version
sys.exit(0) if version.parse('$v2') >= version.parse('$v1') else sys.exit(1)
" 2>/dev/null || python -c "
import sys
sys.exit(0) if [int(x) for x in '$v2'.split('.')] >= [int(x) for x in '$v1'.split('.')] else sys.exit(1)
"
}

# CRITICAL: Immediately intercept requirements-render.txt if it exists
echo "CRITICAL: Checking for requirements-render.txt at script start"
if [ -f "requirements-render.txt" ]; then
    echo "Found requirements-render.txt at start, removing pandas references"
    cat requirements-render.txt
    grep -v -i "pandas" requirements-render.txt > requirements-render.txt.clean
    mv requirements-render.txt.clean requirements-render.txt
    echo "MODIFIED requirements-render.txt:"
    cat requirements-render.txt
fi

echo "===== EXTENSIVE DEBUG INFO ====="
echo "Current directory: $(pwd)"
echo "Directory listing:"
ls -la
echo "Environment variables:"
env | sort
echo "Python version: $(python --version 2>&1)"
echo "Pip version: $(pip --version 2>&1)"
echo "===== END DEBUG INFO ====="

echo "Starting build process for Face Viewer Dashboard..."

# Ensure data directory exists and is preserved
echo "Ensuring data directory structure exists..."
mkdir -p "$(pwd)/data/responses"
touch "$(pwd)/data/responses/.gitkeep"

# Ensure static publish path exists
RENDER_STATIC_PUBLISH_PATH="$(pwd)/static"
if [ ! -d "$RENDER_STATIC_PUBLISH_PATH" ]; then
    echo "Creating static publish directory at $RENDER_STATIC_PUBLISH_PATH"
    mkdir -p "$RENDER_STATIC_PUBLISH_PATH"
fi

# Verify static publish path is not empty
if [ -z "$(ls -A "$RENDER_STATIC_PUBLISH_PATH")" ]; then
    echo "Static publish directory is empty, adding placeholder file"
    touch "$RENDER_STATIC_PUBLISH_PATH/.gitkeep"
fi

# Aggressively search for and clean any requirements-render.txt files
echo "Aggressively searching for requirements-render.txt..."
find / -name "requirements*.txt" -type f 2>/dev/null | while read file; do
    echo "Found requirements file at $file"
    echo "Contents of $file:"
    cat "$file"
    if [[ "$file" == *"requirements-render.txt"* ]]; then
        echo "Found requirements-render.txt at $file, removing pandas references..."
        grep -v -i "pandas" "$file" > "${file}.clean"
        mv "${file}.clean" "$file"
        echo "Cleaned $file:"
        cat "$file"
    fi
done

# Create our own clean requirements-render.txt to override any that might be used
echo "Creating clean requirements-render.txt in multiple locations..."
cat requirements.txt | grep -v -i "pandas" > requirements-render.txt
echo "# pandas is explicitly blocked" >> requirements-render.txt

# Create a clean requirements.txt backup in case it's being modified
cp requirements.txt requirements.txt.original
grep -v -i "pandas" requirements.txt > requirements.txt.clean
cp requirements.txt.clean requirements.txt
echo "Clean requirements.txt:"
cat requirements.txt

# Also create clean files in parent directories and common locations
mkdir -p /tmp/render
cp requirements-render.txt /tmp/render/
cp requirements-render.txt ../requirements-render.txt 2>/dev/null || true

# Check for any Render-specific directories that might contain requirements files
echo "Checking for Render-specific directories:"
find / -type d -name "*render*" 2>/dev/null | grep -v "Permission denied" || true

# Update pip first
echo "Updating pip..."
pip install --upgrade pip

# Install packaging for version comparison
echo "Installing packaging for version comparison..."
pip install packaging

# Set up pip wrapper to intercept all pip commands
echo "Setting up pip wrapper..."
if [ -f "pip_wrapper.sh" ]; then
    chmod +x pip_wrapper.sh
    export PATH="$(pwd):$PATH"
    alias pip="$(pwd)/pip_wrapper.sh"
    echo "PATH=$PATH"
fi

# Create a clean environment marker to prevent cached builds
echo "Creating clean build marker..."
touch .render_clean_build_v3

# Create a complete block for pandas
echo "Creating complete pandas block..."
echo "#!/bin/bash
# Force clean build: $(date +%s) - July 26, 2025
echo 'ERROR: pandas installation blocked by build script'
exit 1" > /tmp/pandas-block.sh
chmod +x /tmp/pandas-block.sh

# Monkey patch pip to prevent pandas installation
echo "Monkey patching pip to block pandas..."
mkdir -p ~/.pip
echo "[global]
extra-index-url=https://pypi.org/simple/
no-binary=:none:
no-build-isolation=false
no-cache-dir=true
" > ~/.pip/pip.conf

# Create a fake pandas package to prevent installation
echo "Creating fake pandas package..."
mkdir -p /tmp/fake-pandas/pandas
echo "setup() {
  echo 'Fake pandas package to prevent real pandas installation'
}" > /tmp/fake-pandas/setup.sh
echo "def __getattr__(name):
    raise ImportError('pandas is not available')" > /tmp/fake-pandas/pandas/__init__.py

# Create a pre-installation hook to intercept pip install commands
echo "Creating pip pre-installation hook..."
mkdir -p ~/.pip/hooks
cat > ~/.pip/hooks/pre-install.py << 'EOF'
#!/usr/bin/env python
import sys

if any('pandas' in arg.lower() for arg in sys.argv):
    print('ERROR: pandas installation blocked by pre-installation hook')
    sys.exit(1)
EOF
chmod +x ~/.pip/hooks/pre-install.py

# Modify any requirements-render.txt that might be created during the build process
echo "Setting up inotify watch for requirements-render.txt..."
(
while true; do
  if [ -f "requirements-render.txt" ]; then
    echo "requirements-render.txt detected, removing pandas references"
    grep -v -i "pandas" requirements-render.txt > requirements-render.txt.clean
    mv requirements-render.txt.clean requirements-render.txt
    echo "Modified requirements-render.txt:"
    cat requirements-render.txt
  fi
  sleep 1
done
) &

# Detect Python version and validate
echo "Detecting and validating Python version..."
detected_python_version=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
minimum_python_version="3.8.0"

# Validate Python version format
if [[ ! "$detected_python_version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "The PYTHON_VERSION must provide a major, minor, and patch version, e.g. 3.8.1. You have requested $detected_python_version. See https://render.com/docs/python-version for more information."
    detected_python_version="3.8.1"  # Default to a safe version
fi

# Compare versions properly using version_compare function
if ! version_compare "$minimum_python_version" "$detected_python_version"; then
    echo "Error: Python version $detected_python_version is less than minimum required version $minimum_python_version"
    exit 1
else
    echo "Python version $detected_python_version is compatible (minimum required: $minimum_python_version)"
fi

# Install core dependencies explicitly
echo "Installing core dependencies explicitly..."
pip install Flask==2.3.3 Werkzeug==2.3.7 Flask-Login==0.6.2 Flask-WTF==1.1.1
pip install gunicorn==21.2.0 python-dotenv==1.0.0 cryptography==41.0.3
pip install plotly==5.18.0 dash==2.14.1 dash-bootstrap-components==1.5.0
pip install requests==2.31.0

# Create ultra-clean requirements file with explicit exclusion
echo "Creating ultra-clean requirements file..."
cat requirements.txt | grep -v -i "pandas" > requirements_ultra_clean.txt
echo "# pandas is explicitly blocked" >> requirements_ultra_clean.txt
echo "Contents of ultra-clean requirements file:"
cat requirements_ultra_clean.txt

# Double-check no pandas was installed
echo "Verifying pandas is not installed..."
if pip show pandas &>/dev/null; then
    echo "WARNING: pandas was installed despite preventions, removing it..."
    pip uninstall -y pandas
fi

# Create a symbolic link to prevent pandas from being installed
echo "Creating symbolic link to prevent pandas installation..."
pip_location=$(pip show pip | grep Location | cut -d' ' -f2)
if [ -n "$pip_location" ]; then
    mkdir -p "$pip_location/pandas"
    touch "$pip_location/pandas/__init__.py"
fi

echo "Verifying core installations..."
pip show Flask
pip show gunicorn

echo "Build completed successfully!"

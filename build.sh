#!/bin/bash
# Install dependencies from the Render-specific requirements file
pip install -r requirements-render.txt
# Also install from the regular requirements file
pip install -r requirements.txt
# Explicitly install gunicorn to ensure it's available
pip install gunicorn==21.2.0

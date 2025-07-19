#!/bin/bash
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Files in directory: $(ls -la)"
echo "Python files: $(find . -name "*.py")"
echo "Starting gunicorn..."
gunicorn app_wsgi:application

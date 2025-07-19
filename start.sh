#!/bin/bash
# Start the application using gunicorn
gunicorn wsgi:application

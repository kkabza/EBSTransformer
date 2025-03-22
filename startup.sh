#!/bin/bash
echo "Starting ESB Transformer application..."
cd /home/site/wwwroot
echo "Current directory: $(pwd)"
echo "Listing files:"
ls -la

# Run diagnostics
echo "Running diagnostics..."
python prestart.py

# Start Gunicorn
echo "Starting Gunicorn server..."
gunicorn --bind=0.0.0.0:8000 --log-level debug app:app 
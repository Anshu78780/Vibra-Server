#!/usr/bin/env bash
# Start script for Render deployment

# Use Gunicorn for production serving
exec gunicorn --config gunicorn_config.py app:app

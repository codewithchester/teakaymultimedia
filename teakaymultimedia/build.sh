#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Collect static files (CSS/JS/images → staticfiles/)
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Create superuser if it doesn't exist (optional, requires env vars)
# python manage.py createsuperuser --no-input || true
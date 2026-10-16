#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser if it doesn't exist (uses DJANGO_SUPERUSER_* env vars)
python manage.py createsuperuser --noinput || true
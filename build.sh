#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

cd Website/myproject
python manage.py collectstatic --noinput
python manage.py migrate 
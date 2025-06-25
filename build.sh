#!/usr/bin/env bash
# exit on error
set -o errexit

# Run the cache clearing script
./clear-build-cache.sh

pip install -r requirements.txt

cd Website/myproject
python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate 
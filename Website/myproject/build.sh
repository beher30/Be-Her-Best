#!/usr/bin/env bash
# exit on error
set -o errexit

# Run the cache clearing script
./clear-build-cache.sh

pip install -r ../../requirements.txt


python manage.py collectstatic --noinput
python manage.py migrate 
cd ..
python myproject/myapp/create_superuser.py 
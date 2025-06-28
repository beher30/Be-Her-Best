FROM python:3.11

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Then copy the rest of the project
COPY . .

# Change to the Django project directory (where manage.py is)
WORKDIR /app/Website/myproject

# Now that we are in the right directory, run collectstatic
RUN python manage.py collectstatic --noinput

# The command to run the app is relative to the current WORKDIR
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"] 
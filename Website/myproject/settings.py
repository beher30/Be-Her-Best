import os
from pathlib import Path
import dj_database_url

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'unsafe-secret-key')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
# Allow both the specific Render domain and all .onrender.com subdomains
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'be-her-best-1.onrender.com,.onrender.com').split(',')

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise for static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Database
DATABASES = {
    'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
} 
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
if not User.objects.filter(username="beherbest").exists():
    User.objects.create_superuser("beherbest", "beherbest@gmail.com", "beherbestfuck")
    print("Superuser created.")
else:
    print("Superuser already exists.") 
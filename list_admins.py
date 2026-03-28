import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mocktest.settings')
django.setup()

from django.contrib.auth.models import User
from django.db.models import Q

users = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True))
for u in users:
    print(f"Username: {u.username}, Superuser: {u.is_superuser}, Staff: {u.is_staff}")

if not users.exists():
    print("No admin or staff users found.")
    all_users = User.objects.all()
    if all_users.exists():
        print("Existing users:")
        for u in all_users:
            print(f"- {u.username}")
    else:
        print("No users found at all.")

import os
import sys
import django

# Django environment setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Admin user mavjudligini tekshirish
if not User.objects.filter(is_superuser=True).exists():
    print("Superuser yaratilmoqda...")
    User.objects.create_superuser(
        username='admin',
        email='admin@admin.com',
        password='admin123'
    )
    print("+ Superuser yaratildi: admin/admin123")
else:
    print("+ Superuser allaqachon mavjud")
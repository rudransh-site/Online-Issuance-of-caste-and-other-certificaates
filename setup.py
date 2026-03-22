"""
Run this ONCE to set up the database and create the default admin account.
Usage:  python setup.py
"""
import os
import sys
import subprocess

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

def run(cmd):
    print(f"\n>>> {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"ERROR running: {cmd}")
        sys.exit(1)

print("="*60)
print("  Certificate Monitoring System — Setup")
print("="*60)

run("python manage.py makemigrations users")
run("python manage.py makemigrations applications")
run("python manage.py makemigrations automation")
run("python manage.py makemigrations admin_panel")
run("python manage.py migrate")

print("\n>>> Creating default admin account...")
import django
django.setup()
from users.models import User

if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser(
        username='admin',
        password='admin123',
        email='admin@cms.gov.in',
        first_name='Revenue',
        last_name='Admin',
        role='ADMIN'
    )
    print("  Admin created: username=admin  password=admin123")
else:
    print("  Admin already exists.")

print("\n" + "="*60)
print("  Setup complete! Run the server with:")
print("  python manage.py runserver")
print("\n  Login credentials:")
print("  Admin:   admin / admin123")
print("="*60)

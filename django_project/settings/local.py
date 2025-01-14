from .base import *

DEBUG = True #determines if local (dev) mode.


ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'columbary_db',  # Replace with your database name
        'USER': 'root',              # Replace with your MySQL username
        'PASSWORD': 'root',  # Replace with your MySQL password
        'HOST': '127.0.0.1',          # Use '127.0.0.1' or your database host
        'PORT': '3306',               # Default MySQL port
    }
}

# Local static and media file settings
STATICFILES_DIRS = [BASE_DIR / 'static']
from django.apps import AppConfig


class PagesConfig(AppConfig):
    name = "pages"

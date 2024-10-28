from .base import *

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1']

# Production database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'your_db_host',
        'PORT': 'your_db_port',
    }
}

# Static files (production)
STATIC_ROOT = '/var/www/your_static_files/'
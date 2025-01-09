from .base import *

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1']

# Production database settings
DATABASES = { #hosted somewhere else
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
        'OPTIONS': {
            "read_default_file": ".venv/my.cnf"  
        }
    }
}

# Static files (production)
STATIC_ROOT = '/var/www/your_static_files/'
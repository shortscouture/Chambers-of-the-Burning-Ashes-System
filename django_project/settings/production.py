from .base import *

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1']

# Production database settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'testDB',
        'USER': 'admin',
        'PASSWORD': 'admin',
        'HOST': 'localhost',
        'PORT': '',
        'OPTIONS': {
            'unix_socket': '/var/run/mysqld/mysqld.sock',
        },
    }
}

# Static files (production)
STATIC_ROOT = '/var/www/your_static_files/'
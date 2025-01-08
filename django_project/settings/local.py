from .base import *

DEBUG = True #determines if local (dev) mode.


ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Development database
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

# Local static and media file settings
STATICFILES_DIRS = [BASE_DIR / 'static']

from .base import *

DEBUG = True #determines if local (dev) mode.


ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Development database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'testdb.sqlite3',
    }
}
# Local static and media file settings
STATICFILES_DIRS = [BASE_DIR / 'static']

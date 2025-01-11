from .base import *

DEBUG = True #determines if local (dev) mode.


ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = { 
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'localhost',
        'OPTIONS': {
            "read_default_file": ".venv/my.cnf"  
        }
    }
}
# Local static and media file settings
STATICFILES_DIRS = [BASE_DIR / 'static']

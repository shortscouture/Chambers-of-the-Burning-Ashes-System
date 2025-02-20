from .base import *
DEBUG = True #determines if local (dev) mode.


ALLOWED_HOSTS = ["127.0.0.1"]
 
DATABASES = {
    'default': {
        'NAME': env('DB_NAME'),
        'ENGINE': 'django.db.backends.mysql',  # Change to your DB engine (e.g., MySQL)
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),  # Remote DB Host
        'PORT': env('DB_PORT'),
    }
}
EMAIL_BACKEND = env('EMAIL_BACKEND')
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = 587 #gmail port
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
ADMIN_EMAIL = env('ADMIN_EMAIL')

# Local static and media file settings
STATICFILES_DIRS = [BASE_DIR / 'static']
from django.apps import AppConfig


class PagesConfig(AppConfig):
    name = "pages"
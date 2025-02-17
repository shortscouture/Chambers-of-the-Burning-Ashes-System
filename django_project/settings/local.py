from .base import *
import environ

DEBUG = True #determines if local (dev) mode.


ALLOWED_HOSTS = ['localhost', '127.0.0.1']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # Change to your DB engine
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),  # Remote DB Host
        'PORT': env('DB_PORT', default='5432'),
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'stalphonsusmakati@gmail.com'
EMAIL_HOST_PASSWORD = 'wcvy daru objs fgwi'
DEFAULT_FROM_EMAIL = 'stalphonsusmakati@gmail.com'
ADMIN_EMAIL = 'jamesnaldo376@gmail.com'

# Local static and media file settings
STATICFILES_DIRS = [BASE_DIR / 'static']
from django.apps import AppConfig


class PagesConfig(AppConfig):
    name = "pages"
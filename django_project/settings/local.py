from .base import *
import environ

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")  # Ensure your .env file is read


DEBUG = True #determines if local (dev) mode.


ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  
        'NAME': env('DB_NAME', default='fallback_db_name'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env.int('DB_PORT', default=3306),  # Convert to integer
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
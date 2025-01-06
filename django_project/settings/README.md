MUST DO WHEN INITIALIZING IN A NEW LOCAL ENVIRONMENT:
1. Install django-environ.
2. Create .env file in your root folder (where manage.py resides)
3. Paste this line to your .env file:
SECRET_KEY= 'your_secret_key'
DEBUG=True 
4. You can set environment variable on local machine using terminal:
Windows
    - set SECRET_KEY=your-secret-key
macOS/Linux
    - export SECRET_KEY=your-secret-key

NOTE: .env is already configured to be used by base.py 


To generate SECRET_KEY:
1. run django shell:
    - python manage.py shell
2. Execute following commands:
    from django.core.management.utils import get_random_secret_key
    secret_key = get_random_secret_key()
    print(secret_key)
3. Copy generated key to local machine AND .env file.

NOTE: Don't forget to put .env in your .gitignore file.


If switching to production or local, simply change

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings.local")  to .local or .production



"""WSGI entry point (used when you deploy the site)."""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "smartlend.settings")
application = get_wsgi_application()

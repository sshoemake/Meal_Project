import os 
from .base import *
from .base import BASE_DIR


SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DEBUG = True

# Use localhost and 127.0.0.1 for development
CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
]

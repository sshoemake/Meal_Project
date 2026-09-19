import os

from .base import *

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', "change_me")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DEBUG = True

# Use localhost and 127.0.0.1 for development
CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "http://127.0.0.1",
]

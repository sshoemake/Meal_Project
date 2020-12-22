from .defaults import *

import json

import os

# with open("/etc/config.json") as config_file:
#    config = json.load(config_file)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG')

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "meal_project",
        "USER": "root",
        "PASSWORD": "somewordpress",
        "HOST": "db",
        "PORT": "3306",
    }
}

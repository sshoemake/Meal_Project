from .defaults import *

import json


with open("/etc/config.json") as config_file:
    config = json.load(config_file)


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config["SECRET_KEY"]


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False


ALLOWED_HOSTS = ["192.168.0.33", "odroidn2.local", "sshoemake.com"]


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "meal_project",
        "USER": "root",
        "PASSWORD": config.get("ROOT_PASS"),
        "HOST": "172.18.0.2",
        "PORT": "3306",
    }
}

from .defaults import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "hk8t!=&di$k*dnu&9!$gh#=2iz#zj6(#$o*ga%@s5osc#1b$s%"


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


ALLOWED_HOSTS = []


# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        # "NAME": "/app/db.sqlite3"
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

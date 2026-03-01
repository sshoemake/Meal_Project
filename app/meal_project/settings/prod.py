import os 
from .base import *  # noqa: F403,F405

def parse_trusted_origins(raw_origins, default_scheme="http://"):
    """
    Converts a comma-separated string into a list of origins with schemes.
    Adds default_scheme if missing.
    Filters out empty strings.
    """
    return [
        o if o.startswith(("http://", "https://")) else f"{default_scheme}{o}"
        for o in (origin.strip() for origin in raw_origins.split(","))
        if o
    ]


SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()]
if not ALLOWED_HOSTS:
    raise RuntimeError("DJANGO_ALLOWED_HOSTS must be set in production")

# Read comma-separated trusted origins from environment variable
raw_origins = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = parse_trusted_origins(raw_origins, default_scheme="https://")

if not CSRF_TRUSTED_ORIGINS:
    raise RuntimeError(
        "DJANGO_CSRF_TRUSTED_ORIGINS must be set in production"
    )

DEBUG = os.getenv("DJANGO_DEBUG", "True") == "True"

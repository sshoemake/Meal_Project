import os

from .base import *


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


def env_bool(name, default):
    """Parse an env var as a boolean with a sane fallback."""
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",") if h.strip()
]
if not ALLOWED_HOSTS:
    raise RuntimeError("DJANGO_ALLOWED_HOSTS must be set in production")

# Read comma-separated trusted origins from environment variable
raw_origins = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "")
CSRF_TRUSTED_ORIGINS = parse_trusted_origins(raw_origins, default_scheme="https://")

if not CSRF_TRUSTED_ORIGINS:
    raise RuntimeError("DJANGO_CSRF_TRUSTED_ORIGINS must be set in production")

# NOTE: fail closed - DEBUG only turns on when explicitly enabled.
DEBUG = env_bool("DJANGO_DEBUG", False)

# Production security settings. All are env-overridable with secure defaults
# so `manage.py check --deploy` reflects real production behavior.
SESSION_COOKIE_SECURE = env_bool("DJANGO_SESSION_COOKIE_SECURE", True)
CSRF_COOKIE_SECURE = env_bool("DJANGO_CSRF_COOKIE_SECURE", True)
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", True)
SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD", True)
SECURE_REFERRER_POLICY = os.getenv("DJANGO_SECURE_REFERRER_POLICY", "same-origin")
SECURE_CROSS_ORIGIN_OPENER_POLICY = os.getenv(
    "DJANGO_SECURE_CROSS_ORIGIN_OPENER_POLICY", "same-origin"
)
# Traffic arrives from Traefik, which sets this header on TLS-terminated requests.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

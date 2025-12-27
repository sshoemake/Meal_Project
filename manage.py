#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(
            f"Python 3.12 required, found {sys.version.split()[0]}"
        )

    """Run administrative tasks."""
    # Use environment variable if set, fallback to dev settings
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.meal_project.settings.dev")
    
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
#!/bin/sh

set -e

python manage.py makemigrations --noinput
python manage.py migrate

python manage.py collectstatic --noinput

exec "$@"

#python manage.py runserver 0.0.0.0:8000
#uwsgi --http :8000 --master --enable-threads --module meal_project.wsgi

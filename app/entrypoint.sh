#!/bin/sh

set -e

if [ "$DATABASE" = "mysql" ]
then
    echo "Waiting for mysql..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 1
    done

    echo "mysql started"
fi

python manage.py makemigrations --noinput
python manage.py migrate

python manage.py collectstatic --noinput

exec "$@"

#python manage.py runserver 0.0.0.0:8000
#uwsgi --http :8000 --master --enable-threads --module meal_project.wsgi

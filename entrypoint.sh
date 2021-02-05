#!/bin/bash -x

python manage.py makemigrations
python manage.py flush --no-input
python manage.py migrate
python manage.py loaddata fixtures.json
python manage.py collectstatic --no-input

exec "$@"
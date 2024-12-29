#!/usr/bin/env bash
set -e

# TODO:  wait to db here

echo "Preparing Django Application"

# static files
poetry run python src/manage.py collectstatic --settings=core.settings.production --no-input --ignore=node_modules --ignore=*.scss --ignore=*.json --ignore=vite.config.js

# Create super user
# Password is set in the env file. variable DJANGO_SUPERUSER_PASSWORD 
if [ "$DEBUG" == "true" ]; then
    poetry run python src/manage.py createsuperuser --username=admin --email=admin@admin.com --no-input --setting=core.settings.production || true
fi

# database
poetry run python src/manage.py migrate

exec "$@"
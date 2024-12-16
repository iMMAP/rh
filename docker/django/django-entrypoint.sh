#!/usr/bin/env bash
set -e

# TODO:  wait to db here

echo "Preparing Django Application"

# static files
make collectstatic settings=core.settings.production
echo "DEBUG: $DEBUG"
make npm-build
# rm -rf src/static/node_modules

# Create super user
# Password is set in the env file. variable DJANGO_SUPERUSER_PASSWORD 
poetry run python src/manage.py createsuperuser --username=admin --email=admin@admin.com --no-input --setting=core.settings.production || true

# database
make migrate

exec "$@"
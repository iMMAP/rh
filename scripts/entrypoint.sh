#!/usr/bin/env bash
set -e

echo "Apply database migrations"
make migrate &

exec "$@"

# RUN_MANAGE_PY='poetry run python -m rh.manage'

# echo 'Collecting static files...'
# $RUN_MANAGE_PY collectstatic --no-input

# echo 'Running migrations...'
# $RUN_MANAGE_PY migrate --no-input

# exec poetry run manage.py rh.core.wsgi:application -p 8000 -b 0.0.0.0

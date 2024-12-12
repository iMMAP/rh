#!/usr/bin/env bash
set -e

# TODO:  wait to db here

echo "Preparing Django Application"

# static files
make collectstatic settings=core.settings.production
make npm-build

# database
make migrate

exec "$@"
#!/usr/bin/env bash
set -e

echo "Preparing Django Application"

# static files
make collectstatic settings=core.settings.production
make npm-build

# database
make migrate

exec "$@"
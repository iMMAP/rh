#!/bin/sh

# Debugging and error handling
set -e

# Create challenges directory if it doesn't exist
mkdir -p /etc/letsencrypt/challenges

# Print environment variables for debugging
echo "HTTPS_HOST: $HTTPS_HOST"
echo "ADMIN_EMAIL: $ADMIN_EMAIL"

# Validate required environment variables
if [ -z "$HTTPS_HOST" ] || [ -z "$ADMIN_EMAIL" ]; then
    echo "Error: HTTPS_HOST and ADMIN_EMAIL must be set"
    exit 1
fi

# Initial certificate generation
if [ ! -f "/etc/letsencrypt/live/$HTTPS_HOST/fullchain.pem" ]; then

    certbot certonly \
        --webroot \
        --webroot-path=/etc/letsencrypt/challenges \
        --non-interactive \
        --agree-tos \
        --email "$ADMIN_EMAIL" \
        -d "$HTTPS_HOST"

fi

# Continuous renewal loop
while true; do
    echo "Attempting certificate renewal"

    certbot renew \
        --webroot \
        --webroot-path=/etc/letsencrypt/challenges \
        --non-interactive \
        --quiet

    sleep 12h
done
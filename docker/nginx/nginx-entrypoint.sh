#!/bin/sh

# Exit script in case of error
set -e

# We make the config dir
mkdir -p "/etc/letsencrypt/autoissued"

echo "Creating autoissued certificates for HTTP host"
if [ ! -f "/etc/letsencrypt/autoissued/privkey.pem" ] || [ "$(find /etc/letsencrypt/autoissued/privkey.pem -mtime +365 -print)" ]; then
        echo "Autoissued certificate does not exist or is too old, we generate one"
        mkdir -p "/etc/letsencrypt/autoissued"
        openssl req -x509 -nodes -days 1825 -newkey rsa:2048 -keyout "/etc/letsencrypt/autoissued/privkey.pem" -out "/etc/letsencrypt/autoissued/fullchain.pem" -subj "/CN=${HTTP_HOST:-null}" 
else
        echo "Autoissued certificate already exists"
fi


echo "Creating symbolic link for HTTPS certificate"

rm -f /certificate_symlink

if [ -n "$HTTPS_HOST" ] && [ -f "/etc/letsencrypt/live/$HTTPS_HOST/fullchain.pem" ] && [ -f "/etc/letsencrypt/live/$HTTPS_HOST/privkey.pem" ]; then
        echo "Certbot certificate exists, we symlink to the live cert"
        ln -sf /etc/letsencrypt/live/$HTTPS_HOST /certificate_symlink
else
        echo "Certbot certificate does not exist, we symlink to autoissued"
        ln -sf /etc/letsencrypt/autoissued /certificate_symlink
fi

# Run the CMD exec nginx -g 'daemon off;'
exec nginx -g 'daemon off;'
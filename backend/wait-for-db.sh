#!/bin/sh
until mysqladmin ping -h"$MYSQL_HOST" -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" --silent; do
    echo "Esperando a que MySQL esté listo..."
    sleep 2
done
exec "$@"
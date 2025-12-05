#!/bin/bash
set -e

echo "🔄 Esperando a que la base de datos esté lista..."
until python << END
import sys
import psycopg2
try:
    conn = psycopg2.connect(
        dbname="${MYSQL_DATABASE}",
        user="${MYSQL_USER}",
        password="${MYSQL_PASSWORD}",
        host="${MYSQL_HOST}",
        port="${MYSQL_PORT}"
    )
    conn.close()
    sys.exit(0)
except psycopg2.OperationalError:
    sys.exit(1)
END
do
  echo "⏳ Base de datos no disponible - reintentando en 2 segundos..."
  sleep 2
done

echo "✅ Base de datos conectada"

echo "🔄 Ejecutando migraciones..."
python manage.py migrate --noinput

echo "🔄 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "🚀 Iniciando servidor..."
exec "$@"

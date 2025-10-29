#!/bin/bash
set -euxo pipefail

echo "==> Django Pre-Start Script"

# Create persistent dirs
/bin/mkdir -p /app/persistent/db
/bin/mkdir -p /app/persistent/media
/bin/chown -R appuser:appuser /app/persistent

# Run migrations
echo "==> Running database migrations..."

[ -f "/app/persistent/db/db.sqlite3" ] && DB_INIT=false || DB_INIT=true

DJANGO_SETTINGS_MODULE="config.settings" /opt/venv/bin/python \
    manage.py migrate --noinput

if [ "$DB_INIT" = true ]; then
    DJANGO_SETTINGS_MODULE="config.settings" DJANGO_SUPERUSER_PASSWORD=easyappzadmin /opt/venv/bin/python \
        manage.py createsuperuser --noinput --username admin --email admin@easyappz.ru
fi

echo "==> Pre-start script completed successfully!"

exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

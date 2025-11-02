#!/bin/bash
set -euxo pipefail

echo "==> Pre-Start Script"

# Create persistent dirs (for future use, e.g., uploads)
/bin/mkdir -p /app/persistent/db
/bin/mkdir -p /app/persistent/media
/bin/chown -R appuser:appuser /app/persistent

echo "==> Starting services via supervisord"
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

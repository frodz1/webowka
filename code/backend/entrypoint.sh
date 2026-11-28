#!/bin/sh
set -e

if [ "$APP_ENV" = "production" ]; then
  case "$DATABASE_URL" in
    *sslmode=require*|*sslmode=verify-ca*|*sslmode=verify-full*) ;;
    *) echo "DATABASE_URL w produkcji musi wymagać TLS (sslmode=require)." >&2; exit 1 ;;
  esac
fi

# Tworzy tabele (idempotentnie), czekając aż Postgres będzie gotowy.
python -m app.init_db

exec gunicorn --bind 0.0.0.0:5000 --workers "${WEB_CONCURRENCY:-3}" \
  --worker-tmp-dir /tmp --access-logfile - "app:create_app()"

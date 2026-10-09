#!/bin/sh
set -e

# Tworzy tabele (idempotentnie), czekając aż Postgres będzie gotowy.
python -m app.init_db

exec gunicorn --bind 0.0.0.0:5000 --workers "${WEB_CONCURRENCY:-3}" --access-logfile - "app:create_app()"

#!/bin/sh
set -e

echo "Running migrations..."
alembic -c alembic/alembic.ini upgrade head

echo "Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8080

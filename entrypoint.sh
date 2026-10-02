#!/bin/sh
set -eu

echo "Running Alembic migrations..."
python -m alembic upgrade head

echo "Starting FleetOps API..."
exec python -m uvicorn fleetops.services.api.main:app --host 0.0.0.0 --port 8001

#!/bin/bash
set -e

echo "==========================================";
echo "MiniBiblio FastAPI Startup"
echo "==========================================="

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "✓ PostgreSQL is ready"

# Run database migrations
echo "Running database migrations..."
uv run alembic upgrade head
echo "✓ Migrations complete"

# Create default admin user if none exists
echo "Checking for admin user..."
uv run python api/scripts/create_admin.py

echo "==========================================="
echo "Starting FastAPI server..."
echo "==========================================="

# Execute the main command
exec "$@"

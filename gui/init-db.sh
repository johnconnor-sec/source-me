#!/bin/bash
# init-db.sh

# Wait for PostgreSQL to start
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "localhost" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"
PGPASSWORD=$POSTGRES_PASSWORD psql -h "localhost" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c 'CREATE EXTENSION vector;'
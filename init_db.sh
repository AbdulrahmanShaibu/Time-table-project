#!/usr/bin/env bash
set -e

# This script attempts to initialize DB and seed minimal data.
# When using docker-compose the MySQL image automatically runs schema.sql.
# Use this script if you prefer to run schema manually (e.g., local MySQL or remote).

: "${DB_HOST:=localhost}"
: "${DB_PORT:=3306}"
: "${DB_USER:=school_admin}"
: "${DB_PASSWORD:=school_password}"
: "${DB_NAME:=school_timetable}"

echo "Initializing database ${DB_NAME} on ${DB_HOST}:${DB_PORT} ..."

# Wait for mysql to be ready (useful in docker)
for i in {1..30}; do
  if mysqladmin ping -h"${DB_HOST}" -P"${DB_PORT}" --silent; then
    echo "MySQL is up"
    break
  fi
  echo "Waiting for MySQL... (${i})"
  sleep 2
done

# Execute schema if present
if [ -f "./schema.sql" ]; then
  echo "Applying schema.sql..."
  mysql -h"${DB_HOST}" -P"${DB_PORT}" -u"${DB_USER}" -p"${DB_PASSWORD}" < schema.sql
  echo "Schema applied."
else
  echo "schema.sql not found!"
  exit 1
fi

echo "Done."

echo "IMPORTANT: Default admin credentials (if used) should be changed immediately."

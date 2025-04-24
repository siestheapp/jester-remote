#!/bin/bash

# Load environment variables
set -a
source .env
set +a

# Create dumps directory if it doesn't exist
mkdir -p data/db/dumps

# Get current timestamp in different formats
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
READABLE_DATE=$(date '+%Y-%m-%d %H:%M:%S %Z')

# Parse DATABASE_URL using regex
if [[ $DATABASE_URL =~ postgresql\+asyncpg://([^:]+):([^@]+)@([^:]+):([^/]+)/([^?]+) ]]; then
    DB_USER="${BASH_REMATCH[1]}"
    DB_PASS="${BASH_REMATCH[2]}"
    DB_HOST="${BASH_REMATCH[3]}"
    DB_PORT="${BASH_REMATCH[4]}"
    DB_NAME="${BASH_REMATCH[5]}"
else
    echo "Error: Could not parse DATABASE_URL"
    exit 1
fi

# Set PGPASSWORD environment variable
export PGPASSWORD="${DB_PASS}"

# Create a single full dump with header comment
(
cat << EOF
-- Database Dump
-- Generated on: ${READABLE_DATE}
-- Database: ${DB_NAME}
-- Host: ${DB_HOST}
--
-- This file contains a complete database dump from the Jester application
-- including both schema and data.
--

EOF

pg_dump \
    --host "${DB_HOST}" \
    --port "${DB_PORT}" \
    --username "${DB_USER}" \
    --dbname "${DB_NAME}" \
    --no-owner \
    --no-privileges \
    --disable-triggers
) > "data/db/dumps/dump_${TIMESTAMP}.sql"

# Unset PGPASSWORD for security
unset PGPASSWORD

echo "Database dump created successfully on ${READABLE_DATE}:"
echo "- Full dump: data/db/dumps/dump_${TIMESTAMP}.sql" 
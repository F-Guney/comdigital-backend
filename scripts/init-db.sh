#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE comdigital_test;
    GRANT ALL PRIVILEGES ON DATABASE comdigital_test TO comdigital;
EOSQL
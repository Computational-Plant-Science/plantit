#!/bin/bash
# create-dagster-databases.sh

set -e

run_db="$1"
event_db="$2"
schedule_db="$3"

PGPASSWORD=$SQL_PASSWORD psql -h $SQL_HOST -U $SQL_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$run_db'" | grep -q 1 || PGPASSWORD=$SQL_PASSWORD psql -h $SQL_HOST -U $SQL_USER -tc "CREATE DATABASE $run_db"
PGPASSWORD=$SQL_PASSWORD psql -h $SQL_HOST -U $SQL_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$event_db'" | grep -q 1 || PGPASSWORD=$SQL_PASSWORD psql -h $SQL_HOST -U $SQL_USER -tc "CREATE DATABASE $event_db"
PGPASSWORD=$SQL_PASSWORD psql -h $SQL_HOST -U $SQL_USER -tc "SELECT 1 FROM pg_database WHERE datname = '$schedule_db'" | grep -q 1 || PGPASSWORD=$SQL_PASSWORD psql -h $SQL_HOST -U $SQL_USER -tc "CREATE DATABASE $schedule_db"

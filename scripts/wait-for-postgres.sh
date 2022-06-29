#!/bin/bash
# wait-for-postgres.sh

set -e

host="$1"
user="$2"
shift
cmd="$@"

until PGPASSWORD=$SQL_PASSWORD psql -h "$host" -U "$user" -c '\q'; do
  >&2 echo "Postgres is unavailable, sleeping for 1 second"
  sleep 1
done

>&2 echo "Postgres is up, executing command"
exec $cmd


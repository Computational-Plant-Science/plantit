#!/bin/bash

DOCKER_COMPOSE="docker-compose -f docker-compose.yml -f docker-compose.dev.yml"

# Bring containers down
$DOCKER_COMPOSE down

# Remove migrations
find . -path "./django/**/migrations/*.py" -not -name "__init__.py" -delete

# Remove files
rm -rf django/files/*
mkdir -p django/files/public
mkdir -p django/files/tmp

# Build containers
$DOCKER_COMPOSE build "$@"

# Start Postgres
$DOCKER_COMPOSE up -d postgres

# Run migrations
$DOCKER_COMPOSE run djangoapp /code/dev/wait-for-postgres.sh postgres python manage.py makemigrations
$DOCKER_COMPOSE run djangoapp python manage.py migrate

# Configure defaults
< dev/setup_defaults.py $DOCKER_COMPOSE run djangoapp python manage.py shell

# Start mock IRODS server and cluster
$DOCKER_COMPOSE up -d irods
$DOCKER_COMPOSE up -d ssh

# Configure mock IRODS server
$DOCKER_COMPOSE exec ssh /bin/bash /root/wait-for-it.sh irods:1247 -- /root/irods_setup.sh

# Stop containers
$DOCKER_COMPOSE stop

# Build front end
cd django/front_end || exit
npm install
npm run build
cd ../..

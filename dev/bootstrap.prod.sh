#!/bin/bash

DOCKER_COMPOSE="docker-compose -f docker-compose.yml -f docker-compose.prod.yml"

# Build front end
cd django/front_end || exit
npm install
npm run build
cd ../..

# Collect static files
$DOCKER_COMPOSE run djangoapp ./manage.py collectstatic --no-input

# Remove migrations
find . -path "./django/**/migrations/*.py" -not -name "__init__.py" -delete

# Run migrations
$DOCKER_COMPOSE -f docker-compose.yml -f docker-compose.prod.yml run djangoapp /code/dev/wait-for-postgres.sh postgres ./manage.py makemigrations
$DOCKER_COMPOSE -f docker-compose.yml -f docker-compose.prod.yml run djangoapp ./manage.py migrate

# Create Django superuser
$DOCKER_COMPOSE -f docker-compose.yml -f docker-compose.prod.yml run djangoapp ./manage.py createsuperuser

# Stop containers
$DOCKER_COMPOSE stop

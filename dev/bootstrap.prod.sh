#!/bin/bash

DOCKER_COMPOSE="docker-compose -f docker-compose.yml -f docker-compose.prod.yml"

echo "Bringing containers down..."
$DOCKER_COMPOSE down

echo "Building front end..."
cd plantit/front_end || exit
npm install
npm run build
cd ../..

echo "Collecting static files..."
$DOCKER_COMPOSE run plantit ./manage.py collectstatic --no-input

echo "Running migrations..."
$DOCKER_COMPOSE run plantit /code/dev/wait-for-postgres.sh postgres ./manage.py makemigrations
$DOCKER_COMPOSE run plantit ./manage.py migrate

echo "Creating superuser (default values should be changed before deploying to production!)..."
$DOCKER_COMPOSE run plantit /code/dev/configure-superuser.sh -u "admin" -p "admin" -e "admin@example.com"

echo "Stopping containers..."
$DOCKER_COMPOSE stop

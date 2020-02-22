#!/bin/bash

#
# Resets everything back to a "Fresh" install by:
#   - rebuilding all docker images
#   - deleting all docker volumes
#   - removing all django migrations
# then rebuilds the images and runs initial django migration and
#  creates an admin user:
#      username: admin
#      pass: admin
#  as well as a default cluster and executor that ssh into the ssh docker cluster
#


DOCKER_COMPOSE="docker-compose -f docker-compose.yml -f compose-dev.yml"

# Bring containers down
$DOCKER_COMPOSE down

# Remove Django migrations
find . -path "./django/**/migrations/*.py" -not -name "__init__.py" -delete

# Remove Django files
rm -rf django/files/*
mkdir -p django/files/public
mkdir -p django/files/tmp

# Build containers
$DOCKER_COMPOSE build "$@"

# Start database and wait for it to come online
$DOCKER_COMPOSE up -d db-dev
echo "Waiting 30s for database to warm up..."
sleep 30s

# Run Django migrations
$DOCKER_COMPOSE run djangoapp python manage.py makemigrations
$DOCKER_COMPOSE run djangoapp python manage.py migrate

# Add some defaults to the server
< dev/setup_defaults.py $DOCKER_COMPOSE run djangoapp python manage.py shell

# Start mock irods and cluster and wait for them to come online
$DOCKER_COMPOSE up -d irods
$DOCKER_COMPOSE up -d ssh
echo "Waiting 30s for irods and ssh to warm up..."
sleep 30s

# Configure irods
$DOCKER_COMPOSE exec ssh /bin/bash /root/irods_setup.sh

# Bring containers down
$DOCKER_COMPOSE down

# Build front end
cd django/front_end
npm install
npm run build
cd ../..

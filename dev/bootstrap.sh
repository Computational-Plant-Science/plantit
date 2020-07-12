#!/bin/bash

nocache=0

while getopts 'n' opt; do
    case $opt in
        n) nocache=1 ;;
        *) echo 'Error in command line parsing' >&2
           exit 1
    esac
done
shift "$(( OPTIND - 1 ))"

echo "Bootstrapping ${PWD##*/}..."

DOCKER_COMPOSE="docker-compose -f docker-compose.yml -f docker-compose.dev.yml"

echo "Bringing containers down..."
$DOCKER_COMPOSE down

env_file=".env"
echo "Checking for environment variable file '$env_file'..."
if [ ! -f $env_file ]; then
  echo "Environment variable file '$env_file' does not exist. Creating it..."
  chmod +x dev/create-env-file.sh
  ./dev/create-env-file.sh
else
  echo "Environment variable file '$env_file' already exists. Continuing..."
fi

echo "Building front end..."
cd plantit/front_end || exit
npm install
npm run build
cd ../..

echo "Removing migrations..."
find . -path "./plantit/**/migrations/*.py" -not -name "__init__.py" -delete

echo "Removing files..."
rm -rf plantit/files/*
mkdir -p plantit/files/public
mkdir -p plantit/files/tmp

if [[ "$nocache" -eq 0 ]]; then
  echo "Building containers..."
  $DOCKER_COMPOSE build "$@"
else
  echo "Building containers with option '--no-cache'..."
  $DOCKER_COMPOSE build "$@" --no-cache
fi
$DOCKER_COMPOSE up -d plantit

echo "Running migrations..."
$DOCKER_COMPOSE exec plantit /code/dev/wait-for-postgres.sh postgres python manage.py makemigrations
$DOCKER_COMPOSE exec plantit python manage.py migrate

echo "Creating superuser..."
admin_password=$(cut -d '=' -f 2 <<< "$(grep "DJANGO_ADMIN_PASSWORD" "$env_file")" )
admin_username=$(cut -d '=' -f 2 <<< "$(grep "DJANGO_ADMIN_USERNAME" "$env_file")" )
$DOCKER_COMPOSE exec plantit /code/dev/configure-superuser.sh -u "$admin_username" -p "$admin_password" -e "admin@example.com"

echo "Configuring mock cluster and IRODS..."
$DOCKER_COMPOSE up -d irods
$DOCKER_COMPOSE up -d cluster
$DOCKER_COMPOSE exec cluster /bin/bash /root/wait-for-it.sh irods:1247 -- /root/configure-irods.sh
if [ -f config/ssh/known_hosts ]; then
  touch config/ssh/known_hosts
fi
$DOCKER_COMPOSE exec plantit bash -c "ssh-keyscan -H cluster >> /code/config/ssh/known_hosts"
if [ ! -f config/ssh/id_rsa.pub ]; then
  ssh-keygen -b 2048 -t rsa -f config/ssh/id_rsa -N ""
fi
$DOCKER_COMPOSE exec plantit bash -c "/code/dev/ssh-copy-id.expect"

echo "Stopping containers..."
$DOCKER_COMPOSE stop
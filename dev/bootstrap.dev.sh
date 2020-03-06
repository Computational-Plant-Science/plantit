#!/bin/bash

echo "Bootstrapping [DEVELOPMENT] environment..."

DOCKER_COMPOSE="docker-compose -f docker-compose.yml -f docker-compose.dev.yml"

echo "Bringing containers down..."
$DOCKER_COMPOSE down

env_file=".env"
echo "Checking for environment variable file '$env_file'..."
if [ ! -f $env_file ]; then
  echo "Environment variable file '$env_file' does not exist. Creating it..."
  cat <<EOT >>$env_file
VUE_APP_TITLE=plantit
NODE_ENV=development
DJANGO_SETTINGS_MODULE=plantit.settings
DJANGO_SECRET_KEY=some_secret_key
DJANGO_DEBUG=True
DJANGO_FIELD_ENCRYPTION_KEY=some_encryption_key
DJANGO_API_URL=http://localhost/apis/v1/
DJANGO_ALLOWED_HOSTS=*
SQL_ENGINE=django.db.backends.postgresql
SQL_HOST=postgres
SQL_PORT=5432
SQL_NAME=postgres
SQL_USER=postgres
SQL_PASSWORD=some_password
EOT
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

echo "Building containers..."
$DOCKER_COMPOSE build "$@"

echo "Running migrations..."
$DOCKER_COMPOSE up -d --remove-orphans postgres
$DOCKER_COMPOSE run plantit /code/dev/wait-for-postgres.sh postgres python manage.py makemigrations
$DOCKER_COMPOSE run plantit python manage.py migrate

echo "Creating superuser..."
$DOCKER_COMPOSE run plantit /code/dev/configure-superuser.sh -u "admin" -p "admin" -e "admin@example.com" -v

echo "Configuring mock IRODS..."
$DOCKER_COMPOSE up -d irods
$DOCKER_COMPOSE up -d ssh
$DOCKER_COMPOSE exec ssh /bin/bash /root/wait-for-it.sh irods:1247 -- /root/configure-irods.sh

echo "Stopping containers..."
$DOCKER_COMPOSE stop


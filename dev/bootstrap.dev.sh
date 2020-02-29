#!/bin/bash

DOCKER_COMPOSE="docker-compose -f docker-compose.yml -f docker-compose.dev.yml"

# Bring containers down
$DOCKER_COMPOSE down

# Create `.env` if it doesn't exist
if [ ! -f .env ]; then
  echo "Environment variable file '.env' does not exist; creating it..."
  cat <<EOT >>.env
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
fi

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
$DOCKER_COMPOSE <dev/setup_defaults.py run djangoapp python manage.py shell

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

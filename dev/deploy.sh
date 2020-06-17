#!/bin/bash

host="$1"
compose="docker-compose -f docker-compose.yml -f docker-compose.prod.yml"
env_file=".env"
dagster_config_file="plantit/dagster.yaml"

echo "Bringing containers down..."
$compose down

echo "Pulling changes..."
git stash
git pull

echo "Checking for environment variable file '$env_file'..."
if [ ! -f $env_file ]; then
  echo "Environment variable file '$env_file' does not exist. Creating it..."
  chmod +x dev/create-env-file.sh
  ./dev/create-env-file.sh
else
  echo "Environment variable file '$env_file' already exists. Continuing..."
fi

echo "Checking for dagster config file '$dagster_config_file'..."
if [ ! -f $dagster_config_file ]; then
  echo "Dagster config file '$dagster_config_file' does not exist. Creating it..."
  chmod +x dev/create-dagster-config-file.sh
  ./dev/create-dagster-config-file.sh
else
  echo "Dagster config file '$dagster_config_file' already exists. Continuing..."
fi

echo "Building front end..."
cd plantit/front_end || exit
npm install
npm run build
cd ..
cd ..

echo "Collecting static files..."
$compose run plantit ./manage.py collectstatic --no-input

echo "Running migrations..."
$compose run plantit /code/dev/wait-for-postgres.sh postgres ./manage.py makemigrations
$compose run plantit ./manage.py migrate

echo "Configuring NGINX..."
find config/nginx/conf.d/local.conf -type f -exec sed -i "s/localhost/$host/g" {} \;

echo "Configuring environment variables..."
find .env -type f -exec sed -i "s/DJANGO_API_URL=http:\/\/plantit\/apis\/v1\//DJANGO_API_URL=http:\/\/$host\/apis\/v1\//g" {} \;
find .env -type f -exec sed -i "s/DJANGO_DEBUG=True/DJANGO_DEBUG=False/g" {} \;
find .env -type f -exec sed -i "s/NODE_ENV=development/NODE_ENV=production/g" {} \;

echo "Bringing containers up..."
$compose up -d
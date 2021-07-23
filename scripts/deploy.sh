#!/bin/bash

echo "Deploying $config..."
config="$1"
host="$2"
email="$3"
compose="docker-compose -f docker-compose.$config.yml"

echo "Bringing containers down..."
$compose down --remove-orphans

echo "Fetching latest source from git..."
git fetch origin master
git checkout origin/master plantit/
git checkout origin/master scripts/
git checkout origin/master "docker-compose.$config.yml"

echo "Pulling image definitions..."
$compose pull

echo "Building front end..."
cd plantit/front_end || exit
npm install
npm run build
cd ../..

echo "Creating log directory..."
mkdir -p logs

echo "Collecting static files..."
$compose run plantit ./manage.py collectstatic --no-input

echo "Configuring NGINX..."
find config/nginx/conf.d/local.conf -type f -exec sed -i "s/localhost/$host/g" {} \;

echo "Configuring environment variables..."
find .env -type f -exec sed -i "s/DJANGO_API_URL=http:\/\/plantit\/apis\/v1\//DJANGO_API_URL=http:\/\/$host\/apis\/v1\//g" {} \;
find .env -type f -exec sed -i "s/DJANGO_DEBUG=True/DJANGO_DEBUG=False/g" {} \;
find .env -type f -exec sed -i "s/DJANGO_SECURE_SSL_REDIRECT=False/DJANGO_SECURE_SSL_REDIRECT=True/g" {} \;
find .env -type f -exec sed -i "s/DJANGO_SESSION_COOKIE_SECURE=False/DJANGO_SESSION_COOKIE_SECURE=True/g" {} \;
find .env -type f -exec sed -i "s/DJANGO_CSRF_COOKIE_SECURE=False/DJANGO_CSRF_COOKIE_SECURE=True/g" {} \;
find .env -type f -exec sed -i "s/NODE_ENV=development/NODE_ENV=production/g" {} \;

echo "Bringing containers up..."
$compose up -d --quiet-pull

echo "Running migrations..."
$compose exec -T plantit python manage.py makemigrations --noinput
$compose exec -T plantit python manage.py migrate --noinput

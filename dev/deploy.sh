#!/bin/bash

host="$1"
compose="docker-compose -f docker-compose.prod.yml"

./dev/bootstrap.sh -p

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
$compose up -d
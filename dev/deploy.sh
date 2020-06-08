#!/bin/sh

host="$1"
compose="docker-compose -f docker-compose.yml -f docker-compose.prod.yml"

$compose down
git stash
git pull
cd plantit/front_end || exit
npm install
npm run build
cd ..
cd ..
$compose run plantit ./manage.py collectstatic --no-input
$compose run plantit /code/dev/wait-for-postgres.sh postgres ./manage.py makemigrations
$compose run plantit ./manage.py migrate
find config/nginx/conf.d/local.conf -type f -exec sed -i "s/localhost/$host/g" {} \;
find .env -type f -exec sed -i "s/DJANGO_API_URL=http:\/\/plantit\/apis\/v1\//DJANGO_API_URL=http:\/\/$host\/apis\/v1\//g" {} \;
find .env -type f -exec sed -i "s/DJANGO_DEBUG=True/DJANGO_DEBUG=False/g" {} \;
find .env -type f -exec sed -i "s/NODE_ENV=development/NODE_ENV=production/g" {} \;
$compose up -d
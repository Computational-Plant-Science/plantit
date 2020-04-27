#!/bin/sh

host="$1"
compose="docker-compose -f docker-compose.yml -f docker-compose.prod.yml"

cd plantit/front_end || exit
npm install
npm run build
cd ..
cd ..
$compose run plantit ./manage.py collectstatic --no-input
$compose run plantit /code/dev/wait-for-postgres.sh postgres ./manage.py makemigrations
$compose run plantit ./manage.py migrate
find config/nginx/conf.d/local.conf -type f -exec sed -i "s/localhost/$host/g" {} \;
$compose up
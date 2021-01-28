#!/bin/bash

echo "Bootstrapping ${PWD##*/} development environment..."
compose="docker-compose -f docker-compose.dev.yml"
nocache=0
quiet=0

while getopts 'nq' opt; do
    case $opt in
        n) nocache=1 ;;
        q) quiet=1 ;;
        *) echo 'Error in command line parsing' >&2
           exit 1
    esac
done
shift "$(( OPTIND - 1 ))"

echo "Bringing containers down..."
$compose down --remove-orphans

env_file=".env"
echo "Checking for environment variable file '$env_file'..."
if [ ! -f $env_file ]; then
  echo "Environment variable file '$env_file' does not exist. Creating it..."
  chmod +x scripts/configure-environment.sh
  ./scripts/configure-environment.sh
else
  echo "Environment variable file '$env_file' already exists. Continuing..."
fi

echo "Building front end..."
cd plantit/front_end || exit
npm install
npm run build
cd ../..

if [[ "$nocache" -eq 0 ]]; then
  if [[ "$quiet" -eq 0 ]]; then
    echo "Building images..."
    docker build -t computationalplantscience/plantit -f dockerfiles/plantit/Dockerfile .
  else
    echo "Building images quietly..."
    docker build -t computationalplantscience/plantit -q -f dockerfiles/plantit/Dockerfile .
  fi
else
  if [[ "$quiet" -eq 0 ]]; then
    echo "Building images with cache disabled..."
    docker build -t computationalplantscience/plantit --no-cache -f dockerfiles/plantit/Dockerfile .
  else
    echo "Building images quietly with cache disabled..."
    docker build -t computationalplantscience/plantit -q --no-cache -f dockerfiles/plantit/Dockerfile .
  fi
fi

echo "Pulling 3rd-party images and bringing containers up..."
$compose up -d --quiet-pull

echo "Creating run log directory..."
mkdir -p logs

echo "Running migrations..."
$compose exec -T plantit /code/scripts/wait-for-postgres.sh postgres python manage.py makemigrations
$compose exec -T plantit python manage.py migrate

echo "Creating superuser..."
admin_password=$(cut -d '=' -f 2 <<< "$(grep "DJANGO_ADMIN_PASSWORD" "$env_file")" )
admin_username=$(cut -d '=' -f 2 <<< "$(grep "DJANGO_ADMIN_USERNAME" "$env_file")" )
admin_email=$(cut -d '=' -f 2 <<< "$(grep "DJANGO_ADMIN_EMAIL" "$env_file")" )
$compose exec -T plantit /code/scripts/configure-superuser.sh -u "$admin_username" -p "$admin_password" -e "$admin_email"

echo "Configuring sandbox container deployment target..."
$compose exec -T plantit /bin/bash /code/scripts/configure-sandbox.sh
if [ ! -d config/ssh ]; then
  mkdir config/ssh
fi
if [ ! -f config/ssh/known_hosts ]; then
  touch config/ssh/known_hosts
  $compose exec -T plantit bash -c "ssh-keyscan -H sandbox >> /code/config/ssh/known_hosts"
fi
if [ ! -f config/ssh/id_rsa.pub ]; then
  ssh-keygen -b 2048 -t rsa -f config/ssh/id_rsa -N ""
  $compose exec -T plantit bash -c "/code/scripts/ssh-copy-id.expect"
fi

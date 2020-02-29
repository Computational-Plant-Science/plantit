#!/bin/bash

positional=()
while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    -u|--username)
    username="$2"
    shift
    shift
    ;;
    -p|--password)
    password="$2"
    shift
    shift
    ;;
    -e|--email)
    email="$2"
    shift
    shift
    ;;
    -v|--verbose) verbose=1;shift;;
    *)
    positional+=("$1")
    shift
    ;;
esac
done
set -- "${positional[@]}"

if (( verbose == 1 )); then
  echo "Creating Django superuser with..."
  echo "username: ${username}"
  echo "password: ${password}"
  echo "email: ${email}"
fi

script="
from django.contrib.auth.models import User;

username = '$username';
password = '$password';
email = '$email';

if User.objects.filter(username=username).count()==0:
    User.objects.create_superuser(username, email, password);
    print('Superuser created.');
else:
    print('Superuser with that name already exists!');
"
printf "$script" | python manage.py shell
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
esac
done
set -- "${positional[@]}"

script="
from django.contrib.auth.models import User

username = '$username';

if User.objects.filter(username=username).count()==0:
    print('No user with username ' + username);
else:
    user = User.objects.get(username=username)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print('Configured staff/superuser permissions for user ' + username)
"
printf "$script" | python manage.py shell
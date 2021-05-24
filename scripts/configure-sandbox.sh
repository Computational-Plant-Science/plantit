#!/bin/bash

echo "Configuring sandbox..."

script="
from datetime import timedelta
from plantit.resources.models import Resource

if Resource.objects.filter(name='Sandbox').count()==0:
    Resource.objects.create(name='Sandbox', description='A cluster-in-a-container suitable for lightweight, in-process test deployments.', workdir='/opt/plantit-cli/runs', username='root', port=22, hostname='sandbox', pre_commands='export LC_ALL=en_US.utf8 && export LANG=en_US.utf8', public=True)
else:
    print('Sandbox already exists!')
"
printf "$script" | python manage.py shell
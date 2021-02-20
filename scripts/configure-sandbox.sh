#!/bin/bash

echo "Configuring sandbox deployment target..."

script="
from datetime import timedelta
from plantit.targets.models import Target

if Target.objects.filter(name='Sandbox').count()==0:
    Target.objects.create(name='Sandbox', description='A cluster-in-a-container suitable for lightweight, in-process test deployments.', workdir='/opt/plantit-cli/runs', username='root', port=22, hostname='sandbox', pre_commands='export LC_ALL=en_US.utf8 && export LANG=en_US.utf8')
else:
    print('Sandbox already exists!')
"
printf "$script" | python manage.py shell
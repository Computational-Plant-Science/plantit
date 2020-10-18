#!/bin/bash

echo "Configuring sandbox deployment target..."

script="
from plantit.targets.models import Target

if Target.objects.filter(name=name).count()==0:
    Target.objects.create(name='Sandbox', description='A cluster-in-a-container suitable for lightweight, in-process test deployments.', workdir='/test', username='root', port=22, hostname='sandbox', pre_commands='export LC_ALL=C.UTF-8 && export LANG=C.UTF-8')
else:
    print('Sandbox already exists!')
"
printf "$script" | python manage.py shell
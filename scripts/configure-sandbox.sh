#!/bin/bash

echo "Configuring sandbox..."

script="
from datetime import timedelta
from plantit.agents.models import Agent

if Agent.objects.filter(name='Sandbox').count()==0:
    Agent.objects.create(name='Sandbox', description='A cluster-in-a-container suitable for lightweight, in-process test deployments.', workdir='/opt/plantit-cli/submissions', username='root', port=22, hostname='sandbox', pre_commands='export LC_ALL=en_US.utf8 && export LANG=en_US.utf8', public=True)
else:
    print('Sandbox already exists!')
"
printf "$script" | python manage.py shell
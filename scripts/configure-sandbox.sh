#!/bin/bash

echo "Configuring sandbox..."

script="
import uuid
from datetime import timedelta
from plantit_web.agents.models import Agent

if Agent.objects.filter(name='Sandbox').count()==0:
    Agent.objects.create(name='Sandbox', guid=str(uuid.uuid4()), description='A cluster-in-a-container suitable for lightweight, in-process test deployments.', workdir='/opt/plantit-cli/runs', username='root', port=22, hostname='sandbox', pre_commands='export LC_ALL=en_US.utf8 && export LANG=en_US.utf8', public=True)
else:
    print('Sandbox already exists!')
"
printf "$script" | python manage.py shell
#!/bin/bash

echo "Configuring sandbox deployment target..."

script="
from datetime import timedelta
from plantit.clusters.models import Cluster

if Cluster.objects.filter(name='Sandbox').count()==0:
    Cluster.objects.create(name='Sandbox', description='A cluster-in-a-container suitable for lightweight, in-process test deployments.', workdir='/opt/plantit-cli/runs', username='root', port=22, hostname='sandbox', pre_commands='export LC_ALL=en_US.utf8 && export LANG=en_US.utf8', public=True)
else:
    print('Sandbox already exists!')
"
printf "$script" | python manage.py sell
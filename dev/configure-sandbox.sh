#!/bin/bash

echo "Configuring sandbox deployment target..."

script="
from plantit.runs.models import Cluster

name = 'Sandbox'
description = 'An Ubuntu 18.04 deployment target suitable for workflow test runs. Executes workflows in-process and does not support parallelization.'
workdir = 'test'
username = 'root'
password = 'root'
port = 22
hostname = sandbox

if Cluster.objects.filter(name=name).count()==0:
    Cluster.objects.create(name=name, description=description, workdir=workdir, username=username, password=password, port=port, hostname=hostname)
    print('Configured sandbox.')
else:
    print('Sandbox already exists!')
"
printf "$script" | python manage.py shell
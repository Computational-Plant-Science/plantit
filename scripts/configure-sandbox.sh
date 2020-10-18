#!/bin/bash

echo "Configuring sandbox deployment target..."

script="
from plantit.targets.models import Target

if Target.objects.filter(name=name).count()==0:
    Target.objects.create(name='Sandbox', description='A cluster-in-a-container suitable for lightweight, in-process test deployments.', workdir='/test', username='root', port=22, hostname='sandbox', pre_commands='export LC_ALL=C.UTF-8 && export LANG=C.UTF-8')
    Target.objects.create(name='Sapelo2', description='GACRC\\'s Sapelo2 cluster.', workdir='/home/wpb35237/plantit/', username='wpb36237', port=22, hostname='sapelo2-droid.gacrc.uga.edu', pre_commands='export LC_ALL=en_US.utf8 && export LANG=en_US.utf8 && ml load Anaconda3/5.0.1 && ml load git/2.23.0-GCCcore-8.3.0-nodocs && source activate plantit')
    Target.objects.create(name='Stampede2', description='TACC\\'s Stampede2 cluster.', workdir='/home1/03203/dirt/plantit', username='dirt', port=22, hostname='stampede2.tacc.utexas.edu', pre_commands='export LC_ALL=en_US.utf8 && export LANG=en_US.utf8 && ml load gcc/9.1.0 && ml load python3/3.8.2 && ml load tacc-singularity/3.4.2 && source ../bin/activate')
else:
    print('Sandbox already exists!')
"
printf "$script" | python manage.py shell
#!/bin/bash

#
# Resets everything back to a "Fresh" install by:
#   - rebuilding all docker images
#   - deleting all docker volumes
#   - removing all django mmigrations
# then rebuilds the images and runs initial django migration and
#  creates an admin user:
#      username: admin
#      pass: admin
#

#Delete all docker containers and volumes
docker-compose rm -v -f -s

# Remove all previous django migrations
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete

# Remove all files saved to the server
rm -rf 'files/scripts.job_manager/*'

#recreate images
docker-compose build

#start the databse container, it needs some time to initilize before
# starting the webserver
docker-compose up -d db

echo "Waiting 30s for db to warm up..."
sleep 30s

#Reinstall databases
docker-compose run web python manage.py makemigrations
docker-compose run web python manage.py migrate

#Add some defaults to the server
docker-compose run web python manage.py shell << PYTHONCODE
#BEGIN PYTHON CODE

#Default admin user
from django.contrib.auth.models import User;
User.objects.create_superuser('admin', 'admin@example.com', 'admin')

#Default objects to work with
from job_manager.models import Cluster, Executor, Job
from job_manager.test.test_models import create_cluster, create_script, create_executor
cluster = create_cluster("./{sub_script} {job_pk} {auth_token}")
sub_script = create_script('/code/dev/server_scripts/confirm_complete.sh')
status_script = create_script('/code/dev/server_scripts/update_status.sh')
exe = create_executor(sub_script)
exe.files.add(status_script)

#END PYTHON CODE
PYTHONCODE


#Stop db container
docker-compose stop

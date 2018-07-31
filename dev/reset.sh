#!/bin/bash

#
# Resets everything back to a "Fresh" install by:
#   - rebuilding all docker images
#   - deleting all docker volumes
#   - removing all django migrations
# then rebuilds the images and runs initial django migration and
#  creates an admin user:
#      username: admin
#      pass: admin
#  as well as a default cluster and executor that ssh into the ssh docker cluster
#

#Delete all docker containers and volumes
docker-compose rm -v -f -s

# Remove all previous django migrations
find . -path django/**/migrations/*.py -not -name "__init__.py" -delete
find . -path django/**/migrations/*.py -delete

# Remove all files saved to the server
rm -rf django/files/*

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
user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')

#Default objects to work with
from job_manager.models import Cluster
from job_manager.test.test_models import create_cluster
cluster = create_cluster("./{sub_script} {job_pk} {task_pk} {auth_token}")

#END PYTHON CODE
PYTHONCODE

#Stop db container
docker-compose stop

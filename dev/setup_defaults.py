'''
This file is run by reset.sh to setup some website defaults
'''

#Default admin user
from django.contrib.auth.models import User;
user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')

#Default objects to work with
from job_manager.remote import Cluster
from job_manager.test.test_models import create_cluster
cluster = create_cluster("clusterside submit --url http://web/jobs/api/")

from file_manager.permissions import Permissions
Permissions.allow(user,"local",'./files/')
Permissions.allow(user,"irods",'/home/rods/')

#Some fake objects to fill the websitegv
from job_manager.test.test_models import create_collection, create_job, add_task
collection = create_collection(user = user)
job = create_job(user = user, collection= collection)
add_task(job,"Fake Task 1")
add_task(job,"Fake Task 2")
add_task(job,"Fake Task 3")

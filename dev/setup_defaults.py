'''
This file is run by reset.sh to setup some website defaults
'''

#Default admin user
from django.contrib.auth.models import User;
admin_user = User.objects.create_superuser(username = 'admin',
                                     email = 'admin@example.com',
                                     password = 'admin')
regular_user = User.objects.create_user(username = 'user1',
                         email = 'user1@example.com',
                         password = 'user1')


#Default objects to work with
from job_manager.remote import Cluster
from job_manager.test.test_models import create_cluster
cluster = create_cluster("clusterside submit")

from file_manager.permissions import Permissions
Permissions.allow(admin_user,"local",'./files/')
Permissions.allow(regular_user,"local",'./files/')
Permissions.allow(admin_user,"irods",'/tempZone/home/rods/')
Permissions.allow(regular_user,"irods",'/tempZone/home/rods/')

#Some fake objects to fill the website
from job_manager.test.test_models import create_collection, create_job, add_task
collection = create_collection(user = admin_user)
job = create_job(user = admin_user, collection= collection)
add_task(job,"Fake Task 1")
add_task(job,"Fake Task 2")
add_task(job,"Fake Task 3")

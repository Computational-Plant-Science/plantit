import os

# Create Django admin user
from django.contrib.auth.models import User;
admin_user = User.objects.create_superuser(username = 'admin',
                                     email = 'admin@example.com',
                                     password = 'admin')
regular_user = User.objects.create_user(username = 'user1',
                         email = 'user1@example.com',
                         password = 'user1')

# Create mock cluster
from plantit.job_manager.remote import Cluster
from plantit.job_manager.test.test_models import create_cluster
cluster = create_cluster("clusterside submit")

# Configure mock IRODS
variables = ["IRODS_USERNAME = 'rods'",
             "IRODS_PASSWORD = 'rods'",
             "IRODS_HOSTNAME = 'irods'",
             "IRODS_ZONE = 'tempZone'"]
if not os.path.exists('plantit/secret.py'):
    with open('plantit/secret.py','w') as infile:
        for line in variables:
            infile.write(line + "\n")

'''
This file is run by reset.sh to setup some website defaults
'''

#Default admin user
from django.contrib.auth.models import User;
user = User.objects.create_superuser('admin', 'admin@example.com', 'admin')

#Default objects to work with
from job_manager.remote import Cluster
from job_manager.test.test_models import create_cluster
cluster = create_cluster("./{sub_script} {job_pk} {task_pk} {auth_token}")

from file_manager.permissions import Permissions
from file_manager.filesystems.local import Local
l = Local(name = "Local")
l.save()
Permissions.allow(user,l,'./files/')

from file_manager.filesystems.irods import IRods
irods = IRods(hostname="test_irods",username="rods",password="rods",zone="tempZone")
irods.save()
Permissions.allow(user,irods,'/home/rods/')

#dirt2d workflow defaults
from workflows.dirt2d.models import Defaults
from django.core.files import File
from job_manager.remote import File as JobFile
sub_script = JobFile(content=File(open("workflows/dirt2d/dev/run.sh")),
                     file_name="run.sh")
sub_script.save()
server_update = JobFile(content=File(open("files/server_update")),
                        file_name="server_update")
server_update.save()
traits_file = JobFile(content=File(open("files/traits.csv")),
                      file_name="traits.csv")
traits_file.save()
d = Defaults(submission_script = sub_script)
d.save()
d.files.add(server_update)
d.files.add(traits_file)

#Some fake objects to fill the website
from job_manager.test.test_models import create_collection, create_job, add_task
collection = create_collection(user = user)
job = create_job(user = user, collection= collection)
add_task(job,"Fake Task 1")
add_task(job,"Fake Task 2")
add_task(job,"Fake Task 3")

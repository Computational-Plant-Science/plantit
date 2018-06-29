import datetime
from os import path
import random
import string

from django.test import TestCase
from django.utils import timezone
from django.core import files
from django.contrib.auth.models import User;

from job_manager.models import Job, Status, Cluster, Executor, File

# Create your tests here.
def create_script(file=None):
    if(not file):
        file = '/code/dev/server_scripts/test_create_file.sh'
    script = File(content=files.File(open(file, 'r')))
    script.file_name = path.basename(file)
    script.save()
    return script

def create_cluster(submit_commands=None,uname=None):
    if(not submit_commands):
        submit_commands = "cat {sub_script}"
    if(not uname):
        uname="root"
    c = Cluster(name="Test",
                port=22,
                description="Connects to docker ssh container",
                username=uname,
                password="root",
                hostname="ssh",
                workdir="/root/",
                submit_commands=submit_commands,
                cancel_commands="")
    c.save()
    return c

def create_executor(script = None):
    if(not script):
        script = create_script()

    e = Executor(name="test executor",
                 description="Does not do anything",
                 submission_script=script)
    e.save()
    return e

def create_user():
    uname = 'test_' + ''.join(random.choice(string.ascii_letters) for x in range(5))
    uname = 'email_' + ''.join(random.choice(string.ascii_letters) for x in range(5))
    return User.objects.create_user('uname','no-email','test')

def create_job(cluster = None, executor = None):
    if(not cluster):
        cluster = create_cluster()

    if(not executor):
        executor = Executor(name="test executor",
                    description="Does not do anything")
        executor.save()

    u = create_user()

    j = Job(date_created=timezone.now(),
            cluster=cluster,
            executor=executor,
            user=u)
    j.save()
    j.status_set.create(state=Status.CREATED,date=timezone.now(),description="Created")
    return j

class JobModelTests(TestCase):
    def test_current_status(self):
        """
            Check that the most recent (defined by status.date) is
            returned as the current status.
        """
        j = create_job()
        time = timezone.now() + datetime.timedelta(days=1)
        j.status_set.create(state=Status.RUNNING,date=time,description="Updated")
        self.assertIs(j.current_status().date == time, True)

import datetime
from os import path
import random
import string
import tempfile

from django.test import TestCase
from django.utils import timezone
import django.core.files as files
from django.contrib.auth.models import User;
from django.core.exceptions import SuspiciousFileOperation

from job_manager.job import Status, Job, Task, DummyTask
from job_manager.remote import Cluster, SubmissionTask, File, UploadFileTask
from job_manager.job import __cancel_job__, __run_next__

from collection.models import Collection

import paramiko

# Create your tests here.
def create_script(file=None):
    """
        Create a script file.

        Args:
            content (str): file contents
            name (str): file name
    """
    if not file:
        file = tempfile.NamedTemporaryFile(mode="w",dir='./files/tmp/',delete=False)
        file.write("echo 'Test' > test.file")
        file.close()

    script = File(content=files.File(open(file.name,'r')))
    script.file_name = path.basename(file.name)

    script.save()

    return script

def create_collection(user = None):
    if(not user):
        user = create_user()

    c = Collection(name="Test Collection",
                   description="test",
                   user=user,
                   storage_type="Local",
                   base_file_path="files/")
    c.save()

    return c

def create_cluster(submit_commands=None,uname=None):
    if(not submit_commands):
        submit_commands = "./{sub_script}"
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
                cancel_commands="ls /")
    c.save()
    return c

def add_task(job,name = None):
    if not name:
        name = "Test Task"
    e = DummyTask(name=name,
                 description="Does not do anything",
                 job=job)
    e.save()
    return e

def create_user():
    uname = 'test_' + ''.join(random.choice(string.ascii_letters) for x in range(5))
    email = 'email_' + ''.join(random.choice(string.ascii_letters) for x in range(5))
    return User.objects.create_user(uname,email,'test')

def create_job(user = None, collection = None):
    if(not user):
        user = create_user()
    if(not collection):
        collection = create_collection(user)

    j = Job(date_created=timezone.now(),
            user=user,
            collection=create_collection()
            )

    j.save()
    j.status_set.create(state=Status.CREATED,date=timezone.now(),description="Created")
    return j

class JobTests(TestCase):
    def test_current_status(self):
        """
            Check that the most recent (defined by status.date) is
            returned as the current status.
        """
        j = create_job()
        time = timezone.now() + datetime.timedelta(days=1)
        j.status_set.create(state=Status.OK,date=time,description="Updated")
        self.assertEqual(j.current_status().date,time)

    def test_run_job(self):
        c = create_cluster()
        j = create_job()
        t = add_task(j)

        try:
            __run_next__(j.pk)
        except:
            self.assertIs(False,True)

        t.refresh_from_db()
        self.assertTrue(t.ran)


    def test_cancel_job(self):
        j = create_job()
        __cancel_job__(j.pk)
        self.assertEqual(j.current_status().state,Status.FAILED)

    def test_multi_task_job(self):
        j = create_job()

        t2 = DummyTask(name="Task 2",
                     description="should run Second",
                     job = j,
                     order_pos = 2)
        t2.save()
        t1 = DummyTask(name="Task 1",
                     description="should run first",
                     job = j,
                     order_pos = 1)
        t1.save()

        __run_next__(j.pk)
        t1.refresh_from_db()
        t2.refresh_from_db()
        self.assertIs(t1.ran,True)
        self.assertIs(t2.ran,False)
        t1.finish()
        __run_next__(j.pk) # HACK to get around celery not working durning tests
        t1.refresh_from_db()
        t2.refresh_from_db()
        self.assertIs(t1.ran,True)
        self.assertIs(t2.ran,True)

    def test_cancel_submitted_job(self):
        pass

    def test_cancel_failed(self):
        pass

from file_manager.permissions import Permissions
from file_manager.filesystems.local import Local

class RemoteTests(TestCase):
    def setUp(self):
        self.storage_type = Local(name = "Local")
        self.storage_type.save()
        self.user = create_user()
        Permissions.allow(self.user,self.storage_type,'./files/')
        Permissions.allow(self.user,self.storage_type,'./files/tmp/')

    def open_sftp(cluster,job):
        """
            Opens an sftp connection to the job's cluster and cds into
            the jobs work directory
        """
        cluster = cluster
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(cluster.hostname,
                       cluster.port,
                       cluster.username,
                       cluster.password)
        sftp = client.open_sftp()
        sftp.chdir(path=cluster.workdir + "/" + job.work_dir)
        return sftp

    def create_submission_task(cluster = None, job = None, order_pos = 1):
        if not cluster:
            cluster = create_cluster()
        if not job:
            job = create_job()

        t = SubmissionTask(name="TestTask",
                    description="Test Submission Task",
                    job = job,
                    order_pos = order_pos,
                    cluster = cluster)
        t.save()
        return t

    def test_ssh_login_failed(self):
        """
            Test that job state is set to FAILED if server login fails
        """
        j = create_job()
        t = RemoteTests.create_submission_task(job = j)
        t.run()
        self.assertEqual(j.current_status().state,Status.FAILED)

    def test_submit_failed(self):
        """
            Test job state is set to FAILED if the server scripts return
            and error code
        """
        c = create_cluster(submit_commands="cat a_file_that_does_not_exist.sh")
        j = create_job()
        t = RemoteTests.create_submission_task(cluster = c, job = j)
        t.run()
        self.assertEqual(j.current_status().state,Status.FAILED)

    def test_submission_format_cluster_cmds(self):
        j = create_job()
        c = create_cluster()
        submission_script = create_script()
        file1 = create_script()
        task = SubmissionTask(name="Task 2",
                     description="should run Second",
                     job = j,
                     cluster = c,
                     order_pos = 1,
                     submission_script=submission_script,
                     parameters="""{
                                    "p":"-p",
                                    "task":"--task test"
                                }""")

        res = task.format_cluster_cmds("{job_pk}")
        self.assertEqual(str(j.pk),res)

        res = task.format_cluster_cmds("{auth_token}")
        self.assertEqual(str(j.auth_token),res)

        res = task.format_cluster_cmds("{task_pk}")
        self.assertEqual(str(task.pk),res)

        res = task.format_cluster_cmds("{p} {task}")
        self.assertEqual("-p --task test",res)

        j.submission_id = 10
        res = task.format_cluster_cmds("{sub_id}")
        self.assertEqual(str(j.submission_id),res)

    def test_submission_task(self):
        j = create_job()
        c = create_cluster()
        submission_script = create_script()
        file1 = create_script()
        task = SubmissionTask(name="Task 2",
                     description="should run Second",
                     job = j,
                     cluster = c,
                     order_pos = 1,
                     submission_script=submission_script)
        task.save()
        task.files.add(file1)
        task.run()

        #The submission task catches most errors raised during the sftp/ssh calls,
        # and sets the job status to Status.FAILED
        job_status = j.current_status()
        self.assertEqual(job_status.state,
                         Status.CREATED,
                         msg="WORKDIR: %s, MESSAGE: %s"%
                                (j.work_dir,job_status.description))

        sftp = RemoteTests.open_sftp(c,j)
        uploaded_files = sftp.listdir()
        self.assertTrue(file1.file_name in uploaded_files)
        self.assertTrue(submission_script.file_name in uploaded_files)
        self.assertTrue('test.file' in uploaded_files) #Created by the submission script
        self.assertFalse(task.complete) #Task must be marked complete by the cluster

    def test_upload_file_task(self):
        j = create_job(user=self.user)
        c = create_cluster()
        file1 = tempfile.NamedTemporaryFile(mode="w",dir='./files/tmp/',delete=False)
        file2 = tempfile.NamedTemporaryFile(mode="w",dir='./files/tmp/',delete=False)
        file1.close()
        file2.close()
        files = "%s,%s"%(file1.name,file2.name)
        task = UploadFileTask(name="Task",
             description="Uploads some files",
             job = j,
             order_pos = 1,
             cluster = c,
             pwd = './files/tmp/',
             storage_type=self.storage_type.name,
             files = files)
        task.save()
        task.run()

        #The task catches most errors raised during the sftp calls,
        # and sets the job status to Status.FAILED
        job_status = j.current_status()
        self.assertEqual(job_status.state,
                         Status.CREATED,
                         msg=job_status.description)

        sftp = RemoteTests.open_sftp(c,j)
        uploaded_files = sftp.listdir("files/")
        for file in files.split(","):
            self.assertTrue(path.basename(file) in uploaded_files)

        #This job should have marked itself complete
        self.assertTrue(task.complete)

    def test_upload_file_task_file_not_exist(self):
        j = create_job(user=self.user)
        file1 = tempfile.NamedTemporaryFile(mode="w",dir='./files/tmp/',delete=False)
        file1.close()
        files = "%s,non_existant_file"%(file1.name)
        task = UploadFileTask(name="Task",
                     cluster = create_cluster(),
                     description="Uploads some files",
                     job = j,
                     order_pos = 1,
                     pwd = './files/tmp/',
                     storage_type=self.storage_type.name,
                     files = files)
        task.save()
        task.run()

        #The task catches the IOError associated with a nonexistant file
        #  and sets the job status to failed
        job_status = j.current_status()
        self.assertEqual(job_status.state,
                         Status.FAILED,
                         msg=job_status.description)

        #This job should have not marked itself complete since it failed
        self.assertFalse(task.complete)

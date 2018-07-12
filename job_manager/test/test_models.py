import datetime
from os import path
import random
import string

from django.test import TestCase
from django.utils import timezone
from django.core import files
from django.contrib.auth.models import User;

from job_manager.models import Status, Cluster, Job, Task
from job_manager.models import __cancel_job__, __run_next__
from job_manager.contrib import SubmissionTask, File, DummyTask, UploadFileTask

import paramiko

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

def add_task(job,script = None):
    if(not script):
        script = create_script()

    e = SubmissionTask(name="Test Task",
                 description="Does not do anything",
                 submission_script=script,
                 job=job)
    e.save()
    return e

def create_user():
    uname = 'test_' + ''.join(random.choice(string.ascii_letters) for x in range(5))
    email = 'email_' + ''.join(random.choice(string.ascii_letters) for x in range(5))
    return User.objects.create_user(uname,email,'test')

def create_job(cluster = None, user = None):
    if(not cluster):
        cluster = create_cluster()

    if(not user):
        user = create_user()

    j = Job(date_created=timezone.now(),
            cluster=cluster,
            user=user)
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
        self.assertEqual(j.current_status().date,time)

    def test_submit_job(self):
        """
            Test submitting job to cluster
        """
        c = create_cluster()
        j = create_job(cluster=c)
        add_task(j)

        try:
            __run_next__(j.pk)
        except:
            self.assertIs(False,True)

    def test_login_failed(self):
        """
            Test that job state is set to FAILED if server login fails
        """
        c = create_cluster(uname="hacker")
        j = create_job(cluster=c)
        add_task(j)
        __run_next__(j.pk)
        self.assertEqual(j.current_status().state,Status.FAILED)

    def test_submit_failed(self):
        """
            Test job state is set to FAILED if the server scripts return
            and error code
        """
        c = create_cluster(submit_commands="cat a_file_that_does_not_exist.sh")
        j = create_job(cluster=c)
        add_task(j)
        __run_next__(j.pk)
        self.assertEqual(j.current_status().state,Status.FAILED)

    def test_cancel_unsubmitted_job(self):
        """
            Test that a canceled job that was not sumbitted to the cluster
            is has a state of FAILED
        """
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

class TaskTests(TestCase):
    def open_sftp(self,job):
        """
            Opens an sftp connection to the job's cluster and cds into
            the jobs work directory
        """
        cluster = job.cluster
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(cluster.hostname,
                       cluster.port,
                       cluster.username,
                       cluster.password)
        sftp = client.open_sftp()
        sftp.chdir(path=cluster.workdir + "/" + job.work_dir)
        return sftp

    def test_submission_format_cluster_cmds(self):
        j = create_job()
        submission_script = create_script()
        file1 = create_script(file='dev/server_scripts/server_update')
        task = SubmissionTask(name="Task 2",
                     description="should run Second",
                     job = j,
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
        submission_script = create_script()
        file1 = create_script(file='dev/server_scripts/server_update')
        task = SubmissionTask(name="Task 2",
                     description="should run Second",
                     job = j,
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
                         msg=job_status.description)

        sftp = self.open_sftp(j)
        uploaded_files = sftp.listdir()
        self.assertTrue(file1.file_name in uploaded_files)
        self.assertTrue(submission_script.file_name in uploaded_files)
        self.assertTrue('test.file' in uploaded_files) #Created by the submission script

    def test_upload_file_task(self):
        j = create_job()
        files = "test_create_file.sh,server_update"
        task = UploadFileTask(name="Task",
                     description="Uploads some files",
                     job = j,
                     order_pos = 1,
                     pwd = './dev/server_scripts/',
                     backend = "FileSystemStorage",
                     files = files)
        task.save()
        task.run()

        #The task catches most errors raised during the sftp calls,
        # and sets the job status to Status.FAILED
        job_status = j.current_status()
        self.assertEqual(job_status.state,
                         Status.CREATED,
                         msg=job_status.description)

        sftp = self.open_sftp(j)
        uploaded_files = sftp.listdir("files/")
        for file in files.split(","):
            self.assertTrue(file in uploaded_files)

        #This job should have marked itself complete
        self.assertTrue(task.complete)

    def test_upload_file_task_file_not_exist(self):
        j = create_job()
        files = "test_create_file.sh,non_existant_file"
        task = UploadFileTask(name="Task",
                     description="Uploads some files",
                     job = j,
                     order_pos = 1,
                     pwd = './dev/server_scripts/',
                     backend = "FileSystemStorage",
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

from __future__ import absolute_import, unicode_literals
from celery import shared_task

import binascii
import os

import paramiko
from paramiko.ssh_exception import AuthenticationException

from encrypted_model_fields.fields import EncryptedCharField
from django.db import models
from django.utils import timezone
from django.conf import settings

from model_utils.managers import InheritanceManager

@shared_task
def __run_next__(pk):
    """
        Runs next uncompleted job task
        This function is run in a Celery worker to make the job run
            asyncroniully with the cluster
    """
    job = Job.objects.get(pk=pk)

    if(job.current_status().state == Status.FAILED):
        return

    queued_tasks = job.task_set.filter(complete = False).order_by('order_pos').select_subclasses()
    if(len(queued_tasks) > 0):
        task = queued_tasks[0]
        task.run()
    else:
        job.status_set.create(state=Status.COMPLETED,
                    date=timezone.now(),
                    description=str("All Tasks Finished"))

@shared_task
def __cancel_job__(pk):
    """
        This function will open an ssh connection and
        cancel the passed job

        This function is run in a Celery worker to make the job run
            asyncroniully with the cluster
    """
    job = Job.objects.get(pk=pk)

    status = job.current_status().state

    if(status < Status.RUNNING):
        return #Job already done.
    elif(status == Status.CREATED):
        # Job never actucally submitted to a cluster
        job.status_set.create(state=Status.FAILED,
                               date=timezone.now(),
                               description="Job Canceled")
    else:
        cmds = format_cluster_cmds(self.cancel_commands)
        #Connect to server
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(cluster.hostname,
                       cluster.port,
                       cluster.username,
                       cluster.password)

        stdin, stdout, stderr = client.exec_command(cmds)
        errors = stderr.readlines()
        if(errors != []):
            self.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description=str(errors))
        else:
            self.status_set.create(state=Status.FAILED,
                                   date=timezone.now(),
                                   description="Job Canceled")
        client.close()


class Cluster(models.Model):
    """
        Contains information needed to login in to the cluster and submit
        or cancel jobs. Clusters must support ssh via password authentication.
    """
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    workdir = models.CharField(max_length=250)
    username = models.CharField(max_length=100)
    password = EncryptedCharField(max_length=100)
    port = models.PositiveIntegerField()
    hostname = models.CharField(max_length=250)
    submit_commands = models.TextField()
    cancel_commands = models.TextField()

    def __str__(self):
        return self.name

class Job(models.Model):
    """
        The Job class contains all information related to the computations
        to be performed on the cluster.

        A job consists of one or more job_manager.models.Task. Tasks are run
        asending-serially according to their Task.order_pos number. The tasks
        are run server side, but asynchronously via a celery worker.

        Jobs should be cluster agnostic.

        fields:
        date_created: Date the job was created, defaults to timezone.now()
        cluster: ForeinKey to Cluster, The cluster used to run the job
        auth_token: A authentication token used by
            job_manager.authentication.JobTokenAuthentication to authenicate
            REST API connections
        user: user that created the job
        submission_id: UID of the cluster job that is performing the job actions.
    """
    def generate_token():
        """
            Generate a valid auth_token
        """
        return binascii.hexlify(os.urandom(20)).decode()

    date_created = models.DateTimeField(default=timezone.now)
    cluster = models.ForeignKey(Cluster,on_delete=models.CASCADE)
    auth_token = models.CharField(max_length=40,default=generate_token)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    submission_id = models.CharField(max_length=100,null=True,blank=True)

    #def __str__(self):
        #return "Status: %s, Cluster: %s" (self.current_status(),self.cluster)

    def current_status(self):
        """
            Returns the most recent status of the job as a Status object.
        """
        return self.status_set.latest('date')

    @staticmethod
    def run_next(pk):
        """
            Submit job async
        """
        return __run_next__.delay(pk)

    @staticmethod
    def cancel(pk):
        """
            Cancel job async
        """
        return __cancel_job__.delay(pk)

class Task(models.Model):
    """
        A task that can be run by a Job

        Once a job is started by calling Job.run_next(job.pk), the first task
        is automatically run, every task after the first will wait until
        the previous tasks finish() method is called.
    """
    objects = InheritanceManager()
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    order_pos = models.PositiveIntegerField(default=1)
    complete = models.BooleanField(default=False)

    def run(self):
        """
            Command called to run the task
        """
        raise NotImplementedError

    def __str__(self):
        return self.name

    def finish(self):
        """
            Mark this task complete and initiate the next task in the
                task queue for the job
        """
        self.complete = True
        self.save()
        return Job.run_next(self.job.pk)

class Status(models.Model):
    """
        Tracks job status.
    """
    #Possible states
    COMPLETED  = 1 # Computation completed and data returned
    FAILED     = 2 # Job failed
    RUNNING    = 3 # Job running on cluster
    IN_QUEUE   = 4 # Job confired it is queued on the cluster
    SUBMITTED  = 5 # Job was submtted to the cluster
    CREATED    = 6 # Job was crated but not yet submitted to a cluster

    State = (
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (RUNNING, 'Running'),
        (IN_QUEUE, 'In Queue'),
        (SUBMITTED, 'Submitted'),
        (CREATED, 'Created')
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    state = models.PositiveIntegerField(choices=State,default=CREATED)
    date = models.DateTimeField(default=timezone.now,blank=True)
    description = models.CharField(max_length=280)

    def __str__(self):
        return self.State[self.state - 1][1]

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
        asynchronous with the webserver
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
        This function will open an ssh connection to the cluster and
        cancel the passed job

        This function is run in a Celery worker to make the job run
        asynchronous with the webserver
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

        Attributes:
            name (str): The name of the cluster (max_length=20)
            description (str):
                A short description providing notes and information related to
                this cluster
            workdir (str): Directory on the cluster in which tasks are run
            username (str): username used to log into the cluster
            password (str): password used to log into the cluster
            port (int): Cluster ssh server ssh port (default=22)
            hostname (str): Cluster hostname
            submit_commands (str): The command(s) to be run via an ssh terminal
                submit_commands has access to variables_ set by either some tasks
                or jobs. When available, they are automatically instered in place
                of the following text (default='./{sub_script} {job_pk} {task_pk} {auth_token}')
            cancel_commands (str): The coammnds(s) to be executed to cancel
                a job on the cluster.

        .. _variables:
        Variables:
            +-------------+-----------------------------------------------+
            + Varabile    + Description                                   |
            +=============+===============================================+
            |{sub_script} | the path (on the clustet) to the submission   |
            |             | script provided by the current task           |
            |             | (only valid for some tasks)                   |
            +-------------+-----------------------------------------------+
            |{job_pk}     | the current job id                            |
            +-------------+-----------------------------------------------+
            |{task_pk}    | the current task id                           |
            +-------------+-----------------------------------------------+
            |{auth_token} | the REST API authentication token             |
            +-------------+-----------------------------------------------+
    """
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    workdir = models.CharField(max_length=250)
    username = models.CharField(max_length=100)
    password = EncryptedCharField(max_length=100)
    port = models.PositiveIntegerField(default=22)
    hostname = models.CharField(max_length=250)
    submit_commands = models.TextField(default="./{sub_script} {job_pk} {task_pk} {auth_token}")
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

        Attributes:
            date_created (DateTime): Date the job was
                created, defaults to timezone.now() (default=now)
            cluster (ForeignKey): ForeinKey to Cluster,
                The cluster used to run the job
            auth_token (str): A authentication token used by
                job_manager.authentication.JobTokenAuthentication to authenicate
                REST API connections (autogenerated by default)
            user (str): user that created the job
            submission_id (str): UID of the cluster job that is performing the job actions.
            work_dir (str): the directory on the cluster to perform the task in.
                 This path is relative to the clusters work_dir path.
                 (autogenerated by default)
    """
    def generate_work_dir():
        """
            Generate a string to use as the the working directory for a job
        """
        return timezone.now().strftime('%s') + "/"

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
    work_dir = models.CharField(max_length=100,
                                null=True,
                                blank=True,
                                default=generate_work_dir)

    # def __str__(self):
    #      return "Status: %s, Cluster: %s" (self.current_status().description,self.cluster)

    def current_status(self):
        """
            Returns the most recent status of the job as a :class:`Status` object.
        """
        return self.status_set.latest('date')

    @staticmethod
    def run_next(pk):
        """
            Submit job async

            Args:
                pk (int): the job pk number

            Returns:
                the :class:`Celery` worker object
        """
        return __run_next__.delay(pk)

    @staticmethod
    def cancel(pk):
        """
            Submit job async

            Args:
                pk (int): the job pk number

            Returns:
                the :class:`Celery` worker object
        """
        return __cancel_job__.delay(pk)

class Task(models.Model):
    """
        A task that can be run by a Job

        Once a job is started by calling Job.run_next(job.pk), the first task
        is automatically run, every task after the first will wait until
        the previous tasks finish() method is called.

        Attributes:
            name (str): Name of the task
            description (str): Information and note related to this task
            job (ForeignKey): The job containing this task
            order_pos (int): The position within the job task queue.
                Tasks are executed sequentially according to their
                order_pos. Behavior for mutiple tasks with the same order_pos
                is undefined.
            complete (bool): The is completed
            last_updated (DateTime): last time the task was updated, typically,
                changed when the task is created or marked as complete.
    """
    objects = InheritanceManager()
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    order_pos = models.PositiveIntegerField(default=1)
    complete = models.BooleanField(default=False)
    last_updated = models.DateTimeField(default=None,blank=True,null=True)

    def run(self):
        """
            Command called to run the task
        """
        raise NotImplementedError

    def __str__(self):
        return "%s (%d)"%(self.name,self.pk)

    def finish(self):
        """
            Mark this task complete and initiate the next task in the
                task queue for the job
        """
        self.complete = True
        print("Here for task %s"%(self.name))
        self.last_updated = timezone.now()
        self.save()
        return Job.run_next(self.job.pk)

class Status(models.Model):
    """
        Job status.

        Arguments:
            job (ForeinKey):
            state (int):
            date (DateTime):
            description (str):
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

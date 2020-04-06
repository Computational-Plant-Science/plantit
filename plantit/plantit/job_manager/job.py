"""
    The main job manager framework.
"""
from __future__ import absolute_import, unicode_literals
from celery import shared_task

import binascii
import os

from django.db import models
from django.utils import timezone
from django.conf import settings
from model_utils.managers import InheritanceManager

from encrypted_model_fields.fields import EncryptedCharField

import plantit.jobs.solids
from ..collection.models import Collection


@shared_task
def __run_task__(task_pk):
    """
        Calls the run command asynchronously on the given task
        regardless of its state.

        Args:
            task_pk: pk of the task to run
    """
    task = Task.objects.get_subclass(pk=task_pk)
    plantit.jobs.solids.run_workflow()


@shared_task
def __run_next__(pk):
    """
        Runs next uncompleted job task

        This function is run in a Celery worker to make the job run
        asynchronous with the webserver
    """
    job = Job.objects.get(pk=pk)

    if job.current_status().state == Status.FAILED:
        return

    queued_tasks = job.task_set.filter(complete=False).order_by('order_pos').select_subclasses()
    if len(queued_tasks) > 0:
        task = queued_tasks[0]
        plantit.jobs.solids.run_workflow()
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

    if status < Status.OK:
        return  # Job already done.
    elif status == Status.CREATED:
        # Job never actucally submitted to a cluster
        job.status_set.create(state=Status.FAILED,
                              date=timezone.now(),
                              description="Job Canceled")
    else:
        cmds = format_cluster_cmds(self.cancel_commands)
        # Connect to server
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(cluster.hostname,
                       cluster.port,
                       cluster.username,
                       cluster.password)

        stdin, stdout, stderr = client.exec_command(cmds)
        errors = stderr.readlines()
        if errors:
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
        or cancel jobs. Clusters must support ssh via password authentication
        or support ssh key authentication.

        **Key Authentication**

        If :attr:`~Cluster.password` is left blank, ssh will be attempted
        using ssh keys. The private key must be placed in
        <repository_root>/config/ssh/id_rsa and the server must be included
        in the known hosts file at <repository_root>/config/ssh/known_hosts.

        Attributes:
            name (str): The name of the cluster (max_length=20)
            description (str):
                A short description providing notes and information related to
                this cluster
            working_directory (str): Directory on the cluster in which tasks are run
            username (str): username used to log into the cluster
            password (str): password used to log into the cluster
            port (int): Cluster ssh server ssh port (default=22)
            hostname (str): Cluster hostname
            submit_commands (str): The command(s) to be run via an ssh terminal
                submit_commands has access to variables set by either some tasks
                or jobs. When available, they are automatically instered in place
                of the following text (default='clusterside submit')
            cancel_commands (str): The coammnds(s) to be executed to cancel
                a job on the cluster. (default='# clusterside cancel #<- cancel
                commands are not implemented by clusterside.')

            Note:
                Cancel commands are not currently implemented by clusterside.
    """
    name = models.CharField(max_length=20,
                            help_text="Human-readable name of cluster.")
    description = models.TextField(blank=True,
                                   help_text="Human-readable description of cluster.")
    workdir = models.CharField(max_length=250,
                               help_text="Where (full path) to put folders for workflow analysis jobs on the cluster.")
    username = models.CharField(max_length=100,
                                help_text="ssh username")
    password = EncryptedCharField(max_length=100, blank=True, null=True, default=None,
                                  help_text="ssh password. Leave blank for public-key auth. See README for setup.")
    port = models.PositiveIntegerField(default=22,
                                       help_text="ssh port")
    hostname = models.CharField(max_length=250,
                                help_text="ssh hostname")
    submit_commands = models.TextField(default="clusterside submit",
                                       help_text="Commands to run on the cluster to submit a job.")
    cancel_commands = models.TextField(
        default="# clusterside cancel #<- cancel commands are not implemented by clusterside.",
        help_text="NOT IMPLEMENTED.")

    def __str__(self):
        return self.name


class Job(models.Model):
    """
        The Job class contains all information required to run the workflow
        computations on a :class:`remote.Cluster`.

        A job consists of one or more job_manager.models.Task. Tasks are run
        serially, in asending order, according to their Task.order_pos number.
        The tasks are run server side, but asynchronously via a celery worker.

        Jobs should be cluster agnostic.

        Attributes:
            date_created (DateTime): Date the job was
                created, defaults to :meth:`timezone.now`
            auth_token (str): A authentication token used by
                :class:`job_manager.authentication.JobTokenAuthentication` to authenticate
                REST API connections (autogenerated by default)
            user (str): user that created the job
            submission_id (str): UID of the cluster job that is performing the
                job actions.

                submission_id is currently not set by Clusterside. submission_id
                is planned to be used for canceling jobs running on the server.
                Job cancleing is not yet implemented.
            workflow (str): app_name of workflow that submitted the job.
            work_dir (str): the directory on the cluster to perform the task in.
                 This path is relative to the clusters work_dir path.
                 (autogenerated based on the time/date by default)

    """

    class Meta:
        ordering = ['-date_created']

    def generate_work_dir():
        """
            Generate a string to use as the the working directory for a job

            Returns:
                timezone.now().strftime('%s') + "/" as the directory string
        """
        return timezone.now().strftime('%s') + "/"

    def generate_token():
        """
            Generate a valid auth_token

            Returns:
                a binary ascii token compatible with
                :class:`~plantit.job_manager.authentication.JobTokenAuthentication`
        """
        return binascii.hexlify(os.urandom(20)).decode()

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=timezone.now)
    auth_token = models.CharField(max_length=40, default=generate_token)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submission_id = models.CharField(max_length=100, null=True, blank=True)
    workflow = models.CharField(max_length=280, null=True, blank=True)
    cluster = models.ForeignKey(Cluster,
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL)
    work_dir = models.CharField(max_length=100,
                                null=True,
                                blank=True,
                                default=generate_work_dir)
    remote_results_path = models.CharField(max_length=100,
                                           null=True,
                                           blank=True,
                                           default=None)

    def __str__(self):
        return "Job: %s, User %s, Workflow: %s, Status: %s, Cluster: %s" % (self.pk,
                                                                            self.user,
                                                                            self.workflow,
                                                                            self.current_status().state,
                                                                            self.cluster)

    def current_status(self):
        """
            The job's most recent status.

            Returns:
                the most recent status of the job as a :class:`Status` object.
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
            Cancel job async

            Args:
                pk (int): the job pk number

            Returns:
                the :class:`Celery` worker object
        """
        return __cancel_job__.delay(pk)


class Task(models.Model):
    """
        A task that can be run by a Job

        Once a job is started by calling :meth:`Job.run_next`, the first task
        is automatically run, every task after the first will wait until
        the previous task's :meth:`~Task.finish()` method is called.

        New tasks can be created by extending this class. A task begins
        when it's :meth:`~Task.run`  method is called and finished when it's
        :meth:`~Task.finish` method is called. :meth:`~Task.run` is typically
        called automatically by the Job the task is part of. :meth:`~Task.finish`
        must either be called at the end of :meth:`~Task.run` if the task is
        finished when :meth:`~Task.run` is done, or by another method
        if the task must wait for asynchronous processes to finish before it
        is finished (e.g. wait for a job to run on an external cluster)

        Example:

            .. code-block:: python
                :caption: from job_manager.job.DummyTask

                ...
                def run(self):
                    "
                        A task that just marks it run state as run.
                    "
                    self.ran = True
                    self.save()
                    self.finish()
                ...

        Attributes:
            name (str): Name of the task
            description (str): Information and note related to this task
            job (ForeignKey): The job containing this task
            order_pos (int): The position within the job task queue.
                Tasks are executed sequentially according to their
                order_pos. Behavior for multiple tasks with the same order_pos
                is undefined.
            complete (bool): The is completed
            last_updated (DateTime): last time the task was updated, typically,
                changed when the task is created or marked as complete.
    """
    objects = InheritanceManager()
    name = models.CharField(max_length=20, blank=False, null=False)
    description = models.TextField(blank=True)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    order_pos = models.PositiveIntegerField(default=1)
    complete = models.BooleanField(default=False)
    last_updated = models.DateTimeField(default=None, blank=True, null=True)

    class Meta:
        ordering = ['order_pos']

    def run(self):
        """
            Command called to run the task
        """
        raise NotImplementedError

    def __str__(self):
        return "%s (%d)" % (self.name, self.pk)

    def finish(self):
        """
            Mark this task complete and initiate the next task in the
                task queue for the job
        """
        self.complete = True
        self.last_updated = timezone.now()
        self.save()
        return Job.run_next(self.job.pk)


class Status(models.Model):
    """
        Job status object.

        **Possible Status States:**

        - :attr:`Status.COMPLETED` (int): Job is completed
        - :attr:`Status.FAILED` (int): Job failed
        - :attr:`Status.OK` (int): Status update, everything is OK
        - :attr:`Status.WARN` (int): Status update, warning: recoverable error
        - :attr:`Status.CREATED` (int): Job was crated but not yet started

        Attributes:
            job (ForeinKey): The job that this status is liked to
            state (int): The state of this status. Must be one of
                the "Possible Status States" listed above.
            date (DateTime): The time the status was added to the job
            description (str): A string description of why this status
                was added to the job
    """

    # Possible states
    COMPLETED = 1  # Job completed
    FAILED = 2  # Job failed
    OK = 3  # Status update, everything is OK
    WARN = 4  # Status update, warning: recoverable error
    CREATED = 5  # Job was crated but not yet started

    class Meta:
        ordering = ['-date']

    State = (
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (OK, 'OK'),
        (WARN, 'Warning'),
        (CREATED, 'Created')
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    state = models.PositiveIntegerField(choices=State, default=CREATED)
    date = models.DateTimeField(default=timezone.now, blank=True)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.State[self.state - 1][1]


class DummyTask(Task):
    """
        A task that does nothing except keep track of it's run state.

        Attributes:
            ran (bool): set to true when :meth:`run` is called
    """
    ran = models.BooleanField(default=False)

    def run(self):
        self.ran = True
        self.save()
        self.finish()

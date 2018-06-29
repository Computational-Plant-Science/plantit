import binascii
import os

from django.db import models
from django.conf import settings
from django.utils import timezone
from encrypted_model_fields.fields import EncryptedCharField

class Cluster(models.Model):
    """
        Cluster is where Jobs are run
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

class File(models.Model):
    """
        Files that are copied to the cluster server to run the job
    """
    content = models.FileField(upload_to='files/scripts/job_manager/')
    file_name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.file_name)

class Executor(models.Model):
    """
        An executor handles getting a Job running on a Cluster.

        Ideally, executors are cluster agnostic. The cluster object
        should address any commands that are cluster specific, allowing
        the executor to focous on the type of job that is being run.
    """
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    submission_script = models.ForeignKey(File,
                                          blank=True,
                                          null=True,
                                          on_delete=models.SET_NULL,
                                          related_name="submit_script")
    files = models.ManyToManyField(File,blank=True)

    def __str__(self):
        return self.name

class Job(models.Model):
    """
        Specifics to the job that will be submitted to the cluster.

        fields:
        date_created: Date the job was created, defaults to timezone.now()
        cluster: ForeinKey to Cluster, The cluster used to run the job
        executor: ForeignKey to Executor to The code the
            will execute the job on the cluster
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
    executor = models.ForeignKey(Executor,on_delete=models.CASCADE)
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

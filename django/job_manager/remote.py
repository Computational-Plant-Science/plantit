import os
import stat
import errno

import json
from json.decoder import JSONDecodeError

from django.db import models
from django.utils import timezone
from django.core.files.storage import FileSystemStorage

from encrypted_model_fields.fields import EncryptedCharField

import paramiko
from paramiko.ssh_exception import AuthenticationException

from .job import Task, Job, Status

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

class SSHTaskMixin(models.Model):
    """
        Implements a run() method required for :class:`job_manager.models.Task`
        that opens an ssh connection client and sftp to the job's cluster when
        the task is run, then calls self.ssh(). Also handels closing the ssh
        connections after self.ssh() returns or if ssh() thorws an exception.

        Classes extending this mixin must also extend :class:`job_manager.models.Task`
        and should implment the ssh(self,client) method and perform task
        functions within instead of in run().

        SSHTaskMixin handles silently IOError and AuthenticationException
        Exceptions (including ones raised by the ssh() method) by marking the
        job failed. Any other exceptions raised by ssh() will cause the job
        status to be set to failed and the exception reraised.

        The SSHTaskMixin must be extdned before Task:

        Example:
            class SomeTask(SSHTaskMixin,Task): #<- This is correct
                pass

            class SomeTask(Task,SSHTaskMixin): #<- Task's run() will run instead
                pass

        Attributes:
            cluster (ForeignKey): ForeinKey to Cluster,
                The cluster used to run the task
            client (:class:`paramako.SSHClient`): ssh connection to the cluster
            sftp (:class:`paramiko.sft_client.SFTPClient`): sftp connection to the
                            cluster. The connection is chdir'd into self.workdir
            workdir (str): full path of the job's working directory on the cluster
    """
    class Meta:
        abstract = True

    cluster = models.ForeignKey(Cluster,on_delete=models.CASCADE)

    def run(self):
        #Open Connection
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(self.cluster.hostname,
                           self.cluster.port,
                           self.cluster.username,
                           self.cluster.password)
        except (AuthenticationException) as e:
            self.job.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description=str(e))
            return

        self.client = client
        self.sftp = self.client.open_sftp()
        self.workdir = self.cluster.workdir + "/" + self.job.work_dir

        #Chdir into working directory
        try:
            self.sftp.chdir(self.cluster.workdir)
        except OSError:
            self.job.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description="Cluster Workdir does not exist")
            client.close()
            return
        try: #OSError raised if dir already exists
            self.sftp.mkdir(self.job.work_dir)
        except OSError as e:
            pass
        self.sftp.chdir(self.job.work_dir)

        #Run task
        try:
            self.ssh()
        except IOError as e:
            self.job.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description=str(e))
            return
        except Exception as e:
            self.job.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description=str(e))
            raise e
        finally:
            client.close()
            self.sftp.close()

class File(models.Model):
    """
        Files that are copied to the cluster server to run a SubmissionTask

        Attributes:
            content (:class:`File`): The file
            file_name (str): Name of the file
    """
    content = models.FileField(upload_to='files/scripts/job_manager/')
    file_name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.file_name)

class SubmissionTask(SSHTaskMixin, Task):
    """
        A job task for submitting jobs to a Cluster.

        The submission task sshes into the cluster, copies its submission script
        and files into the Job's working directory, the executes the cluster's
        ":attr:job_manager.models.Cluster.submit_commands", substuting the "{}"
        strings listed in :meth:`format_cluster_cmds` for their respective values.

        Submission tasks should be cluster agnostic. The cluster object
        should address any commands that are cluster specific.

        Attributes:
            submission_script (ForeignKey): the script (:class:`File`) executed
                on the cluster
            files (ManyToMany): The other :class:`File`s uploaded to the server
            paramaters (str): JSON encoded set of paramters to pass to
                submission_script upon execution (see :meth:`format_cluster_cmds`)
    """
    submission_script = models.ForeignKey(File,
                                          blank=True,
                                          null=True,
                                          on_delete=models.SET_NULL,
                                          related_name="submit_script")
    files = models.ManyToManyField(File,blank=True)
    parameters = models.TextField(null=True,blank=True)

    def format_cluster_cmds(self,cmds):
        """
            Replaces predfined string toeksn with saved information,
            tokens that replaced are:

            {job_pk}      the job pk
            {auth_token}  the REST authentication token for the job
            {sub_script}  the name of the script to run, provided by the task to be run
            {task_pk}     the pk of the current task
            {params}      the paramaters stored in the parameters field

            Throws:
                json.decoder.JSONDecodeError if paramaters are not decodeable
        """
        if(self.submission_script):
            cmds = cmds.replace("{sub_script}", os.path.basename(self.submission_script.file_name))
        cmds = cmds.replace("{job_pk}", str(self.job.pk))
        cmds = cmds.replace("{auth_token}", str(self.job.auth_token))
        cmds = cmds.replace("{task_pk}",str(self.pk))
        if(self.parameters):
            params = json.loads(self.parameters)
            for key,value in params.items():
                cmds = cmds.replace("{%s}"%(key,),value)
        if(self.job.submission_id):
            cmds = cmds.replace("{sub_id}", str(self.job.submission_id))
        return cmds

    def ssh(self):
        """
            Copies script files, and executes the
            submission script

            Exceptions:
                IOError: thrown during copying of files
        """

        #Copy run scripts to cluster
        FILE_PERMISSIONS = stat.S_IRUSR | stat.S_IXUSR

        for f in self.files.all():
            fname = os.path.basename(f.file_name)
            self.sftp.put(f.content.path, fname)
            self.sftp.chmod(fname,FILE_PERMISSIONS)
        if(self.submission_script):
            f = self.submission_script
            fname = os.path.basename(f.file_name)
            self.sftp.put(f.content.path, fname)
            self.sftp.chmod(fname,FILE_PERMISSIONS)

        try:
            #Submit job to cluster queue
            cmds = "cd " + self.workdir + "; " + self.cluster.submit_commands
            cmds = self.format_cluster_cmds(cmds.replace('\r\n','\n').replace('\r','\n'))
            stdin, stdout, stderr = self.client.exec_command(cmds)
            error = str(stderr.readlines())

            if(error != "[]"):
                if len(error) > 200:
                    error = (error[:100] + "..." + error[-100:])
                self.job.status_set.create(state=Status.FAILED,
                            date=timezone.now(),
                            description=error)
                return

        except JSONDecodeError as e:
            msg = "Paramater Decode Error: " + str(e)
            self.job.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description=msg)

class UploadFileTask(SSHTaskMixin,Task):
    """
        Uploads a list of files to the server to a files folder in
            the job work directory

        Attributes:
            fields (str): comma-seperated list of paths of files to uplaod,
                paths must be relative to pwd field
            backend (str): File system backend to use, supported options are:
                ====================  ====================================================
                Option                Class Loaded
                ====================  ====================================================
                "FileSystemStorage"   :class:`django.core.files.storage.FileSystemStorage`
                ====================  ====================================================

            pwd (str): File system working directory
    """

    SUPPORTED_FILE_SYSTEMS = (('FileSystemStorage','FileSystemStorage'),)

    files = models.TextField(blank=False)
    backend = models.CharField(choices=SUPPORTED_FILE_SYSTEMS,
                               blank=False,
                               max_length=100)
    pwd = models.CharField(max_length=250)

    def ssh(self):
        file_paths = self.files.split(',')
        dir = "files/"

        if(self.backend == 'FileSystemStorage'):
            file_storage = FileSystemStorage(self.pwd)

        try: #OSError raised if dir already exists
            self.sftp.mkdir(dir)
        except OSError as e:
            pass

        for file_name in file_paths:
            file = file_storage.open(file_name)
            fname = dir + "/" + os.path.basename(file.name)
            self.sftp.putfo(file, fname)

        self.finish()

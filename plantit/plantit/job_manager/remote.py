"""
    Tasks for working with remove servers.
"""

import json
import os
import stat
from json.decoder import JSONDecodeError
from os import path

import paramiko
from django.conf import settings
from django.db import models
from django.utils import timezone
from paramiko.ssh_exception import AuthenticationException

from .job import Task, Status, Cluster
from ..file_manager import permissions
from ..workflows import registrar


class SSHTaskMixin(models.Model):
    """
        Implements a run() method for :class:`job_manager.job.Task`
        that opens an ssh connection client and sftp to the job's cluster when
        the task is run, then calls self.ssh(). Also handles closing the ssh
        connections after self.ssh() returns or if ssh() throws an exception.

        Classes extending this mixin must also extend :class:`job_manager.models.Task`
        and should implement the ssh(self,client) method and perform task
        functions within instead of in run().

        SSHTaskMixin handles silently IOError and AuthenticationException
        Exceptions (including ones raised by the ssh() method) by marking the
        job failed. Any other exceptions raised by ssh() will cause the job
        status to be set to failed and the exception re-raised.

        Note:
            The SSHTaskMixin must be extended before Task:

            Example:

                .. code-block:: python

                    class SomeTask(SSHTaskMixin,Task): #<- This is correct
                        pass

                    class SomeTask(Task,SSHTaskMixin): #<- Task's run() will run instead
                        pass

        Example:

            .. code-block:: python

                class SomeTask(SSHTaskMixin,Task):

                    def ssh(self):
                        #Access self.client for running
                        # ssh bash commands
                        # or self.sftp for sending/gettings
                        # files via sftp.
                        # the workdirectory of the job can be
                        # found in
                        # self.workdir.

        See :class:`SubmissionTask` for a full example of using this mixin.

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

    cluster = models.ForeignKey(Cluster, on_delete=models.CASCADE)

    def run(self):
        # Open Connection
        try:
            client = paramiko.SSHClient()
            if getattr(settings, 'DEBUG', False):
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            else:
                client.load_system_host_keys("../config/ssh/known_hosts")
                client.set_missing_host_key_policy(paramiko.RejectPolicy())
            if self.cluster.password is None:
                # Use ssh key
                k = paramiko.RSAKey.from_private_key_file('../config/ssh/id_rsa')
                client.connect(self.cluster.hostname,
                               self.cluster.port,
                               self.cluster.username,
                               pkey=k)
            else:
                # Use password
                client.connect(self.cluster.hostname,
                               self.cluster.port,
                               self.cluster.username,
                               self.cluster.password)
        except AuthenticationException as e:
            self.job.status_set.create(state=Status.FAILED,
                                       date=timezone.now(),
                                       description=str(e))
            return

        self.client = client
        self.sftp = self.client.open_sftp()
        self.workdir = self.cluster.workdir + "/" + self.job.work_dir

        # Chdir into working directory
        try:
            self.sftp.chdir(self.cluster.workdir)
        except OSError:
            self.job.status_set.create(state=Status.FAILED,
                                       date=timezone.now(),
                                       description="Cluster Workdir does not exist")
            client.close()
            return
        try:  # OSError raised if dir already exists
            self.sftp.mkdir(self.job.work_dir)
        except OSError as e:
            pass
        self.sftp.chdir(self.job.work_dir)

        # Run task
        try:
            print(self.ssh)
            self.ssh()
        except IOError as e:
            self.job.status_set.create(state=Status.FAILED,
                                       date=timezone.now(),
                                       description=("Plant IT Internal IOError Error During"
                                                    " Submission, please contact admins"))
            return
        except Exception as e:
            self.job.status_set.create(state=Status.FAILED,
                                       date=timezone.now(),
                                       description=("Plant IT Internal Error During" +
                                                    " Submission, please contact admins"))
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
        :attr:`job_manager.remote.Cluster.submit_commands`.

        Submission tasks should be cluster agnostic. The cluster object
        should address any commands that are cluster specific.

        Attributes:
            parameters (str containing a JSON object): The workflow user
                parameters as set by the user during submission.
            app_name (str): The app_name of the workflow to run (Required)
    """

    parameters = models.TextField(null=True, blank=True)
    app_name = models.CharField(max_length=40)

    def get_params(self):
        """
            Combines workflow and server set parameters into a JSON
            object to be saved provided as the workflow.json file
            to ClusterSide.

            Returns:
                JSON Object containing workflow parameters for this job.
        """

        # Workflow specific configuration in workflow.WORKFLOW dictionary
        config = registrar.list[self.app_name]

        params = {
            "server_url": settings.API_URL,
            "job_pk": self.job.pk,
            "auth_token": self.job.auth_token,
            "task_pk": self.pk,
            "parameters": json.loads(self.parameters)
        }
        params.update(config)  # Add config from workflow.WORKFLOW

        return json.dumps(params)

    def ssh(self):
        """
            Copies script files, and executes the
            submission script

            Exceptions:
                IOError: thrown during copying of files
        """

        # Copy run scripts to cluster
        FILE_PERMISSIONS = stat.S_IRUSR | stat.S_IXUSR

        with open(path.join('workflows', str(self.app_name), 'process.py'), 'r') as file:
            fname = os.path.basename(file.name)
            self.sftp.putfo(file, fname)

        with self.sftp.open('workflow.json', 'w') as file:
            file.write(self.get_params())

        try:
            # Submit job to cluster queue
            cmds = "cd " + self.workdir + "; " + self.cluster.submit_commands
            stdin, stdout, stderr = self.client.exec_command(cmds)

            if stdout.channel.recv_exit_status():
                error = "stderr: " + str(stderr.readlines())
                error = error + " stdout: " + str(stdout.readlines())
                if len(error) > 900:
                    error = error[:450] + "..." + error[-450:]
                print(error)
                self.job.status_set.create(state=Status.FAILED,
                                           date=timezone.now(),
                                           description="Plant IT Internal Error: " + error)
                return

        except JSONDecodeError as e:
            msg = "Paramater Decode Error: " + str(e)
            self.job.status_set.create(state=Status.FAILED,
                                       date=timezone.now(),
                                       description=msg)


class UploadCollectionTask(SSHTaskMixin, Task):
    """
        Uploads all the files in a collection to the server to the files folder
        in the job wok directory.

        Note:
            This was, and could be, used in conjunction with a
            :class:`~plantit.file_manager.filesystems.local.Local` file system
            to copy :class:`~plantit.collection.models.Sample` files saved
            locally on the server to the cluster for analysis.

            In the current build of Plant IT, such local file systems are not
            supported.
    """
    collection_dir = "samples/"

    def ssh(self):
        collection = self.job.collection.cast()  # Cast down to access the files attribute

        with self.sftp.open('samples.json', 'w') as file:
            file.write(collection.to_json())

        file_storage = permissions.open_folder(storage_type=collection.storage_type,
                                               path=collection.base_file_path,
                                               user=self.job.user)

        self.finish()


class UploadFileTask(SSHTaskMixin, Task):
    """
        Uploads a list of files to the job work directory on the server.

        Attributes:
            fields (str): comma-seperated list of paths of files to uplaod,
                paths must be relative to webserver root
            delete (bool): delete local file after upload
    """

    files = models.TextField(blank=False, null=False)
    delete = models.BooleanField(default=False)

    def ssh(self):
        file_paths = self.files.split(',')

        for file_name in file_paths:
            file = open(file_name)
            fname = os.path.basename(file.name)
            self.sftp.putfo(file, fname)
            if self.delete:
                os.remove(file_name)

        self.finish()

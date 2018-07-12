import os
import stat
import errno

import json
from json.decoder import JSONDecodeError

from django.db import models
from django.utils import timezone
from django.core.files.storage import FileSystemStorage

import paramiko
from paramiko.ssh_exception import AuthenticationException


from .models import Task, Job, Status

"""
    Classes that implment unimplmented methdos of their parent classes.

    These classes are not vital to the core of the app, but are required
    to have a working example.
"""
class File(models.Model):
    """
        Files that are copied to the cluster server to run a SubmissionTask
    """
    content = models.FileField(upload_to='files/scripts/job_manager/')
    file_name = models.CharField(max_length=100)

    def __str__(self):
        return str(self.file_name)

class DummyTask(Task):
    """
        A task that does nothing except keep track of its run state
    """
    ran = models.BooleanField(default=False)

    def run(self):
        self.ran = True
        self.save()

class SubmissionTask(Task):
    """
        A job task for submitting jobs to a Cluster.

        Submission tasks should be cluster agnostic. The cluster object
        should address any commands that are cluster specific.
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
        job = self.job

        cmds = cmds.replace("{sub_script}", os.path.basename(self.submission_script.file_name))
        cmds = cmds.replace("{job_pk}", str(job.pk))
        cmds = cmds.replace("{auth_token}", str(job.auth_token))
        cmds = cmds.replace("{task_pk}",str(self.pk))
        if(self.parameters):
            params = json.loads(self.parameters)
            for key,value in params.items():
                cmds = cmds.replace("{%s}"%(key,),value)
        if(job.submission_id):
            cmds = cmds.replace("{sub_id}", str(job.submission_id))
        return cmds

    def run(self):
        """
            This function opens an ssh connection and
            submit the passed job

            Exceptions that should be caught:
            IOError: thrown during copyting of files
            AuthenticationException: thrown if login to server fails
        """
        job = self.job
        cluster = job.cluster
        dir = job.work_dir

        try:
            #Connect to server
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(cluster.hostname,
                           cluster.port,
                           cluster.username,
                           cluster.password)

            #Copy run scripts to cluster
            FILE_PERMISSIONS = stat.S_IRUSR | stat.S_IXUSR
            sftp = client.open_sftp()
            sftp.chdir(path=cluster.workdir)

            try:
                sftp.mkdir(dir)
            except OSError as e:
                #Raised if dir already exists
                pass

            for f in self.files.all():
                fname = dir + "/" + os.path.basename(f.file_name)
                sftp.put(f.content.path, fname)
                sftp.chmod(fname,FILE_PERMISSIONS)
            if(self.submission_script):
                f = self.submission_script
                fname = dir + "/" + os.path.basename(f.file_name)
                sftp.put(f.content.path, fname)
                sftp.chmod(fname,FILE_PERMISSIONS)
            sftp.close()

            #Submit job to cluster queue
            cmds = "cd " + cluster.workdir + "/" + dir + " ; " + cluster.submit_commands
            cmds = self.format_cluster_cmds(cmds)
            stdin, stdout, stderr = client.exec_command(cmds)
            error = stderr.readlines()
            client.close()

            if(error):
                job.status_set.create(state=Status.FAILED,
                            date=timezone.now(),
                            description=str(error))
                return

        except (AuthenticationException, IOError) as e:
            job.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description=str(e))
        except JSONDecodeError as e:
            msg = "Paramater Decode Error: " + str(e)
            job.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description=msg)
        except Exception as e:
            job.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description="Internal Server Error During SubmissionTask.run()")
            raise e

class UploadFileTask(Task):
    """
        Uploads a list of files to the server to a files folder in
            the job work directory

        fields: comma-seperated list of paths of files to uplaod,
            paths must be relative to pwd field
        backend: File system backend to use, supported options are:
            "FileSystemStorage" : django.core.files.storage.FileSystemStorage
        pwd: File system working directory
    """
    SUPPORTED_FILE_SYSTEMS = (('FileSystemStorage','FileSystemStorage'),)

    files = models.TextField(blank=False)
    backend = models.CharField(choices=SUPPORTED_FILE_SYSTEMS,
                               blank=False,
                               max_length=100)
    pwd = models.CharField(max_length=250)

    def run(self):
        job = self.job
        cluster = job.cluster
        file_paths = self.files.split(',')
        dir = job.work_dir + "/files/"

        if(self.backend == 'FileSystemStorage'):
            file_storage = FileSystemStorage(self.pwd)

        try:
            #Connect to server
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(cluster.hostname,
                           cluster.port,
                           cluster.username,
                           cluster.password)

            #Copy files to cluster
            FILE_PERMISSIONS = stat.S_IRUSR | stat.S_IXUSR
            sftp = client.open_sftp()
            sftp.chdir(path=cluster.workdir)

            #OSError raised if dir already exists
            try:
                sftp.mkdir(job.work_dir)
            except OSError as e:
                pass
            try:
                sftp.mkdir(dir)
            except OSError as e:
                pass

            for file_name in file_paths:
                file = file_storage.open(file_name)
                fname = dir + "/" + os.path.basename(file.name)
                sftp.putfo(file, fname)

            self.finish()
        except (AuthenticationException, IOError) as e:
            job.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description=str(e))
        except Exception as e:
            job.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description="Internal Server Error During UploadFileTask.run()")
            raise e

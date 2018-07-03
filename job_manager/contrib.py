import os
import stat

from django.db import models
from django.utils import timezone

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

    def format_cluster_cmds(self,cmds):
        """
            Replaces predfined string toeksn with saved information,
            tokens that replaced are:

            {job_pk}      the job pk
            {auth_token}  the REST authentication token for the job
            {sub_script}  the name of the script to run, provided by the task to be run
        """
        job = self.job

        cmds = cmds.replace("{sub_script}", os.path.basename(self.submission_script.file_name))
        cmds = cmds.replace("{job_pk}", str(job.pk))
        cmds = cmds.replace("{auth_token}", str(job.auth_token))
        cmds = cmds.replace("{task_pk}",str(self.pk))
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
            dir = str(job.pk) + "_" + timezone.now().strftime('%s')
            sftp.mkdir(dir) #Throws IOError if directory already exists
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
                self.complete = False
                return


        except (AuthenticationException, IOError) as e:
            job.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description=str(e))
        except Exception as e:
            job.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description="Internal Server Error")
            raise e

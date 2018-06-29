# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task

import binascii
import os
import stat

from django.utils import timezone
import paramiko
from paramiko.ssh_exception import AuthenticationException
from job_manager.models import Job, Status

def generate_job_token():
    return binascii.hexlify(os.urandom(20)).decode()

def format_cluster_cmds(cmds,job):
    if(job.executor.submission_script):
        cmds = cmds.replace("{sub_script}", os.path.basename(job.executor.submission_script.file_name))
    cmds = cmds.replace("{job_pk}", str(job.pk))
    cmds = cmds.replace("{auth_token}", str(job.auth_token))
    if(job.submission_id):
        cmds = cmds.replace("{sub_id}", str(job.submission_id))
    return cmds

@shared_task
def __submit_job__(pk):
    """
        This function opens an ssh connection and
        submit the passed job

        Exceptions that should be caught:
        IOError: thrown during copyting of executor files
        AuthenticationException: thrown if login to server fails
    """
    job = Job.objects.get(pk=pk)
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
        for f in job.executor.files.all():
            fname = dir + "/" + os.path.basename(f.file_name)
            sftp.put(f.content.path, fname)
            sftp.chmod(fname,FILE_PERMISSIONS)
        if(job.executor.submission_script):
            f = job.executor.submission_script
            fname = dir + "/" + os.path.basename(f.file_name)
            sftp.put(f.content.path, fname)
            sftp.chmod(fname,FILE_PERMISSIONS)
        sftp.close()

        #Submit job to cluster queue
        cmds = "cd " + cluster.workdir + "/" + dir + " ; " + cluster.submit_commands
        cmds = format_cluster_cmds(cmds,job)
        stdin, stdout, stderr = client.exec_command(cmds)
        error = stderr.readlines()
        client.close()

        if(error):
            job.status_set.create(state=Status.FAILED,
                        date=timezone.now(),
                        description=str(error))

    except (AuthenticationException, IOError) as e:
        job.status_set.create(state=Status.FAILED,
                    date=timezone.now(),
                    description=str(e))
    except Exception as e:
        job.status_set.create(state=Status.FAILED,
                    date=timezone.now(),
                    description="Internal Server Error")
        raise e

@shared_task
def __cancel_job__(pk):
    """
        This function will open an ssh connection and
        cancel the passed job
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

def submit_job(pk):
    """
        Submit job async
    """
    __submit_job__.delay(pk)

def cancel_job(pk):
    """
        Cancel job async
    """
    __cancel_job__.delay(pk)

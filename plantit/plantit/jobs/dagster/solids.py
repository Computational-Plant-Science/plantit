import json
import sys
from os import path
import traceback

from dagster import solid, String, FileHandle, List, LocalFileHandle, composite_solid, Bool, Tuple, Dict
from django.utils import timezone

from .types import DagsterJob
from ..models.abstract_status import AbstractStatus
from ..ssh import SSH, DagsterSSHOptions


@solid
def sftp_upload_text(context, ssh_options: DagsterSSHOptions, text: str, remote_path: str):
    ssh = SSH.from_options(ssh_options)
    with ssh:
        sftp = ssh.client.open_sftp()
        with sftp.open(remote_path, 'w') as file:
            file.write(text)

    context.log.info(f"Uploaded text content to '{remote_path}' on '{ssh_options.host}'")


@solid
def sftp_upload_file(context, ssh_options: DagsterSSHOptions, file: FileHandle, remote_path: str):
    ssh = SSH.from_options(ssh_options)
    with ssh:
        sftp = ssh.client.open_sftp()
        local_path = context.file_manager.copy_handle_to_local_temp(file)
        sftp.put(local_path, remote_path)
        sftp.close()

    context.log.info(f"Uploaded file '{local_path}' to '{remote_path}' on '{ssh_options.host}'")


@solid
def ssh_execute(context, ssh_options: DagsterSSHOptions, command: str) -> Tuple[Bool, List[String]]:
    ssh = SSH.from_options(ssh_options)
    with ssh:
        stdin, stdout, stderr = ssh.client.exec_command(command)

        if stdout.channel.recv_exit_status():
            context.log.error(f"Executing '{command}' on '{ssh_options.host}' returned non-zero exit code")
            return False, stdout.readlines() + stderr.readlines()
        else:
            context.log.info(f"Executing '{command}' on '{ssh_options.host}' returned successfully")
            return True, stdout.readlines() + stderr.readlines()


@solid
def upload_workflow_collection(context, job: Dict) -> Dict:
    try:
        remote_path = path.join(job['cluster']['workdir'], job['work_dir'], 'samples.json')
        ssh = SSH(job['cluster']['hostname'], job['cluster']['port'], job['cluster']['username'], job['cluster']['password'])
        with ssh:
            sftp = ssh.client.open_sftp()
            with sftp.open(remote_path, 'w') as file:
                file.write(json.dumps(job['collection']))

        context.log.info(
            f"Uploaded collection '{job['collection']['name']}' for workflow '{job['workflow']}' job '{job['pk']}' to working directory '{job['work_dir']}' on cluster '{job['cluster']['hostname']}'")
        return job
    except Exception:
        msg = f"Failed to upload collection '{job['collection']['name']}' for workflow '{job['workflow']}' job '{job['pk']}' to working directory '{job['work_dir']}' on cluster '{job['cluster']['hostname']}': {traceback.format_exc()}"
        context.log.error(msg)


@solid
def upload_workflow_definition(context, job: Dict) -> Dict:
    try:
        remote_path = path.join(job['cluster']['workdir'], job['work_dir'], 'process.py')
        ssh = SSH(job['cluster']['hostname'], job['cluster']['port'], job['cluster']['username'], job['cluster']['password'])
        with ssh:
            sftp = ssh.client.open_sftp()
            local_path = context.file_manager.copy_handle_to_local_temp(
                LocalFileHandle(path.join('workflows', job['workflow'], 'process.py')))

            sftp.put(local_path, remote_path)
            sftp.close()

        context.log.info(
            f"Uploaded workflow '{job['workflow']}' definition for job '{job['pk']}' to working directory '{job['work_dir']}' on cluster '{job['cluster']['hostname']}'")
        return job
    except Exception:
        msg = f"Failed to upload workflow '{job['workflow']}' definition for job '{job['pk']}' to working directory '{job['work_dir']}' on cluster '{job['cluster']['hostname']}': {traceback.format_exc()}"
        context.log.error(msg)


@solid
def upload_workflow_parameters(context, job: Dict) -> Dict:
    try:
        remote_path = path.join(job['cluster']['workdir'], job['work_dir'], 'workflow.json')
        ssh = SSH(job['cluster']['hostname'], job['cluster']['port'], job['cluster']['username'], job['cluster']['password'])
        with ssh:
            sftp = ssh.client.open_sftp()
            with sftp.open(remote_path, 'w') as file:
                file.write(json.dumps(job['parameters']))
            sftp.close()

        context.log.info(
            f"Uploaded workflow '{job['workflow']}' parameters for job '{job['pk']}' to working directory '{job['work_dir']}' on cluster '{job['cluster']['hostname']}'")
        return job
    except Exception:
        msg = f"Failed to upload workflow '{job['workflow']}' parameters for job '{job['pk']}' to working directory '{job['work_dir']}' on cluster '{job['cluster']['hostname']}': {traceback.format_exc()}"
        context.log.error(msg)


@solid
def create_directory(context, job: Dict) -> Dict:
    try:
        cmd = "cd " + path.join(job['cluster']['workdir']) + "; mkdir " + job['work_dir']
        context.log.info(cmd)
        ssh = SSH(job['cluster']['hostname'], job['cluster']['port'], job['cluster']['username'], job['cluster']['password'])
        with ssh:
            stdin, stdout, stderr = ssh.client.exec_command(cmd)
            output = stdout.readlines() + stderr.readlines()

            if stdout.channel.recv_exit_status():
                raise Exception(f"Got error output: {output}")
            else:
                context.log.info(
                    f"Created working directory '{job['work_dir']}' for workflow '{job['workflow']}' job '{job['pk']}' on cluster '{job['cluster']['hostname']}' with output: {output}")
                return job

    except Exception:
        msg = f"Failed to create working directory '{job['work_dir']}' for workflow '{job['workflow']}' job '{job['pk']}' on cluster '{job['cluster']['hostname']}': {traceback.format_exc()}"
        context.log.error(msg)


@composite_solid
def upload_workflow(job: Dict) -> Dict:
    return upload_workflow_collection(upload_workflow_parameters(upload_workflow_definition(job)))


@solid
def execute_workflow(context, job: Dict) -> Dict:
    try:
        cmd = "cd " + path.join(job['cluster']['workdir'], job['work_dir']) + "; " + job['cluster']['submit_commands']
        ssh = SSH(job['cluster']['hostname'], job['cluster']['port'], job['cluster']['username'], job['cluster']['password'])
        with ssh:
            stdin, stdout, stderr = ssh.client.exec_command(cmd)
            output = stdout.readlines() + stderr.readlines()

            if stdout.channel.recv_exit_status():
                raise Exception(f"Got error output: {output}")
            else:
                context.log.info(
                    f"Executed workflow '{job['workflow']}' job '{job['pk']}' in working directory '{job['work_dir']}' on cluster '{job['cluster']['hostname']}' with output: {output}")
                return job

    except Exception:
        msg = f"Failed to execute workflow '{job['workflow']}' job '{job['pk']}' in working directory '{job['work_dir']}' on cluster '{job['cluster']['hostname']}': {traceback.format_exc()}"
        context.log.error(msg)

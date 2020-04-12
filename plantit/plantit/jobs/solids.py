from os import path

import json

from dagster import solid, Field, String
from django.conf import settings

from ..workflows import registrar


@solid(required_resource_keys={'ssh_client'})
def upload_workflow(context, working_directory: str, definition: str, parameters: str):
    content = {
        "server_url": settings.API_URL,
        "parameters": json.loads(parameters)
    }
    content.update(registrar.list[definition])
    with context.resources.ssh_client as client:
        with client.client.sftp as sftp:
            sftp.chdir(working_directory)
            with open(path.join('workflows', str(definition), 'process.py'), 'r') as file:
                sftp.putfo(file, path.basename(file.name))
            with sftp.open('workflow.json', 'w') as file:
                file.write(json.dumps(content))


@solid(required_resource_keys={'ssh_client'})
def setup_workflow(context, working_directory: str, command: str):
    with context.resources.ssh_client as client:
        cmd = "cd " + working_directory + "; " + command
        stdin, stdout, stderr = client.exec_command(cmd)
        if stdout.channel.recv_exit_status():
            error = "stderr: " + str(stderr.readlines())
            error = error + " stdout: " + str(stdout.readlines())
            print(error)


@solid(
    required_resource_keys={'ssh_client'},
    config = {
        'submit_command': Field(
            String,
            is_required=True,
            description='The command to submit the workflow to the cluster.',
        )
    }
)
def run_workflow(context, working_directory: str):
    with context.resources.ssh_client as client:
        cmd = "cd " + working_directory + "; " + context.solid_config['submit_command']
        stdin, stdout, stderr = client.exec_command(cmd)
        if stdout.channel.recv_exit_status():
            error = "stderr: " + str(stderr.readlines())
            error = error + " stdout: " + str(stdout.readlines())
            print(error)


@solid(required_resource_keys={'ssh_client'})
def download_results(context):
    return


@solid(required_resource_keys={'ssh_client'})
def cleanup(context):
    return


@solid
def not_much(_):
    return
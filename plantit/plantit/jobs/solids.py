import json

from dagster import solid
from django.conf import settings


@solid(required_resource_keys={'ssh_client'})
def upload(context):
    with context.resources.ssh_client as client:
        with client.client.sftp.open('workflow.json', 'w') as file:
            file.write(json.dumps({
                "server_url": settings.API_URL,
            }))


@solid(required_resource_keys={'ssh_client'})
def prerun(context):
    pass


@solid(required_resource_keys={'ssh_client'})
def run(context):
    pass


@solid(required_resource_keys={'ssh_client'})
def postrun(context):
    pass


@solid(required_resource_keys={'ssh_client'})
def download(context):
    pass


@solid
def not_much(_):
    return
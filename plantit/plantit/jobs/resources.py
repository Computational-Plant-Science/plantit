from dagster import resource, Field, String, Int

from plantit.jobs.ssh_client import SSHClient


@resource(config={
    'host': Field(String),
    'port': Field(Int),
    'username': Field(String),
    'password': Field(String)
})
def test_ssh_client_resource(context):
    return SSHClient(
        context.resource_config['host'],
        context.resource_config['port'],
        context.resource_config['username'],
        context.resource_config['password'])
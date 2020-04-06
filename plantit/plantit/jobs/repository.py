from dagster import Field, String, Int, resource
from dagster import RepositoryDefinition

from plantit.jobs.pipelines import parallel_pipeline, workflow
from plantit.jobs.ssh_client import SSHClient


@resource(config={'host': Field(String), 'port': Field(Int), 'username': Field(String), 'password': Field(String)})
def ssh_client_resource(context):
    return SSHClient(
        context.resource_config['host'],
        context.resource_config['port'],
        context.resource_config['username'],
        context.resource_config['password'])


def define_repo():
    return RepositoryDefinition(
        name='default', pipeline_defs=[parallel_pipeline, workflow]
    )

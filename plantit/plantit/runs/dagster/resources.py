from dagster import resource, Field, String, Int, Optional

from plantit.runs.ssh import SSH


@resource(config_schema={
    'host': Field(String),
    'port': Field(Int),
    'username': Field(String),
})
def ssh_resource(context):
    return SSH(
        context.resource_config['host'],
        context.resource_config['port'],
        context.resource_config['username'])
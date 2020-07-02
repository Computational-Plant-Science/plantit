from dagster import resource, Field, String, Int, Optional

from plantit.jobs.ssh import SSH


@resource(config_schema={
    'host': Field(String),
    'port': Field(Int),
    'username': Field(String),
    'password': Field(Optional[String])
})
def ssh_resource(context):
    return SSH(
        context.resource_config['host'],
        context.resource_config['port'],
        context.resource_config['username'],
        context.resource_config['password'])
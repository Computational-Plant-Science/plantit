import paramiko

from dagster import ModeDefinition, default_executors, pipeline, solid, Field, String, Int, resource
from dagster import RepositoryDefinition
from dagster_celery import celery_executor


class SSHClient:
    def __init__(self, host: str, port: int, username: str, password: str = None):
        self.client = None
        self.port = port
        self.host = host
        self.username = username
        self.password = password

    def __enter__(self):
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        if self.password:
            client.connect(self.host, self.port, self.username, self.password)
        else:
            client.connect(self.host, self.port, self.username)

        self.client = client

    def __exit__(self, exc_type, exc_value, traceback):
        self.client.close()


@resource(config={'host': Field(String), 'port': Field(Int), 'username': Field(String), 'password': Field(String)})
def ssh_client_resource(context):
    return SSHClient(
        context.resource_config['host'],
        context.resource_config['port'],
        context.resource_config['username'],
        context.resource_config['password'])


@solid(required_resource_keys={'ssh_client'})
def upload(context):
    pass


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


@pipeline(mode_defs=[
    ModeDefinition(
        resource_defs={'ssh_client', ssh_client_resource},
        executor_defs=default_executors + [celery_executor]
    )
])
def parallel_pipeline():
    for i in range(50):
        not_much.alias('not_much_' + str(i))()


def define_repo():
    return RepositoryDefinition(
        name='parallel_pipeline', pipeline_defs=[parallel_pipeline]
    )

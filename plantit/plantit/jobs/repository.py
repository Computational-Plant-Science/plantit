from dagster import ModeDefinition, default_executors, pipeline, solid
from dagster import RepositoryDefinition
from dagster_celery import celery_executor

celery_mode_defs = [ModeDefinition(executor_defs=default_executors + [celery_executor])]


@solid(required_resource_keys={'paramiko'})
def upload(context):
    pass


@solid(required_resource_keys={'paramiko'})
def prerun(context):
    pass


@solid(required_resource_keys={'paramiko'})
def run(context):
    pass


@solid(required_resource_keys={'paramiko'})
def postrun(context):
    pass


@solid(required_resource_keys={'paramiko'})
def download(context):
    pass


@solid
def not_much(_):
    return


@pipeline(mode_defs=celery_mode_defs)
def parallel_pipeline():
    for i in range(50):
        not_much.alias('not_much_' + str(i))()


def define_repo():
    return RepositoryDefinition(
        name='parallel_pipeline', pipeline_defs=[parallel_pipeline]
    )

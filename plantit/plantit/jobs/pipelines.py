from dagster import pipeline, ModeDefinition, default_executors
from dagster_celery import celery_executor

from plantit.jobs.repository import ssh_client_resource
from plantit.jobs.solids import not_much, upload, prerun, run, postrun, download


@pipeline(mode_defs=[
    ModeDefinition(
        name='default',
        executor_defs=default_executors + [celery_executor]
    )
])
def parallel_pipeline():
    for i in range(50):
        not_much.alias('not_much_' + str(i))()


@pipeline(mode_defs=[
    ModeDefinition(
        name='default',
        resource_defs={'ssh_client': ssh_client_resource},
        executor_defs=default_executors + [celery_executor]
    )
])
def workflow():
    upload()
    prerun()
    run()
    postrun()
    download()
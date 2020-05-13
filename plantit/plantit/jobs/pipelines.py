from dagster import pipeline, ModeDefinition, default_executors
from dagster_celery import celery_executor

from plantit.jobs.resources import test_ssh_client_resource
from plantit.jobs.solids import not_much, upload_workflow, setup_workflow, run_workflow, download_results, cleanup


@pipeline(mode_defs=[
    ModeDefinition(
        name='default',
        executor_defs=default_executors + [celery_executor],
    )
])
def parallel_pipeline():
    for i in range(50):
        not_much.alias('not_much_' + str(i))()


@pipeline(mode_defs=[
    ModeDefinition(
        name='test',
        resource_defs={'ssh_client': test_ssh_client_resource},
        executor_defs=default_executors + [celery_executor]
    )
])
def workflow():
    upload_workflow()
    setup_workflow()
    run_workflow()
    download_results()
    cleanup()
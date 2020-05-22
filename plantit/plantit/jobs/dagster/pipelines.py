from plantit.jobs.dagster.solids import *

from dagster import ModeDefinition, default_executors, pipeline
from dagster_celery import celery_executor

@pipeline(mode_defs=[ModeDefinition(executor_defs=default_executors + [celery_executor])])
def workflow():
    execute_workflow(upload_workflow(create_directory()))

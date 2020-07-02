from plantit.jobs.dagster.solids import *

from dagster import ModeDefinition, default_executors, pipeline
from dagster_celery import celery_executor


@pipeline(mode_defs=[ModeDefinition(executor_defs=default_executors + [celery_executor])])
def plantit_pipeline():
    execute_command.alias('create_working_directory')()
    execute_command()

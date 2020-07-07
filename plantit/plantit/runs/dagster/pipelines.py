from plantit.runs.dagster.resources import ssh_resource
from plantit.runs.dagster.solids import *

from dagster import ModeDefinition, default_executors, pipeline
from dagster_celery import celery_executor


@pipeline(mode_defs=[ModeDefinition(executor_defs=default_executors + [celery_executor], resource_defs={'ssh': ssh_resource})])
def plantit_pipeline():
    execute_command.alias('create_working_directory')()
    upload_pipeline()
    execute_command()

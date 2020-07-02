from dagster import DagsterType, Selector, input_hydration_config, Field, String, Int, Shape, Dict, Permissive

from plantit.jobs.models.abstract_status import AbstractStatus
from plantit.jobs.models.abstract_cluster import AbstractCluster
from plantit.jobs.models.abstract_job import AbstractJob

DagsterStatus = DagsterType(
    name='Status',
    type_check_fn=lambda _, value: isinstance(value, AbstractStatus),
    description='Workflow submission status'
)


@input_hydration_config(Permissive({
    'workdir': Field(String),
    'username': Field(String),
    'port': Field(String),
    'hostname': Field(String),
    'submit_commands': Field(String)}
))
def cluster_input_hydration_config(_, selector) -> AbstractCluster:
    cluster = AbstractCluster()
    cluster.workdir = selector['workdir']
    cluster.username = selector['username']
    if 'password' in selector:
        cluster.password = selector['password']
    cluster.port = selector['port']
    cluster.hostname = selector['hostname']
    cluster.submit_commands = selector['submit_commands']
    return cluster


DagsterCluster = DagsterType(
    name='Cluster',
    type_check_fn=lambda _, value: isinstance(value, AbstractCluster),
    description='Compute cluster',
    input_hydration_config=cluster_input_hydration_config
)


@input_hydration_config(Permissive({
    'workflow': Field(String),
    'cluster': Field(String),
    'work_dir': Field(String),
}))
def job_input_hydration_config(_, selector) -> AbstractJob:
    job = AbstractJob()
    job.workflow = selector['workflow']
    job.cluster = selector['cluster']
    job.work_dir = selector['work_dir']
    return job


DagsterJob = DagsterType(
    name='Job',
    type_check_fn=lambda _, value: isinstance(value, AbstractJob),
    description='Job definition',
    input_hydration_config=job_input_hydration_config
)

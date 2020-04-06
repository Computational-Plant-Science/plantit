from dagster import RepositoryDefinition

from .pipelines import parallel_pipeline, workflow


def define_repo():
    return RepositoryDefinition(
        name='jobs', pipeline_defs=[parallel_pipeline, workflow]
    )

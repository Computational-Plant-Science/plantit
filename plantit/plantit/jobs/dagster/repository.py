from dagster import RepositoryDefinition

from .pipelines import *


def define_repo():
    return RepositoryDefinition(
        name='jobs', pipeline_defs=[workflow]
    )

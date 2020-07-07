from dagster import RepositoryDefinition, repository

from .pipelines import *


@repository
def plantit_repository():
    return [plantit_pipeline]

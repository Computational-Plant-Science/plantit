from dagster import RepositoryDefinition

from .pipelines import *

import django
django.setup()


def define_repo():
    return RepositoryDefinition(
        name='jobs', pipeline_defs=[workflow]
    )

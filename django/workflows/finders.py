import os
from django.apps import apps
from django.core.files.storage import (
    FileSystemStorage, Storage, default_storage,
)
from django.contrib.staticfiles.finders import AppDirectoriesFinder, searched_locations
from django.contrib.staticfiles import utils

class WorkflowDirectoriesFinder(AppDirectoriesFinder):
    """
    A static files finder that looks in the directory of each app as
    specified in the source_dir attribute.
    """
    source_dir = 'django/static'

from django.db import models
from django.core import serializers

from model_utils.managers import InheritanceManager

from collection.models import Sample
from job_manager.job import Job
from job_manager.remote import SubmissionTask, UploadCollectionTask, UploadFileTask

"""
    A workflow consists of a collection of files, details about the files
    (metadata), and a collection of tasks that are run to analze the files.
    Typically, the tasks are the same across all collections in the same
    workflow.

    Modules inside :module:`workflows.models` that are specific to each workflow
    are prefixed with "Abstract", indicating they need to be extended
    independentially by each workflow.

    See :module:`workflows.dirt2d.models` for a working example
"""

#
# This class was created to save results to the database. When this became
# more complicated, saving the results to a file (saved in the Job class)
# was utilized instead. I left the class here so that I can come back to
# saving results in the database at a later date
#
# class Result(models.Model):
#     """
#         Represents the results from one sample
#     """
#     objects = InheritanceManager()
#     job = models.ForeignKey(Job, on_delete=models.CASCADE)
#     sample = models.ForeignKey(Sample, on_delete=models.CASCADE)
#
#     attributes = {}
#
#     def serialize(self):
#         result = {}
#
#         result = serializers.serialize('python',
#             [self, ],
#             fields = self.attributes.keys() )[0]
#
#         result['name'] = self.sample.name
#
#         return result
#
#     def __str__(self):
#         return "Result(sample=%s,job=%s)"%(self.sample,self.job)

class Tag(models.Model):
    """
        All tags are available to all workflows and should be used to broadly
        describe the contents of a workflow collection, allowing it to be easily
        found via a site-wide search. For example, a workflow collection that
        is related to maze would get a "maze" tag, allowing it to show up
        when users are looking for analysis realted to maze.

        Tags should not be exteded by individual workflows.

        Attributes:
            tag (str): tag
            description (str): tag description
    """
    tag = models.CharField(max_length=50)
    description = models.CharField(max_length=250)

class WorkFlows():
    registry = {}

    def register(self,workflow,types):
        registry[workflow]

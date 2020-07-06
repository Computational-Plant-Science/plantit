import json
import os

import binascii

from django.conf import settings
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone

from plantit.collection.models import Collection
from plantit.jobs.models.abstract_job import AbstractJob
from plantit.jobs.models.cluster import Cluster


class Job(models.Model, AbstractJob):
    class Meta:
        ordering = ['-created']

    collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now())
    token = models.CharField(max_length=40, default=binascii.hexlify(os.urandom(20)).decode())
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    submission_id = models.CharField(max_length=100, null=True, blank=True)
    pipeline_owner = models.CharField(max_length=280, null=True, blank=True)
    pipeline_name = models.CharField(max_length=280, null=True, blank=True)
    cluster = models.ForeignKey(Cluster,
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL)
    work_dir = models.CharField(max_length=100,
                                null=True,
                                blank=True,
                                default=timezone.now().strftime('%s') + "/")
    remote_results_path = models.CharField(max_length=100,
                                           null=True,
                                           blank=True,
                                           default=None)
    parameters = models.TextField(blank=True, null=True)

    def __str__(self):
        return json.dumps(model_to_dict(self))

    def current_status(self):
        """
            The job's most recent status.

            Returns:
                the most recent status of the job as a :class:`Status` object.
        """
        try:
            return self.status_set.filter(date__isnull=False).latest('date')
        except:
            return None


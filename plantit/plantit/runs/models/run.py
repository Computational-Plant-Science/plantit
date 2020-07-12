import binascii
import json
import os
import uuid

from django.conf import settings
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone

from plantit.runs.models.cluster import Cluster


class Run(models.Model):
    class Meta:
        ordering = ['-created']

    # collection = models.ForeignKey(Collection, on_delete=models.CASCADE)
    created = models.DateTimeField(default=timezone.now())
    token = models.CharField(max_length=40, default=binascii.hexlify(os.urandom(20)).decode())
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=36, null=False, blank=False, default=uuid.uuid4())
    workflow_owner = models.CharField(max_length=280, null=True, blank=True)
    workflow_name = models.CharField(max_length=280, null=True, blank=True)
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

    def __str__(self):
        return json.dumps(model_to_dict(self))

    @property
    def plantit_status(self):
        try:
            return self.plantitstatus_set.filter(date__isnull=False).latest('date')
        except:
            return None

    @property
    def target_status(self):
        try:
            return self.targetstatus_set.filter(date__isnull=False).latest('date')
        except:
            return None

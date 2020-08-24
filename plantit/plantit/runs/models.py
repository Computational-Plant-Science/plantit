import json

from django.conf import settings
from django.db import models
from django.forms import model_to_dict
from django.utils import timezone

from plantit.targets.models import Target


class Run(models.Model):
    class Meta:
        ordering = ['-created']

    created = models.DateTimeField(default=timezone.now())
    token = models.CharField(max_length=40)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    identifier = models.CharField(max_length=36, null=False, blank=False)
    workflow_owner = models.CharField(max_length=280, null=True, blank=True)
    workflow_name = models.CharField(max_length=280, null=True, blank=True)
    cluster = models.ForeignKey(Target,
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
    def status(self):
        try:
            return self.status_set.filter(date__isnull=False).latest('date')
        except:
            return None


class Status(models.Model):
    class Meta:
        ordering = ['-date']

    COMPLETED = 1
    FAILED = 2
    RUNNING = 3
    CREATED = 4

    State = (
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (RUNNING, 'Running'),
        (CREATED, 'Created')
    )

    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    state = models.PositiveIntegerField(choices=State, default=CREATED)
    location = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now, blank=True)
    description = models.TextField(blank=True)


    def __str__(self):
        return self.State[self.state - 1][1]
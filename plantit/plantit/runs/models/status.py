from django.db import models
from django.utils import timezone

from plantit.runs.models.run import Run


class TargetStatus(models.Model):
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
    date = models.DateTimeField(default=timezone.now, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.State[self.state - 1][1]


class PlantitStatus(models.Model):
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
    date = models.DateTimeField(default=timezone.now, blank=True)
    description = models.TextField(blank=True)


    def __str__(self):
        return self.State[self.state - 1][1]

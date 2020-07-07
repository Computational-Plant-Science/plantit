from django.db import models
from django.utils import timezone

from plantit.runs.models.abstractstatus import AbstractStatus
from plantit.runs.models.run import Run


class Status(models.Model, AbstractStatus):
    """
        Job status object.

        **Possible Status States:**

        - :attr:`Status.COMPLETED` (int): Job is completed
        - :attr:`Status.FAILED` (int): Job failed
        - :attr:`Status.OK` (int): Status update, everything is OK
        - :attr:`Status.WARN` (int): Status update, warning: recoverable error
        - :attr:`Status.CREATED` (int): Job was crated but not yet started

        Attributes:
            job (ForeinKey): The job that this status is liked to
            state (int): The state of this status. Must be one of
                the "Possible Status States" listed above.
            date (DateTime): The time the status was added to the job
            description (str): A string description of why this status
                was added to the job
    """

    class Meta:
        ordering = ['-date']

    COMPLETED = 1
    FAILED = 2
    OK = 3
    WARN = 4
    CREATED = 5

    State = (
        (COMPLETED, 'Completed'),
        (FAILED, 'Failed'),
        (OK, 'OK'),
        (WARN, 'Warning'),
        (CREATED, 'Created')
    )

    job = models.ForeignKey(Run, on_delete=models.CASCADE)
    state = models.PositiveIntegerField(choices=State, default=CREATED)
    date = models.DateTimeField(default=timezone.now, blank=True)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return self.State[self.state - 1][1]
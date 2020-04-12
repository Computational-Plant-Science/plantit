'''
    Plant IT celery configuration. Provides a
    `celery task queue <http://www.celeryproject.org>`_ for running
    jobs asynchronously of the web server. Used extensively by
    :mod:`plantit.job_manager`.

    Celery is run in the celery docker container.

    Attention:
        The celery container must be restarted to load any code changes.
'''

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plantit.settings')

app = Celery('plantit',
             broker='amqp://rabbitmq',
             backend='amqp://rabbitmq')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

import os

import eventlet

# patch standard libraries to play nice with eventlet non-blocking concurrency
#   https://stackoverflow.com/a/28332804/6514033
#   https://stackoverflow.com/a/32374184/6514033
eventlet.monkey_patch()

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plantit.settings')
app = Celery('plantit', broker='redis://redis', backend='redis://redis')

app.config_from_object('django.conf:settings', namespace='CELERY')

# load task modules from all registered Django app configs
app.autodiscover_tasks()

# route IO-bound tasks to the eventlet worker
app.conf.task_routes = {
    'plantit.celery_tasks.transfer*': {'queue': 'eventlet'},
    'plantit.celery_tasks.refresh*': {'queue': 'eventlet'},
    'plantit.celery_tasks.find*': {'queue': 'eventlet'}
}

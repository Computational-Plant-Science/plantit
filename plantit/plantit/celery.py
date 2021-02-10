import json
import os
from os import environ
from datetime import timedelta, datetime

from celery import Celery, shared_task

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'plantit.settings')

app = Celery(
    'plantit',
    broker='amqp://rabbitmq',
    backend=f"db+postgresql://{environ.get('SQL_USER')}:{environ.get('SQL_PASSWORD')}@{environ.get('SQL_HOST')}")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

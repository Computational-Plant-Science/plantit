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


# @shared_task()
# def remove_old_runs():
#     epoch = datetime.fromordinal(0)
#     threshold = datetime.now() - timedelta(days=30)
#     epoch_ts = f"{epoch.year}-{epoch.month}-{epoch.day}"
#     threshold_ts = f"{threshold.year}-{threshold.month}-{threshold.day}"
#     print(f"Removing runs created before {threshold.strftime('%d/%m/%Y %H:%M:%S')}")
#     Run.objects.filter(date__range=[epoch_ts, threshold_ts]).delete()
#
#
# @shared_task()
# def crawl_github_repos():
#     flows = []
#     users = User.objects.all()
#     usernames = [user.profile.github_username for user in users] + [
#         'Computational-Plant-Science',
#         'van-der-knaap-lab',
#         'burke-lab']
#     for username in usernames:
#         flows = flows + __list_by_user(username)
#
#     flows_file = settings.FLOWS_CACHE
#     with open(flows_file, 'w') as file:
#         json.dump(flows, file)


# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

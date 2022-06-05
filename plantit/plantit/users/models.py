from django.contrib.auth.models import User
from django.db import models

from plantit.agents.models import Agent


class Profile(models.Model):
    user: User = models.OneToOneField(User, on_delete=models.CASCADE)
    github_username: str = models.CharField(max_length=255, blank=True, default='')
    github_token: str = models.CharField(max_length=500, blank=True, default='')
    cyverse_access_token: str = models.TextField(blank=True, default='')
    cyverse_refresh_token: str = models.TextField(blank=True, default='')
    institution = models.CharField(max_length=255, blank=True, default='')
    dark_mode: bool = models.BooleanField(default=False)
    interactive_mode = models.ForeignKey(Agent, null=True, blank=True, on_delete=models.PROTECT)
    push_notification_status = models.CharField(max_length=10, null=False, blank=False, default='disabled')
    push_notification_topic_arn = models.CharField(max_length=255, null=True, blank=True)
    push_notification_sub_arn = models.CharField(max_length=255, null=True, blank=True)
    hints = models.BooleanField(default=False)
    created = models.DateField(null=True, blank=True)
    first_login = models.BooleanField(default=True)
    dirt_email = models.CharField(max_length=255, null=True, blank=True)
    dirt_name = models.CharField(max_length=255, null=True, blank=True)


class Migration(models.Model):
    profile: Profile = models.OneToOneField(Profile, on_delete=models.CASCADE)
    started = models.DateTimeField(null=True, blank=True)
    completed = models.DateTimeField(null=True, blank=True)
    target_path = models.CharField(max_length=255, null=True, blank=True)
    num_files = models.IntegerField(null=True, blank=True)
    num_metadata = models.IntegerField(null=True, blank=True)
    num_outputs = models.IntegerField(null=True, blank=True)
    num_logs = models.IntegerField(null=True, blank=True)
    uploads = models.JSONField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    outputs = models.JSONField(null=True, blank=True)
    logs = models.JSONField(null=True, blank=True)

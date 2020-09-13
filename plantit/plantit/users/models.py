from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user: User = models.OneToOneField(User, on_delete=models.CASCADE)
    github_username: str = models.CharField(max_length=255, blank=True, default='')
    github_token: str = models.CharField(max_length=255, blank=True, default='')
    cyverse_token: str = models.CharField(max_length=255, blank=True, default='')

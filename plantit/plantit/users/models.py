from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user: User = models.OneToOneField(User, on_delete=models.CASCADE)
    cyverse_token: str = models.CharField(max_length=255, blank=True),
    github_token: str = models.CharField(max_length=255, blank=True),
    github_username: str = models.CharField(max_length=255, blank=True)
    orcid_id: str = models.CharField(max_length=20, default='', blank=True)
    country: str = models.CharField(max_length=255, default='', blank=True)
    continent: str = models.CharField(max_length=255, default=None, blank=True)
    institution: str = models.CharField(max_length=255, default='', blank=True)
    field_of_study: str = models.CharField(max_length=255, default='', blank=True)


class Role(models.Model):
    user: User = models.ManyToManyField(User, on_delete=models.CASCADE)
    description: str = models.CharField(max_length=255, blank=True)

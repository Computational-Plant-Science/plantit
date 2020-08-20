from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user: User = models.OneToOneField(User, on_delete=models.CASCADE)
    github_username: str = models.CharField(max_length=100, default='', blank=True, null=True)
    country: str = models.CharField(max_length=256, default='', blank=True)
    continent: str = models.CharField(max_length=256, default=None, blank=True, null=True)
    institution: str = models.CharField(max_length=256, default='', blank=True)
    field_of_study: str = models.CharField(max_length=256, default='', blank=True)


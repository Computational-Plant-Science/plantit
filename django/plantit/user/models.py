from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from plantit.job_manager.job import Job
from plantit.collection.models import Collection

# Create your models here.
class Profile(models.Model):
    # See https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=30, blank=True)
    affiliation = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50)
    pinned_jobs = models.ManyToManyField(Job, related_name='profile_pins')
    pinned_collections = models.ManyToManyField(Collection, related_name='profile_pins')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

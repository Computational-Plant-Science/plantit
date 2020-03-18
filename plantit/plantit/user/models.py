from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from plantit.job_manager.job import Job
from plantit.collection.models import Collection

# Create your models here.
class Profile(models.Model):
    """
        Extends the base :class:`django.contrib.auth.models.User` to
        include a user Profile.

        Attributes:
            user (:class:`~django.contrib.auth.models.User`): The user
                this profile belongs
            city (str): The city the user is located
            affiliation (str): The user's institution or company affiliation.
            country (str): The user's country
            pinned_jobs (ManyToManyField): The jobs the user has pinned
                in the front end user interface
            pinned_collections (ManyToManyField): The collections the user has
                pinned in the front end user interface.
    """
    # See https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    city = models.CharField(max_length=30, blank=True)
    affiliation = models.CharField(max_length=50, blank=True)
    country = models.CharField(max_length=50, blank=True)
    pinned_jobs = models.ManyToManyField(Job, related_name='profile_pins', blank=True)
    pinned_collections = models.ManyToManyField(Collection, related_name='profile_pins', blank=True)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
        Post-Create hook for django User objects that creates a repective
        profile object for the user.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
        Post-Save hook for django User objects that updates the respective
        profile object when the user object is saved.
    """
    instance.profile.save()

from django.db import models

from django.contrib.auth.models import User
from django.db.models import Manager
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
            user (:class:`~django.contrib.auth.models.User`): The user this profile belongs to.
            affiliated_institution (str): The user's institution or company.
            affiliated_institution_type (str): The user's institution type.
            country (str): The user's institution's host country.
            continent(str): The user's institution's continent.
            field_of_study(str): The user's field of study.
            pinned_jobs (ManyToManyField): The user's pinned jobs.
            pinned_collections (ManyToManyField): The user's pinned collections.
    """
    # See https://simpleisbetterthancomplex.com/tutorial/2016/07/22/how-to-extend-django-user-model.html#onetoone
    user: User = models.OneToOneField(User, on_delete=models.CASCADE)
    country: str = models.CharField(max_length=256, blank=False)
    continent: str = models.CharField(max_length=256, blank=False)
    institution: str = models.CharField(max_length=256, blank=False)
    institution_type: str = models.CharField(max_length=256, blank=False)
    field_of_study: str = models.CharField(max_length=256, blank=False)
    pinned_jobs: Manager = models.ManyToManyField(Job, related_name='profile_pins', blank=True)
    pinned_collections: Manager = models.ManyToManyField(Collection, related_name='profile_pins', blank=True)

    def asdict(self):
        return {
            'country': self.country,
            'continent': self.continent,
            'institution': self.institution,
            'institution_type': self.institution_type,
            'field_of_study': self.field_of_study
        }

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

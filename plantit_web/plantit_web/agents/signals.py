from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from plantit_web.agents.models import Agent


@receiver(post_save, sender=Agent)
def update_on_save(sender, instance, created, **kwargs):
    # TODO schedule any default agent tasks
    pass


@receiver(post_delete, sender=Agent)
def update_on_delete(sender, instance, **kwargs):
    # TODO unschedule all agent tasks
    pass
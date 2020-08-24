from django.apps.config import AppConfig


class PlantITConfig(AppConfig):
    name = 'plantit'

    def ready(self):
        from django_cas_ng.signals import cas_user_authenticated, cas_user_logout
        from .signals import cas_user_authenticated_callback, cas_user_logout_callback
        cas_user_authenticated.connect(cas_user_authenticated_callback)
        cas_user_logout.connect(cas_user_logout_callback)

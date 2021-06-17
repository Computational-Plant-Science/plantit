from rest_framework import authentication
from rest_framework import exceptions

from plantit.tasks.models import Task


class TaskTokenAuthentication(authentication.TokenAuthentication):
    keyword = 'Token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        return Task

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            task = model.objects.get(token=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        return task.user, task

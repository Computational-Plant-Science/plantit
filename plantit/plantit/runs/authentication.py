from rest_framework import authentication
from rest_framework import exceptions

from plantit.runs.models import Run


class RunTokenAuthentication(authentication.TokenAuthentication):
    keyword = 'Token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        return Run

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            run = model.objects.get(token=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        return run.user, run

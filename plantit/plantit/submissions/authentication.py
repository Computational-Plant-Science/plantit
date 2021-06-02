from rest_framework import authentication
from rest_framework import exceptions

from plantit.submissions.models import Submission


class SubmissionTokenAuthentication(authentication.TokenAuthentication):
    keyword = 'Token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        return Submission

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            sub = model.objects.get(token=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        return sub.user, sub

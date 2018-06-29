from job_manager.models import Job
from rest_framework import authentication
from rest_framework import exceptions
from rest_framework import authentication

class JobTokenAuthentication(authentication.TokenAuthentication):
    """
    Extends the token system provided by the django rest framework to
    authenicate against tokens saved in the job model. This allows tokens
    to be issued per job instead of per user.
     
    Clients should authenticate by passing the token key in the "Authorization"
    HTTP header, prepended with the string "Token ".  For example:
        Authorization: Token 401f7ac837da42b97f613d789819ff93537bee6a
    """

    keyword = 'Token'
    model = None

    def get_model(self):
        if self.model is not None:
            return self.model
        from rest_framework.authtoken.models import Token
        return Job

    def authenticate_credentials(self, key):
        model = self.get_model()
        try:
            job = model.objects.get(auth_token=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        return (job.user, job)

'''
    Production ready settings for the app. Note that many for the settings below
    need to be set manually for security reasons.

    It is best to create the django/settings.py file and set the required
    variables there. django/settings.py is not tracked by Git. 
'''
from plantit.settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = None

FIELD_ENCRYPTION_KEY = None

#Sets the url to access the PlantIT api from
# Eg: API_URL = http://www.plantit.com/djangoapp/apis/v1/""
API_URL = None

ALLOWED_HOSTS = ['*']

try:
    #Try to import a settings.py file at django/settings.py
    # django/settings.py is ignored by git. It is recommended you add any
    # settings you want to change there.
    #
    # API_URL, SECRET_KEY, INSTALLED_APPS, etc. can all be set in settings.py
    # For INSTALLED_APPS, use list concatenation:
    #                   INSTALLED_APPS += ['another.app']
    import settings.py
except:
    pass

assert SECRET_KEY is not None, "SECRET_KEY must be set"
assert FIELD_ENCRYPTION_KEY is not None, "FIELD_ENCRYPTION_KEY must be set"
assert API_URL is not None, "API_URL must be set"

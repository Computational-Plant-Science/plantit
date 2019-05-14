'''
    Provides some defaults to get a test server up and running. Almost every
    setting in here should not be used in production.

    Run django with settings_prod.py configuration for production.
'''
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e#n-lzvcua1^+-0s^**@0_3*ecrpi0jp=5czckrt!i=q76_ue)'

FIELD_ENCRYPTION_KEY = b'mm8zveo6FRrzVuJ2I_M_LorHdL4lJwDByS5kPWBYaM8='

ALLOWED_HOSTS = ['*']

#Sets the url to access the PlantIT api from
API_URL = "http://djangoapp/apis/v1/"

try:
    #Try to import a settings.py file at django/settings.py
    # django/settings.py is ignored by git. It is recommended you add any
    # settings you want to change there.
    #
    # API_URL, SECRET_KEY, INSTALLED_APPS, etc. can all be set in settings.py
    # For INSTALLED_APPS, use list concatenation:
    #                   INSTALLED_APPS += ['another.app']
    from settings import *
    from plantit.settings import *
except ImportError:
    from plantit.settings import *

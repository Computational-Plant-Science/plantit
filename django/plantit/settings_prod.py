from plantit.settings import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = None

FIELD_ENCRYPTION_KEY = None

#Sets the url to access the PlantIT api from
# Eg: API_URL = http://www.plantit.com/djangoapp/apis/v1/""
API_URL = None

ALLOWED_HOSTS = ['*']

assert SECRET_KEY is not None, "SECRET_KEY must be set"
assert FIELD_ENCRYPTION_KEY is not None, "FIELD_ENCRYPTION_KEY must be set"
assert API_URL is not None, "API_URL must be set"

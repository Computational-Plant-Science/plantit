from plantit.settings import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'e#n-lzvcua1^+-0s^**@0_3*ecrpi0jp=5czckrt!i=q76_ue)'

FIELD_ENCRYPTION_KEY = b'mm8zveo6FRrzVuJ2I_M_LorHdL4lJwDByS5kPWBYaM8='

ALLOWED_HOSTS = ['*']

#Sets the url to access the PlantIT api from
API_URL = "http://djangoapp/apis/v1/"

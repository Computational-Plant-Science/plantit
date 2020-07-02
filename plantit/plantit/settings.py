import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NO_ENV_VAR = 'Environment variable not configured'

assert 'DJANGO_SECRET_KEY' in os.environ, '{NO_ENV_VAR}: DJANGO_SECRET_KEY'
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

assert 'DJANGO_DEBUG' in os.environ, '{NO_ENV_VAR}: DJANGO_DEBUG'
DEBUG = os.environ.get('DJANGO_DEBUG')

assert 'DJANGO_FIELD_ENCRYPTION_KEY' in os.environ, '{NO_ENV_VAR}: DJANGO_FIELD_ENCRYPTION_KEY'
FIELD_ENCRYPTION_KEY = os.environ.get('DJANGO_FIELD_ENCRYPTION_KEY')

assert 'DJANGO_ALLOWED_HOSTS' in os.environ, '{NO_ENV_VAR}: DJANGO_ALLOWED_HOSTS'
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(',')

assert 'DJANGO_API_URL' in os.environ, '{NO_ENV_VAR}: DJANGO_API_URL'
API_URL = os.environ.get('DJANGO_API_URL')

assert 'GITHUB_AUTH_URI' in os.environ, '{NO_ENV_VAR}: GITHUB_AUTH_URI'
GITHUB_AUTH_URI = os.environ.get('GITHUB_AUTH_URI')

assert 'GITHUB_REDIRECT_URI' in os.environ, '{NO_ENV_VAR}: GITHUB_REDIRECT_URI'
GITHUB_REDIRECT_URI = os.environ.get('GITHUB_REDIRECT_URI')

assert 'GITHUB_KEY' in os.environ, '{NO_ENV_VAR}: GITHUB_KEY'
GITHUB_KEY = os.environ.get('GITHUB_KEY')

assert 'GITHUB_SECRET' in os.environ, '{NO_ENV_VAR}: GITHUB_SECRET'
GITHUB_SECRET = os.environ.get('GITHUB_SECRET')

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "/assets/"
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "front_end", "dist", "assets"),
)

#Where Plant IT workflows are kept
WORKFLOW_DIR = os.path.join(BASE_DIR,"workflows")

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #'workflows.finders.WorkflowDirectoriesFinder'
]

MEDIA_URL = "/public/"
MEDIA_ROOT = os.path.join(BASE_DIR, "files", "public")

# Application workflow
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'encrypted_model_fields',
    'plantit.apps.PlantITConfig',
    'front_end.apps.FrontEndConfig',
    'django_cas_ng',
    'taggit'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_cas_ng.middleware.CASMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
)

CAS_SERVER_URL = "https://auth.iplantcollaborative.org/cas4/"
# CAS_SERVER_URL = "https://auth.cyverse.org/cas5/login"
CAS_APPLY_ATTRIBUTES_TO_USER=True
# CAS_VERSION = '3'

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'front_end', 'dist'),
            os.path.join(BASE_DIR, 'templates') #<- This is temporary until cyverse login is implemented
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'plantit.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('SQL_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('SQL_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
        'USER': os.environ.get('SQL_USER', 'user'),
        'PASSWORD': os.environ.get('SQL_PASSWORD', 'password'),
        'HOST': os.environ.get('SQL_HOST', 'localhost'),
        'PORT': os.environ.get('SQL_PORT', '5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/New_York'

USE_I18N = True

USE_L10N = True

USE_TZ = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
    )
}

TAGGIT_CASE_INSENSITIVE = True


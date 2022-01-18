import os

missing_variable = 'Environment variable not configured'

assert 'MAPBOX_TOKEN' in os.environ, f"{missing_variable}: MAPBOX_TOKEN"
assert 'MAPBOX_FEATURE_REFRESH_MINUTES' in os.environ, f"{missing_variable}: MAPBOX_FEATURE_REFRESH_MINUTES"
assert 'DJANGO_SECRET_KEY' in os.environ, f"{missing_variable}: DJANGO_SECRET_KEY"
assert 'DJANGO_DEBUG' in os.environ, f"{missing_variable}: DJANGO_DEBUG"
assert 'DJANGO_ALLOWED_HOSTS' in os.environ, f"{missing_variable}: DJANGO_ALLOWED_HOSTS"
assert 'DJANGO_SECURE_SSL_REDIRECT' in os.environ, f"{missing_variable}: DJANGO_SECURE_SSL_REDIRECT"
assert 'DJANGO_SESSION_COOKIE_SECURE' in os.environ, f"{missing_variable}: DJANGO_SESSION_COOKIE_SECURE"
assert 'DJANGO_CSRF_COOKIE_SECURE' in os.environ, f"{missing_variable}: DJANGO_CSRF_COOKIE_SECURE"
assert 'USERS_CACHE' in os.environ, f"{missing_variable}: USERS_CACHE"
assert 'USERS_REFRESH_MINUTES' in os.environ, f"{missing_variable}: USERS_REFRESH_MINUTES"
assert 'USERS_STATS_REFRESH_MINUTES' in os.environ, f"{missing_variable}: USERS_STATS_REFRESH_MINUTES"
assert 'MORE_USERS' in os.environ, f"{missing_variable}: MORE_USERS"
assert 'AGENT_KEYS' in os.environ, f"{missing_variable}: AGENT_KEYS"
assert 'WORKFLOWS_CACHE' in os.environ, f"{missing_variable}: WORKFLOWS_CACHE"
assert 'WORKFLOWS_REFRESH_MINUTES' in os.environ, f"{missing_variable}: WORKFLOWS_REFRESH_MINUTES"
assert 'TASKS_TIMEOUT_MULTIPLIER' in os.environ, f"{missing_variable}: TASKS_TIMEOUT_MULTIPLIER"
assert 'TASKS_REFRESH_SECONDS' in os.environ, f"{missing_variable}: TASKS_REFRESH_SECONDS"
assert 'TASKS_CLEANUP_MINUTES' in os.environ, f"{missing_variable}: TASKS_CLEANUP_MINUTES"
assert 'TASKS_STEP_TIME_LIMIT_SECONDS' in os.environ, f"{missing_variable}: TASKS_STEP_TIME_LIMIT_SECONDS"
assert 'LAUNCHER_SCRIPT_NAME' in os.environ, f"{missing_variable}: LAUNCHER_SCRIPT_NAME"
assert 'DJANGO_API_URL' in os.environ, f"{missing_variable}: DJANGO_API_URL"
assert 'CYVERSE_REDIRECT_URL' in os.environ, f"{missing_variable}: CYVERSE_REDIRECT_URL"
assert 'CYVERSE_CLIENT_ID' in os.environ, f"{missing_variable}: CYVERSE_CLIENT_ID"
assert 'CYVERSE_CLIENT_SECRET' in os.environ, f"{missing_variable}: CYVERSE_CLIENT_SECRET"
assert 'CYVERSE_TOKEN_REFRESH_MINUTES' in os.environ, f"{missing_variable}: CYVERSE_TOKEN_REFRESH_MINUTES"
assert 'GITHUB_AUTH_URI' in os.environ, f"{missing_variable}: GITHUB_AUTH_URI"
assert 'GITHUB_REDIRECT_URI' in os.environ, f"{missing_variable}: GITHUB_REDIRECT_URI"
assert 'GITHUB_CLIENT_ID' in os.environ, f"{missing_variable}: GITHUB_CLIENT_ID"
assert 'GITHUB_SECRET' in os.environ, f"{missing_variable}: GITHUB_SECRET"
assert 'GITHUB_TOKEN' in os.environ, f"{missing_variable}: GITHUB_TOKEN"
assert 'NO_PREVIEW_THUMBNAIL' in os.environ, f"{missing_variable}: NO_PREVIEW_THUMBNAIL"
assert 'AWS_FEEDBACK_ARN' in os.environ, f"{missing_variable} AWS_FEEDBACK_ARN"
assert 'TUTORIALS_FILE' in os.environ, f"{missing_variable} TUTORIALS_FILE"
assert 'FEEDBACK_FILE' in os.environ, f"{missing_variable} FEEDBACK_FILE"
assert 'AGENTS_HEALTHCHECKS_MINUTES' in os.environ, f"{missing_variable} AGENTS_HEALTHCHECKS_MINUTES"
assert 'AGENTS_HEALTHCHECKS_SAVED' in os.environ, f"{missing_variable} AGENTS_HEALTHCHECKS_SAVED"
assert 'HTTP_TIMEOUT' in os.environ, f"{missing_variable} HTTP_TIMEOUT"

# global Celery task timeout
CELERYD_TASK_SOFT_TIME_LIMIT = 60

MAPBOX_TOKEN = os.environ.get('MAPBOX_TOKEN')
MAPBOX_FEATURE_REFRESH_MINUTES = os.environ.get('MAPBOX_FEATURE_REFRESH_MINUTES')
CYVERSE_TOKEN_REFRESH_MINUTES = os.environ.get('CYVERSE_TOKEN_REFRESH_MINUTES')
API_URL = os.environ.get('DJANGO_API_URL')
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DJANGO_DEBUG')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS').split(',')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_CACHE = os.environ.get('USERS_CACHE')
USERS_REFRESH_MINUTES = os.environ.get('USERS_REFRESH_MINUTES')
USERS_STATS_REFRESH_MINUTES = os.environ.get('USERS_STATS_REFRESH_MINUTES')
MORE_USERS = os.environ.get('MORE_USERS')
AGENT_KEYS = os.environ.get('AGENT_KEYS')
WORKFLOWS_CACHE = os.environ.get('WORKFLOWS_CACHE')
WORKFLOWS_REFRESH_MINUTES = os.environ.get('WORKFLOWS_REFRESH_MINUTES')
TASKS_TIMEOUT_MULTIPLIER = os.environ.get('TASKS_TIMEOUT_MULTIPLIER')
TASKS_REFRESH_SECONDS = os.environ.get('TASKS_REFRESH_SECONDS')
TASKS_CLEANUP_MINUTES = os.environ.get('TASKS_CLEANUP_MINUTES')
TASKS_STEP_TIME_LIMIT_SECONDS = os.environ.get('TASKS_STEP_TIME_LIMIT_SECONDS')
NO_PREVIEW_THUMBNAIL = os.environ.get('NO_PREVIEW_THUMBNAIL')
LAUNCHER_SCRIPT_NAME = os.environ.get('LAUNCHER_SCRIPT_NAME')
AWS_FEEDBACK_ARN = os.environ.get("AWS_FEEDBACK_ARN")
TUTORIALS_FILE = os.environ.get("TUTORIALS_FILE")
FEEDBACK_FILE = os.environ.get("FEEDBACK_FILE")
AGENTS_HEALTHCHECKS_MINUTES = os.environ.get("AGENTS_HEALTHCHECKS_MINUTES")
AGENTS_HEALTHCHECKS_SAVED = os.environ.get("AGENTS_HEALTHCHECKS_SAVED")
HTTP_TIMEOUT = os.environ.get("HTTP_TIMEOUT")

if not DEBUG:
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT')
    SESSION_COOKIE_SECURE = os.environ.get('DJANGO_SESSION_COOKIE_SECURE')
    CSRF_COOKIE_SECURE = os.environ.get('DJANGO_CSRF_COOKIE_SECURE')

GITHUB_AUTH_URI = os.environ.get('GITHUB_AUTH_URI')
GITHUB_REDIRECT_URI = os.environ.get('GITHUB_REDIRECT_URI')
GITHUB_CLIENT_ID = os.environ.get('GITHUB_CLIENT_ID')
GITHUB_SECRET = os.environ.get('GITHUB_SECRET')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# Celery timezone
timezone = 'US/Eastern'

STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATIC_URL = "assets/"
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "front_end", "dist", "assets"),
    os.path.join(BASE_DIR, "front_end", "static")
)

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

MEDIA_URL = "/public/"
MEDIA_ROOT = os.path.join(BASE_DIR, "files", "public")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'plantit.apps.PlantITConfig',
    'taggit',
    'django_celery_beat',
    'channels',
    'simple_history',
    'cacheops',
    'drf_yasg',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("redis", 6379)]
        }
    }
}

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'front_end', 'dist'),
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

ASGI_APPLICATION = 'plantit.asgi.application'
WSGI_APPLICATION = 'plantit.wsgi.application'

DATABASES = {
    'default': {
        # 'ENGINE': os.environ.get('SQL_ENGINE', 'django.db.backends.sqlite3'),
        # 'NAME': os.environ.get('SQL_NAME', os.path.join(BASE_DIR, 'db.sqlite3')),
        'ENGINE': os.environ.get('SQL_ENGINE', 'django.db.backends.postgresql'),
        'NAME': os.environ.get('SQL_NAME', 'plantit'),
        'USER': os.environ.get('SQL_USER', 'user'),
        'PASSWORD': os.environ.get('SQL_PASSWORD', 'password'),
        'HOST': os.environ.get('SQL_HOST', 'localhost'),
        'PORT': os.environ.get('SQL_PORT', '5432'),
    }
}

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

CACHEOPS_REDIS = {
    'host': 'redis',  # redis-server is on same machine
    'port': 6379,  # default redis port
}

# Alternatively the redis connection can be defined using a URL:
# CACHEOPS_REDIS = "redis://redis:6379/1"

CACHEOPS = {
    # cache User.objects.get() calls and all other plantit model gets for 15 minutes
    'auth.user': {'ops': 'get', 'timeout': 60 * 15},
    'plantit.*': {'ops': 'get', 'timeout': 60 * 15},

    # Enable manual caching on all other models with default timeout of an hour
    # Use Post.objects.cache().get(...)
    #  or Tags.objects.filter(...).order_by(...).cache()
    # to cache particular ORM request.
    # Invalidation is still automatic
    # '*.*': {'ops': (), 'timeout': 60*60},
}

# SWAGGER_SETTINGS = {
#     'SECURITY_DEFINITIONS': {
#         'api_key': {
#             'type': 'apiKey',
#             'in': 'header',
#             'name': 'Authorization'
#         }
#     },
# }

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
assert 'CELERY_EVENTLET_QUEUE' in os.environ, f"{missing_variable}: CELERY_EVENTLET_QUEUE"
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
assert 'TASKS_TEMPLATE_SCRIPT_SLURM' in os.environ, f"{missing_variable}: TASKS_TEMPLATE_SCRIPT_SLURM"
assert 'LAUNCHER_SCRIPT_NAME' in os.environ, f"{missing_variable}: LAUNCHER_SCRIPT_NAME"
assert 'INPUTS_FILE_NAME' in os.environ, f"{missing_variable}: INPUTS_FILE_NAME"
assert 'ICOMMANDS_IMAGE' in os.environ, f"{missing_variable}: ICOMMANDS_IMAGE"
assert 'CURL_IMAGE' in os.environ, f"{missing_variable}: CURL_IMAGE"
assert 'DJANGO_API_URL' in os.environ, f"{missing_variable}: DJANGO_API_URL"
assert 'CYVERSE_REDIRECT_URL' in os.environ, f"{missing_variable}: CYVERSE_REDIRECT_URL"
assert 'CYVERSE_CLIENT_ID' in os.environ, f"{missing_variable}: CYVERSE_CLIENT_ID"
assert 'CYVERSE_REDIRECT_URL' in os.environ, f"{missing_variable}: CYVERSE_REDIRECT_URL"
assert 'CYVERSE_CLIENT_SECRET' in os.environ, f"{missing_variable}: CYVERSE_CLIENT_SECRET"
assert 'CYVERSE_TOKEN_REFRESH_MINUTES' in os.environ, f"{missing_variable}: CYVERSE_TOKEN_REFRESH_MINUTES"
assert 'CYVERSE_USERNAME' in os.environ, f"{missing_variable}: CYVERSE_USERNAME"
assert 'CYVERSE_PASSWORD' in os.environ, f"{missing_variable}: CYVERSE_PASSWORD"
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
assert 'STATS_WINDOW_WIDTH_DAYS' in os.environ, f"{missing_variable} STATS_WINDOW_WIDTH_DAYS"
assert 'DOCKER_USERNAME' in os.environ, f"{missing_variable} DOCKER_USERNAME"
assert 'DOCKER_PASSWORD' in os.environ, f"{missing_variable} DOCKER_PASSWORD"
assert 'DIRT_MIGRATION_DATA_DIR' in os.environ, f"{missing_variable} DIRT_MIGRATION_DATA_DIR"
assert 'DIRT_MIGRATION_STAGING_DIR' in os.environ, f"{missing_variable} DIRT_MIGRATION_STAGING_DIR"
assert 'DIRT_MIGRATION_HOST' in os.environ, f"{missing_variable} DIRT_MIGRATION_HOST"
assert 'DIRT_MIGRATION_PORT' in os.environ, f"{missing_variable} DIRT_MIGRATION_PORT"
assert 'DIRT_MIGRATION_USERNAME' in os.environ, f"{missing_variable} DIRT_MIGRATION_USERNAME"
# assert 'DIRT_MIGRATION_DB_CONN_STR' in os.environ, f"{missing_variable} DIRT_MIGRATION_DB_CONN_STR"
assert 'DIRT_MIGRATION_DB_HOST' in os.environ, f"{missing_variable} DIRT_MIGRATION_DB_HOST"
assert 'DIRT_MIGRATION_DB_PORT' in os.environ, f"{missing_variable} DIRT_MIGRATION_DB_PORT"
assert 'DIRT_MIGRATION_DB_USER' in os.environ, f"{missing_variable} DIRT_MIGRATION_DB_USER"
assert 'DIRT_MIGRATION_DB_PASSWORD' in os.environ, f"{missing_variable} DIRT_MIGRATION_DB_PASSWORD"
assert 'DIRT_MIGRATION_DB_DATABASE' in os.environ, f"{missing_variable} DIRT_MIGRATION_DB_DATABASE"


CELERYD_TASK_SOFT_TIME_LIMIT = 60  # global Celery task timeout
CELERY_EVENTLET_QUEUE = os.environ.get('CELERY_EVENTLET_QUEUE')
MAPBOX_TOKEN = os.environ.get('MAPBOX_TOKEN')
MAPBOX_FEATURE_REFRESH_MINUTES = os.environ.get('MAPBOX_FEATURE_REFRESH_MINUTES')
CYVERSE_TOKEN_REFRESH_MINUTES = os.environ.get('CYVERSE_TOKEN_REFRESH_MINUTES')
CYVERSE_REDIRECT_URL = os.environ.get('CYVERSE_REDIRECT_URL')
CYVERSE_USERNAME = os.environ.get('CYVERSE_USERNAME')
CYVERSE_PASSWORD = os.environ.get('CYVERSE_PASSWORD')
CYVERSE_CLIENT_ID = os.environ.get('CYVERSE_CLIENT_ID')
CYVERSE_CLIENT_SECRET = os.environ.get('CYVERSE_CLIENT_SECRET')
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
TASKS_TEMPLATE_SCRIPT_SLURM = os.environ.get('TASKS_TEMPLATE_SCRIPT_SLURM')
NO_PREVIEW_THUMBNAIL = os.environ.get('NO_PREVIEW_THUMBNAIL')
LAUNCHER_SCRIPT_NAME = os.environ.get('LAUNCHER_SCRIPT_NAME')
INPUTS_FILE_NAME = os.environ.get('INPUTS_FILE_NAME')
ICOMMANDS_IMAGE = os.environ.get('ICOMMANDS_IMAGE')
CURL_IMAGE = os.environ.get('CURL_IMAGE')
AWS_FEEDBACK_ARN = os.environ.get("AWS_FEEDBACK_ARN")
TUTORIALS_FILE = os.environ.get("TUTORIALS_FILE")
FEEDBACK_FILE = os.environ.get("FEEDBACK_FILE")
AGENTS_HEALTHCHECKS_MINUTES = os.environ.get("AGENTS_HEALTHCHECKS_MINUTES")
AGENTS_HEALTHCHECKS_SAVED = os.environ.get("AGENTS_HEALTHCHECKS_SAVED")
HTTP_TIMEOUT = os.environ.get("HTTP_TIMEOUT")
STATS_WINDOW_WIDTH_DAYS = os.environ.get("STATS_WINDOW_WIDTH_DAYS")
DOCKER_USERNAME = os.environ.get("DOCKER_USERNAME")
DOCKER_PASSWORD = os.environ.get("DOCKER_PASSWORD")
DIRT_MIGRATION_STAGING_DIR = os.environ.get("DIRT_MIGRATION_STAGING_DIR")
DIRT_MIGRATION_DATA_DIR = os.environ.get("DIRT_MIGRATION_DATA_DIR")
DIRT_MIGRATION_HOST = os.environ.get("DIRT_MIGRATION_HOST")
DIRT_MIGRATION_PORT = os.environ.get("DIRT_MIGRATION_PORT")
DIRT_MIGRATION_USERNAME = os.environ.get("DIRT_MIGRATION_USERNAME")
# DIRT_MIGRATION_DB_CONN_STR = os.environ.get("DIRT_MIGRATION_DB_CONN_STR")
DIRT_MIGRATION_DB_HOST = os.environ.get("DIRT_MIGRATION_DB_HOST")
DIRT_MIGRATION_DB_PORT = os.environ.get("DIRT_MIGRATION_DB_PORT")
DIRT_MIGRATION_DB_USER = os.environ.get("DIRT_MIGRATION_DB_USER")
DIRT_MIGRATION_DB_PASSWORD = os.environ.get("DIRT_MIGRATION_DB_PASSWORD")
DIRT_MIGRATION_DB_DATABASE = os.environ.get("DIRT_MIGRATION_DB_DATABASE")

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

# modify default logging configuration (https://docs.djangoproject.com/en/4.0/ref/logging/#default-logging-definition) to enable/disable debug logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'formatters': {
        'django.server': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        }
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
        },
        'django.server': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'django.server',
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'plantit': {
            'handlers': ['console', 'mail_admins'],
            'level': 'DEBUG' if DEBUG else 'INFO'
        },
        'django': {
            'handlers': ['console', 'mail_admins'],
            'level': 'INFO',
        },
        'django.server': {
            'handlers': ['django.server'],
            'level': 'INFO',
            'propagate': False,
        },
    }
}

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

CACHES = {
    'default': {
        # TODO reinstate redis once we update to Django 4
        # 'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        # 'LOCATION': 'redis://redis:6379',
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
    }
}

CACHEOPS_REDIS = {
    'host': 'redis',  # redis-server is on same machine
    'port': 6379,  # default redis port
}

CACHEOPS = {
    'plantit.*': {'ops': 'get', 'timeout': 60 * 15},
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

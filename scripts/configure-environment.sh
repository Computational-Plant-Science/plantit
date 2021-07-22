#!/bin/bash

admin_password=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50)))\")")
secret_key=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50)))\")")
sql_password=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50)))\")")
field_encryption_key=$(python2 -c "exec(\"import cryptography.fernet\nprint('%s' % cryptography.fernet.Fernet.generate_key())\")")

if [[ -z "${MAPBOX_TOKEN}" ]]; then
  mapbox_token="some_mapbox_token"
  echo "Warning: MAPBOX_TOKEN environment variable missing"
else
  mapbox_token="${MAPBOX_TOKEN}"
fi

if [[ -z "${SQL_PASSWORD}" ]]; then
  sql_password="some_sql_password"
  echo "Warning: SQL_PASSWORD environment variable missing"
else
  sql_password="${SQL_PASSWORD}"
fi

if [[ -z "${GITHUB_CLIENT_ID}" ]]; then
  github_client_id="some_github_client_id"
  echo "Warning: GITHUB_CLIENT_ID environment variable missing"
else
  github_client_id="${GITHUB_CLIENT_ID}"
fi

if [[ -z "${GITHUB_SECRET}" ]]; then
  github_secret="some_github_secret"
  echo "Warning: GITHUB_SECRET environment variable missing"
else
  github_secret="${GITHUB_SECRET}"
fi

if [[ -z "${CYVERSE_CLIENT_ID}" ]]; then
  cyverse_client_id="some_cyverse_client_id"
  echo "Warning: CYVERSE_CLIENT_ID environment variable missing"
else
  cyverse_client_id="${CYVERSE_CLIENT_ID}"
fi

if [[ -z "${CYVERSE_CLIENT_SECRET}" ]]; then
  cyverse_secret="some_cyverse_secret"
  echo "Warning: CYVERSE_CLIENT_SECRET environment variable missing"
else
  cyverse_secret="${CYVERSE_CLIENT_SECRET}"
fi

if [[ -z "${CYVERSE_USERNAME}" ]]; then
  cyverse_username="some_cyverse_username"
  echo "Warning: CYVERSE_USERNAME environment variable missing"
else
  cyverse_username="${CYVERSE_USERNAME}"
fi

if [[ -z "${CYVERSE_PASSWORD}" ]]; then
  cyverse_password="some_cyverse_password"
  echo "Warning: CYVERSE_PASSWORD environment variable missing"
else
  cyverse_password="${CYVERSE_PASSWORD}"
fi

if [[ -z "${DOCKER_USERNAME}" ]]; then
  docker_username="some_docker_username"
  echo "Warning: DOCKER_USERNAME environment variable missing"
else
  docker_username="${DOCKER_USERNAME}"
fi

if [[ -z "${DOCKER_PASSWORD}" ]]; then
  docker_password="some_docker_password"
  echo "Warning: DOCKER_PASSWORD environment variable missing"
else
  docker_password="${DOCKER_PASSWORD}"
fi

if [[ -z "${AWS_ACCESS_KEY}" ]]; then
  aws_access_key="some_aws_access_key"
  echo "Warning: AWS_ACCESS_KEY environment variable missing"
else
  aws_access_key="${AWS_ACCESS_KEY}"
fi

if [[ -z "${AWS_SECRET_KEY}" ]]; then
  aws_secret_key="some_aws_secret_key"
  echo "Warning: AWS_SECRET_KEY environment variable missing"
else
  aws_secret_key="${AWS_SECRET_KEY}"
fi

if [[ -z "${AWS_REGION}" ]]; then
  aws_region="some_aws_region"
  echo "Warning: AWS_REGION environment variable missing"
else
  aws_region="${AWS_REGION}"
fi

if [[ -z "${AWS_FEEDBACK_ARN}" ]]; then
  aws_feedback_arn="some_aws_feedback_arn"
  echo "Warning: AWS_FEEDBACK_ARN environment variable missing"
else
  aws_feedback_arn="${AWS_FEEDBACK_ARN}"
fi

cat <<EOT >>".env"
VUE_APP_TITLE=plantit
MAPBOX_TOKEN=mapbox_token
MAPBOX_FEATURE_REFRESH_MINUTES=60
CYVERSE_REDIRECT_URL=http://localhost:3000/apis/v1/users/cyverse_handle_temporary_code/
CYVERSE_CLIENT_ID=$cyverse_client_id
CYVERSE_CLIENT_SECRET=$cyverse_secret
CYVERSE_USERNAME=$cyverse_username
CYVERSE_PASSWORD=$cyverse_password
CYVERSE_TOKEN_REFRESH_MINUTES=60
NODE_ENV=development
DJANGO_SETTINGS_MODULE=plantit.settings
DJANGO_SECRET_KEY=$secret_key
DJANGO_DEBUG=True
DJANGO_FIELD_ENCRYPTION_KEY=$field_encryption_key
DJANGO_API_URL=http://plantit/apis/v1/
DJANGO_ALLOWED_HOSTS=*
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False
USERS_CACHE=/code/users.json
USERS_REFRESH_MINUTES=60
USERS_STATS_REFRESH_MINUTES=10
MORE_USERS=/code/more_users.json
AGENT_KEYS=${AGENT_KEYS}
WORKFLOWS_CACHE=/code/flows.json
WORKFLOWS_REFRESH_MINUTES=60
TASKS_TIMEOUT_MULTIPLER=2
TASKS_LOGS=/code/logs
TASKS_REFRESH_SECONDS=60
TASKS_CLEANUP_MINUTES=60
LAUNCHER_SCRIPT_NAME=launcher
SQL_ENGINE=django.db.backends.postgresql
SQL_HOST=postgres
SQL_PORT=5432
SQL_NAME=postgres
SQL_USER=postgres
SQL_PASSWORD=$sql_password
GITHUB_AUTH_URI=https://github.com/login/oauth/authorize
GITHUB_REDIRECT_URI=http://localhost:3000/apis/v1/users/github_handle_temporary_code/
GITHUB_SECRET=$github_secret
GITHUB_CLIENT_ID=$github_client_id
DOCKER_USERNAME=$docker_username
DOCKER_PASSWORD=$docker_password
NO_PREVIEW_THUMBNAIL=/code/plantit/front_end/src/assets/no_preview_thumbnail.png
AWS_ACCESS_KEY=$aws_access_key
AWS_SECRET_KEY=$aws_secret_key
AWS_REGION=$aws_region
AWS_FEEDBACK_ARN=$aws_feedback_arn
TUTORIALS_FILE=/code/tutorials.pdf
FEEDBACK_FILE=/code/feedback.pdf
EOT
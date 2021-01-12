#!/bin/bash

admin_password=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50)))\")")
secret_key=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50)))\")")
sql_password=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50)))\")")
field_encryption_key=$(python2 -c "exec(\"import cryptography.fernet\nprint('%s' % cryptography.fernet.Fernet.generate_key())\")")

if [[ -z "${GITHUB_CLIENT_ID}" ]]; then
  github_client_id="some_github_client_id"
  echo "Warning: GITHUB_CLIENT_ID environment variable missing"
else
  github_client_id="${GITHUB_CLIENT_ID}"
fi

if [[ -z "${GITHUB_USERNAME}" ]]; then
  github_username="some_github_username"
  echo "Warning: GITHUB_USERNAME environment variable missing"
else
  github_username="${GITHUB_USERNAME}"
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

cat <<EOT >>".env"
VUE_APP_TITLE=plantit
CYVERSE_REDIRECT_URL=http://localhost:3000/apis/v1/users/cyverse_handle_temporary_code/
CYVERSE_CLIENT_ID=$cyverse_client_id
CYVERSE_CLIENT_SECRET=$cyverse_secret
CYVERSE_USERNAME=$cyverse_username
CYVERSE_PASSWORD=$cyverse_password
NODE_ENV=development
DJANGO_SETTINGS_MODULE=plantit.settings
DJANGO_SECRET_KEY=$secret_key
DJANGO_DEBUG=True
DJANGO_FIELD_ENCRYPTION_KEY=$field_encryption_key
DJANGO_API_URL=http://plantit/apis/v1/
DJANGO_ALLOWED_HOSTS=*
DJANGO_ADMIN_USERNAME=admin
DJANGO_ADMIN_EMAIL=admin@example.com
DJANGO_ADMIN_PASSWORD=$admin_password
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False
FLOWS_CACHE=/code/flows.json
FLOWS_REFRESH_MINUTES=10
SQL_ENGINE=django.db.backends.sqlite3
GITHUB_AUTH_URI=https://github.com/login/oauth/authorize
GITHUB_REDIRECT_URI=http://localhost:3000/apis/v1/users/github_handle_temporary_code/
GITHUB_USERNAME=$github_username
GITHUB_KEY=$github_client_id
GITHUB_SECRET=$github_secret
DOCKER_USERNAME=$docker_username
DOCKER_PASSWORD=$docker_password
EOT
#!/bin/bash

admin_password=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50)))\")")
secret_key=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50)))\")")
sql_password=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50)))\")")
field_encryption_key=$(python2 -c "exec(\"import cryptography.fernet\nprint('%s' % cryptography.fernet.Fernet.generate_key())\")")

if [[ -z "${GITHUB_SECRET}" ]]; then
  github_secret="some_github_secret"
  echo "Warning: GITHUB_SECRET environment variable missing"
else
  github_secret="${GITHUB_SECRET}"
fi

if [[ -z "${CAS_SERVER_URL}" ]]; then
  cas_server_url="some_cas_server_url"
  echo "Warning: CAS_SERVER_URL environment variable missing"
else
  cas_server_url="${CAS_SERVER_URL}"
fi

cat <<EOT >>".env"
VUE_APP_TITLE=plantit
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
DJANGO_CAS_VERSION=3.0
DJANGO_CAS_SERVER_URL=$cas_server_url
DJANGO_CAS_PROXY_CALLBACK=http://localhost/accounts/callback/
DJANGO_CAS_FORCE_SSL_SERVICE_URL=False
SQL_ENGINE=django.db.backends.sqlite3
GITHUB_AUTH_URI=https://github.com/login/oauth/authorize
GITHUB_REDIRECT_URI=http://localhost/apis/v1/profiles/github_handle_temporary_code/
GITHUB_KEY=d15df2f5710e9597290f
GITHUB_SECRET=$github_secret
EOT
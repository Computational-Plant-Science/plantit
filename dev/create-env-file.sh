#!/bin/bash

admin_password=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50)))\")")
secret_key=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50)))\")")
sql_password=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for i in range(50)))\")")
field_encryption_key=$(python2 -c "exec(\"import cryptography.fernet\nprint('%s' % cryptography.fernet.Fernet.generate_key())\")")
if [[ -z "${GITHUB_SECRET}" ]]; then
  github_secret="some_github_secret"
  echo "Warning: Github OAuth App client secret missing"
else
  github_secret="${GITHUB_SECRET}"
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
DJANGO_ADMIN_PASSWORD=$admin_password
SQL_ENGINE=django.db.backends.postgresql
SQL_HOST=postgres
SQL_PORT=5432
SQL_NAME=postgres
SQL_USER=postgres
SQL_PASSWORD=$sql_password
GRAYLOG_GELF_URI=udp://localhost:12201
GRAYLOG_HTTP_EXTERNAL_URI=http://localhost:9000
GITHUB_AUTH_URI=https://github.com/login/oauth/authorize
GITHUB_REDIRECT_URI=http://localhost/apis/v1/profiles/github_handle_temporary_code/
GITHUB_KEY=d15df2f5710e9597290f
GITHUB_SECRET=$github_secret
EOT
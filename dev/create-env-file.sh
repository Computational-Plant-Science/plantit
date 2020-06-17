#!/bin/bash

admin_password=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@$%^&*(-_+)') for i in range(50)))\")")
secret_key=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@$%^&*(-_+)') for i in range(50)))\")")
sql_password=$(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@$%^&*(-_+)') for i in range(50)))\")")
field_encryption_key=$(python2 -c "exec(\"import cryptography.fernet\nprint('%s' % cryptography.fernet.Fernet.generate_key())\")")

cat <<EOT >>".env"
VUE_APP_TITLE=plantit
NODE_ENV=development
DJANGO_SETTINGS_MODULE=plantit.settings
DJANGO_SECRET_KEY=$secret_key
DJANGO_DEBUG=True
DJANGO_FIELD_ENCRYPTION_KEY=$field_encryption_key
DJANGO_API_URL=http://localhost/apis/v1/
DJANGO_ALLOWED_HOSTS=*
DJANGO_ADMIN_USERNAME=admin
DJANGO_ADMIN_PASSWORD=$admin_password
SQL_ENGINE=django.db.backends.postgresql
SQL_HOST=postgres
SQL_PORT=5432
SQL_NAME=postgres
SQL_USER=postgres
SQL_PASSWORD=$sql_password
DAGIT_GRAPHQL_URL=http://dagit:3000/graphql
DAGSTER_HOME=/code/plantit
DAGSTER_RUN_DB=run_storage
DAGSTER_EVENT_DB=event_log_storage
DAGSTER_SCHEDULE_DB=schedule_storage
DAGSTER_FILESTORAGE_BASEDIR=/opt/dagster
DAGSTER_CELERY_BACKEND=amqp://rabbitmq
DAGSTER_CELERY_BROKER=amqp://rabbitmq
GRAYLOG_GELF_URI=http://localhost:12201
GRAYLOG_HTTP_EXTERNAL_URI=http://localhost:9000
EOT
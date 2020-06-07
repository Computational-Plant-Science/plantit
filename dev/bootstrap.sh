#!/bin/bash

echo "Bootstrapping..."

DOCKER_COMPOSE="docker-compose -f docker-compose.yml -f docker-compose.dev.yml"

echo "Bringing containers down..."
$DOCKER_COMPOSE down

env_file=".env"
echo "Checking for environment variable file '$env_file'..."
if [ ! -f $env_file ]; then
  echo "Environment variable file '$env_file' does not exist. Creating it..."
  secret_key=($(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@$%^&*(-_+)') for i in range(50)))\")"))
  sql_password=($(python2 -c "exec(\"import random\nprint('%s' % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@$%^&*(-_+)') for i in range(50)))\")"))
  field_encryption_key=($(python2 -c "exec(\"import cryptography.fernet\nprint('%s' % cryptography.fernet.Fernet.generate_key())\")"))
  cat <<EOT >>$env_file
VUE_APP_TITLE=plantit
NODE_ENV=development
DJANGO_SETTINGS_MODULE=plantit.settings
DJANGO_SECRET_KEY=$secret_key
DJANGO_DEBUG=True
DJANGO_FIELD_ENCRYPTION_KEY=$field_encryption_key
DJANGO_API_URL=http://localhost/apis/v1/
DJANGO_ALLOWED_HOSTS=*
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
EOT
else
  echo "Environment variable file '$env_file' already exists. Continuing..."
fi

dagster_config_file="plantit/dagster.yaml"
echo "Checking for dagster config file '$dagster_config_file'..."
if [ ! -f $dagster_config_file ]; then
  echo "Dagster config file '$dagster_config_file' does not exist. Creating it..."
  sql_user=$(cut -d '=' -f 2 <<< "$(grep "SQL_USER" "$env_file")" )
  sql_host=$(cut -d '=' -f 2 <<< "$(grep "SQL_HOST" "$env_file")" )
  sql_port=$(cut -d '=' -f 2 <<< "$(grep "SQL_PORT" "$env_file")" )
  if [[ -n "$sql_password" ]]; then
    sql_password=$sql_password
  else
    sql_password=$(cut -d '=' -f 2 <<< "$(grep "SQL_PASSWORD" "$env_file")" )
  fi
  run_db=$(cut -d '=' -f 2 <<< "$(grep "DAGSTER_RUN_DB" "$env_file")" )
  event_db=$(cut -d '=' -f 2 <<< "$(grep "DAGSTER_EVENT_DB" "$env_file")" )
  schedule_db=$(cut -d '=' -f 2 <<< "$(grep "DAGSTER_SCHEDULE_DB" "$env_file")" )
  cat <<EOT >>$dagster_config_file
run_storage:
  module: dagster_postgres.run_storage
  class: PostgresRunStorage
  config:
    postgres_db:
      username: $sql_user
      password: $sql_password
      hostname: $sql_host
      db_name: $run_db
      port: $sql_port

event_log_storage:
  module: dagster_postgres.event_log
  class: PostgresEventLogStorage
  config:
    postgres_db:
      username: $sql_user
      password: $sql_password
      hostname: $sql_host
      db_name: $event_db
      port: $sql_port

scheduler:
  module: dagster_cron.cron_scheduler
  class: SystemCronScheduler

schedule_storage:
  module: dagster_postgres.schedule_storage
  class: PostgresScheduleStorage
  config:
    postgres_db:
      username: $sql_user
      password: $sql_password
      hostname: $sql_host
      db_name: $schedule_db
      port: $sql_port

local_artifact_storage:
  module: dagster.core.storage.root
  class: LocalArtifactStorage
  config:
    base_dir: "/var/shared/dagster"

compute_logs:
  module: dagster.core.storage.local_compute_log_manager
  class: LocalComputeLogManager
  config:
    base_dir: "/var/shared/logs/dagster"

dagit:
  execution_manager:
    disabled: False
    max_concurrent_runs: 10 # Test and tune
EOT
else
  echo "Dagster config file '$dagster_config_file' already exists. Continuing..."
fi

echo "Building front end..."
cd plantit/front_end || exit
npm install
npm run build
cd ../..

echo "Removing migrations..."
find . -path "./plantit/**/migrations/*.py" -not -name "__init__.py" -delete

echo "Removing files..."
rm -rf plantit/files/*
mkdir -p plantit/files/public
mkdir -p plantit/files/tmp

echo "Building containers..."
$DOCKER_COMPOSE build "$@" --no-cache
$DOCKER_COMPOSE up -d plantit

echo "Running migrations..."
$DOCKER_COMPOSE exec plantit /code/dev/wait-for-postgres.sh postgres python manage.py makemigrations
$DOCKER_COMPOSE exec plantit python manage.py migrate

echo "Creating superuser..."
$DOCKER_COMPOSE exec plantit /code/dev/configure-superuser.sh -u "admin" -p "admin" -e "admin@example.com" -v

echo "Configuring mock cluster and IRODS..."
$DOCKER_COMPOSE up -d irods
$DOCKER_COMPOSE up -d cluster
$DOCKER_COMPOSE exec cluster /bin/bash /root/wait-for-it.sh irods:1247 -- /root/configure-irods.sh
if [ -f config/ssh/known_hosts ]; then
  touch config/ssh/known_hosts
fi
$DOCKER_COMPOSE exec plantit bash -c "ssh-keyscan -H cluster >> /code/config/ssh/known_hosts"
if [ ! -f config/ssh/id_rsa.pub ]; then
  ssh-keygen -b 2048 -t rsa -f config/ssh/id_rsa -N ""
fi
$DOCKER_COMPOSE exec plantit bash -c "/code/dev/ssh-copy-id.expect"

echo "Creating Dagster databases..."
$DOCKER_COMPOSE exec plantit /code/dev/create-dagster-databases.sh run_storage event_log_storage schedule_storage

echo "Stopping containers..."
$DOCKER_COMPOSE stop
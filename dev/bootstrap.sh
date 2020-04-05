#!/bin/bash

echo "Bootstrapping [DEVELOPMENT] environment..."

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
EOT
else
  echo "Environment variable file '$env_file' already exists. Continuing..."
fi

dagster_config_file="dagster.yaml"
echo "Checking for dagster config file '$dagster_config_file'..."
if [ ! -f $dagster_config_file ]; then
  echo "Dagster config file '$dagster_config_file' does not exist. Creating it..."
  if [[ -n "$sql_password" ]]; then
    password=$sql_password
  else
    password=$(cut -d '=' -f 2 <<< "$(grep "SQL_PASSWORD" "$env_file")" )
  fi
  cat <<EOT >>$dagster_config_file
run_storage:
  module: dagster_postgres.run_storage
  class: PostgresRunStorage
  config:
    postgres_db:
      username: postgres
      password: $password
      hostname: postgres
      db_name: run_storage
      port: 5432

event_log_storage:
  module: dagster_postgres.event_log
  class: PostgresEventLogStorage
  config:
    postgres_db:
      username: postgres
        password: $password
        hostname: postgres
        db_name: event_log_storage
        port: 5432

scheduler:
  module: dagster_cron.cron_scheduler
  class: SystemCronScheduler

schedule_storage:
  module: dagster_postgres.schedule_storage
  class: PostgresScheduleStorage
  config:
    postgres_db:
      username: postgres
        password: $password
        hostname: postgres
        db_name: schedule_storage
        port: 5432

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
$DOCKER_COMPOSE build "$@"

echo "Running migrations..."
$DOCKER_COMPOSE up -d --remove-orphans postgres
$DOCKER_COMPOSE run plantit /code/dev/wait-for-postgres.sh postgres python manage.py makemigrations
$DOCKER_COMPOSE run plantit python manage.py migrate

echo "Creating superuser..."
$DOCKER_COMPOSE run plantit /code/dev/configure-superuser.sh -u "admin" -p "admin" -e "admin@example.com" -v

echo "Configuring mock IRODS..."
$DOCKER_COMPOSE up -d irods
$DOCKER_COMPOSE up -d ssh
$DOCKER_COMPOSE exec ssh /bin/bash /root/wait-for-it.sh irods:1247 -- /root/configure-irods.sh

echo "Stopping containers..."
$DOCKER_COMPOSE stop


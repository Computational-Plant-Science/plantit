#!/bin/bash

env_file=".env"
sql_user=$(cut -d '=' -f 2 <<< "$(grep "SQL_USER" "$env_file")" )
sql_host=$(cut -d '=' -f 2 <<< "$(grep "SQL_HOST" "$env_file")" )
sql_port=$(cut -d '=' -f 2 <<< "$(grep "SQL_PORT" "$env_file")" )
sql_password=$(cut -d '=' -f 2 <<< "$(grep "SQL_PASSWORD" "$env_file")" )
run_db=$(cut -d '=' -f 2 <<< "$(grep "DAGSTER_RUN_DB" "$env_file")" )
event_db=$(cut -d '=' -f 2 <<< "$(grep "DAGSTER_EVENT_DB" "$env_file")" )
schedule_db=$(cut -d '=' -f 2 <<< "$(grep "DAGSTER_SCHEDULE_DB" "$env_file")" )

cat <<EOT >>"plantit/dagster.yaml"
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
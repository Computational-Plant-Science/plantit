![alt text](https://github.com/Computational-Plant-Science/plantit/blob/master/plantit/front_end/src/assets/logo.png?raw=true)

# PlantIT [![Build Status](https://travis-ci.com/Computational-Plant-Science/plantit.svg?branch=master)](https://travis-ci.com/Computational-Plant-Science/plantit)

**Phenomics**-as-a-Service software for accessible, reproducible plant science.

**This project is under active development and is not yet stable**.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Contents**

- [Requirements](#requirements)
- [Documentation](#documentation)
- [Installation](#installation)
  - [Development](#development)
  - [Production](#production)
- [Environment variables](#environment-variables)
- [Workflows](#workflows)
- [Clusters](#clusters)
  - [Cluster login configuration](#cluster-login-configuration)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Requirements

The following are required to run `PlantIT` in a Unix environment:

- [Docker](https://www.docker.com/)
- [npm](https://www.npmjs.com/get-npm)

## Documentation

Full documentation can be found [here](https://computational-plant-science.github.io/DIRT2_Webplatform/build/html/index.html).

## Installation

First, clone the repository:

```bash
git clone git@github.com:Computational-Plant-Science/plantit.git
```

### Development

To set up a new (or restore a clean) development environment, run `dev/bootstrap.sh` from the project root (you may need to use `chmod +x` first). This will:

- Stop and remove project containers and networks
- If an `.env` file (to configure environment variables) does not exist, generate one with default values
- Remove migrations and stored files
- Rebuild containers
- Run migrations
- Create a Django superuser (username `admin`, password `admin`) for the web application
- Configure a mock IRODS server and compute cluster, populating a `known_hosts` file and creating a public/private keypair in `config/ssh`
- Build the Vue front end

Then bring the project up with `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up` (`-d` for detached mode).

This will start a number of containers:

- `plantit`: Django web application (`http://localhost:80`)
- `dagit`: Dagster Dagit instance (`http://localhost:3000`)
- `dagster-celery`: Celery worker for Dagster
- `rabbitmq`: RabbitMQ message broker (admin UI at `http://localhost:15672`)
- `postgres`: PostgreSQL database
- `flower`: Celery monitoring UI (`http://localhost:5555`)
- `adminer`: DB admin UI (`http://localhost:8080`)
- `irods`: mock IRODS server
- `cluster`: mock compute cluster

To bypass CAS login and log directly into Django as superuser, browse to `http://localhost/accounts/login/` and enter username `admin` and password `admin`.

The Django admin interface is at `http://localhost/admin/`.

#### Tests

Tests can be run with `docker-compose -f docker-compose.yml -f docker-compose.dev.yml run plantit /code/dev/wait-for-postgres.sh postgres ./manage.py test`.

### Production

The production configurations look somewhat different than development:

- Django runs behind Gunicorn (both in the same container) which runs behind NGINX (in a separate container)
- NGINX serves static assets and acts as a reverse proxy
- Postgres stores data in a persistent volume
- Graylog consumes and stores container logs
- Google Analytics are enabled via [`vue-analytics`](https://github.com/MatteoGabriele/vue-analytics)
- [Sentry](https://sentry.io/welcome/) provides Vue monitoring and error tracking
- Monitoring tools (Adminer and RabbitMQ dashboard)

Before running PlantIT in a production environment, you must:

- Configure environment variables
- Build the Vue front end with `npm run build` from the `plantit/front_end` directory
- Collect static files:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run plantit ./manage.py collectstatic --no-input
```

- Run migrations:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run plantit /code/dev/wait-for-postgres.sh postgres ./manage.py makemigrations
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run plantit ./manage.py migrate
```

- Create a Django superuser (if one does not exist):

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run plantit /code/dev/configure-superuser.sh -u "<username>" -p "<password>" -e "<email address>"
```

- Configure NGINX `server_name` in `config/ngnix/conf.d/local.conf` to match the host's IP or FQDN
- If deploying for the first time, Graylog must be configured to consume input from other containers once they have all been brought up

Containers can then be brought up with:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

This will start the following:

- `plantit`: Django web application (`http://<host>:80`)
- `dagit`: Dagster Dagit instance (`http://<host>:3000`)
- `dagster-celery`: Celery worker for Dagster
- `rabbitmq`: RabbitMQ message broker (admin UI at `http://localhost:15672`)
- `postgres`: PostgreSQL database
- `flower`: Celery monitoring UI (`http://localhost:5555`)
- `adminer`: PostgreSQL admin UI (`http://localhost:8080`)
- `nginx`: NGINX server

## Environment variables

Docker will read environment variables in the following format from a file named `.env` in the `plantit` root directory (if the file exists):

```
key=value
key=value
...
```

`bootstrap.sh` will generate an `.env` file like the following if one does not exist:

```
VUE_APP_TITLE=plantit
NODE_ENV=development
DJANGO_SETTINGS_MODULE=plantit.settings
DJANGO_SECRET_KEY=some_secret_key
DJANGO_DEBUG=True
DJANGO_FIELD_ENCRYPTION_KEY=some_encryption_key
DJANGO_API_URL=http://localhost/apis/v1/
DJANGO_ALLOWED_HOSTS=*
DJANGO_ADMIN_USERNAME=admin
DJANGO_ADMIN_PASSWORD=some_password
SQL_ENGINE=django.db.backends.postgresql
SQL_HOST=postgres
SQL_PORT=5432
SQL_NAME=postgres
SQL_USER=postgres
SQL_PASSWORD=some_password
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
```

Note that `DJANGO_SECRET_KEY`, `DJANGO_FIELD_ENCRYPTION_KEY`, and `SQL_PASSWORD` are given dummy values above. Executing `dev/bootstrap.sh` in a clean (empty) install directory will generate secure values.

In addition to the environment variables listed above, the following is required to run PlantIT in staging or production:

- `GRAYLOG_GELF_URI`: the endpoint to route log messages to (e.g., the pre-configured value `udp://localhost:12201` if Graylog server is running on the same host as PlantIT)
- `GRAYLOG_HTTP_EXTERNAL_URI`: the Graylog server HTTP API endpoint (e.g., the pre-configured value `http://localhost:9000/`)
- `NODE_ENV` should be set to `production`
- `DJANGO_DEBUG` should be set to `False`
- `DJANGO_API_URL` should point to the host's IP or FQDN

The following variables are required only in production:

- `VUE_APP_ANALYTICS_ID`: provided by Google Analytics
- `VUE_APP_SENTRY_IO_KEY`: provided by Sentry
- `VUE_APP_SENTRY_IO_PROJECT`: provided by Sentry

## Workflows

Workflows created with the [Plant IT workflow template](https://github.com/Computational-Plant-Science/cookiecutter_PlantIT) can be plugged into the web platform by placing workflow repositories in the `django/workflows` directory.

Note that the  `dagit`, and `dagster-celery`, and `plantit` containers must be restarted to reload workflows:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart dagit
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart dagster-celery
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart plantit
```

Note also that the workflow directory name must be identical to the `app_name` configured when the workflow was created (this can also be edited later in the `WORKFLOW_CONFIG` dictionary in `workflow.py`.

## Clusters

See [ClusterSide README](https://github.com/Computational-Plant-Science/plantit-clusterside) for information on installation and configuration of required remote Plant IT code on cluster.

Clusters are added via the admin interface `(/admin/)`. Choose Clusters->Add Cluster. Fill in the commands
accordingly.

Typically, the submit commands will include `clusterside submit`. They may also include loading packages necessary to run clusterside, for example, loading python3.

For Sapelo2 (UGA's cluster), the submit command is:

```bash
ml Python/3.6.4-foss-2018a; /home/cotter/.local/bin/clusterside submit
```

Note that in some environments, [`plantit-clusterside`](https://github.com/Computational-Plant-Science/plantit-clusterside) may not automatically be added to `$PATH` upon installation; either update `$PATH` or use `plantit-clusterside`'s absolute path.

### Cluster login configuration

Plant IT supports both ssh password and public-key based
login. To use public-key login, leave the Password field blank. Public-key login requires the private key and a known_hosts list to be available. Plant IT expects this data to be in the following two files:

- `config/ssh/id_rsa`: The private key used for login
- `config/ssh/known_hosts`: The known_hosts file.

The easiest way to setup public-key logins is to configure the keys for login from the web server, then copy the configured `id_rsa` and `known_hosts` files from the web server user (typically in `$HOME/.ssh/`) to `config/ssh/`

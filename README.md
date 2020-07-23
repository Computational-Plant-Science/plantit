<p align="center">
<img src="https://github.com/Computational-Plant-Science/plantit/blob/master/plantit/front_end/src/assets/logo.png?raw=true" />
<br /><br />
<a href="https://travis-ci.com/Computational-Plant-Science/plantit.svg?branch=master"><img src='https://travis-ci.com/Computational-Plant-Science/plantit.svg?branch=master' alt='Build Status' /></a>
<a href='https://coveralls.io/github/Computational-Plant-Science/plantit?branch=HEAD'><img src='https://coveralls.io/repos/github/Computational-Plant-Science/plantit/badge.svg?branch=HEAD' alt='Coverage Status' /></a>

# PlantIT

Plant science workflow automation in the browser.

</p>

**This project is in open alpha and is not yet stable**.

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
- Python 2.7+

## Installation

First, clone the repository:

```bash
git clone git@github.com:Computational-Plant-Science/plantit.git
```

### Development

To set up a new (or restore a clean) development environment, run `dev/bootstrap.sh` from the project root (you may need to use `chmod +x` first). You can use the `-n` option to disable the Docker build cache. This command will:

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
- `celery`: Celery worker
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
- `celery`: Celery worker for Dagster
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
DJANGO_SECURE_SSL_REDIRECT=False
SQL_ENGINE=django.db.backends.postgresql
SQL_HOST=postgres
SQL_PORT=5432
SQL_NAME=postgres
SQL_USER=postgres
SQL_PASSWORD=some_password
GRAYLOG_GELF_URI=http://localhost:12201
GRAYLOG_HTTP_EXTERNAL_URI=http://localhost:9000
```

Note that `DJANGO_SECRET_KEY`, `DJANGO_FIELD_ENCRYPTION_KEY`, and `SQL_PASSWORD` are given dummy values above. Executing `dev/bootstrap.sh` in a clean (empty) install directory will generate secure values.

In addition to the environment variables listed above, the following is required to run PlantIT in staging or production:

- `GRAYLOG_GELF_URI`: the endpoint to route log messages to (e.g., the pre-configured value `udp://localhost:12201` if Graylog server is running on the same host as PlantIT)
- `GRAYLOG_HTTP_EXTERNAL_URI`: the Graylog server HTTP API endpoint (e.g., the pre-configured value `http://localhost:9000/`)
- `NODE_ENV` should be set to `production`
- `DJANGO_DEBUG` should be set to `False`
- `DJANGO_SECURE_SSL_REDIRECT` should be set to `True`
- `DJANGO_API_URL` should point to the host's IP or FQDN

The following variables are required only in production:

- `VUE_APP_ANALYTICS_ID`: provided by Google Analytics
- `VUE_APP_SENTRY_IO_KEY`: provided by Sentry
- `VUE_APP_SENTRY_IO_PROJECT`: provided by Sentry

## Compute targets

Targets are added via the Django admin interface. Note that [`plantit-cli`](https://github.com/Computational-Plant-Science/plantit-cli) must be installed on the target. In some environments, [`plantit-cli`](https://github.com/Computational-Plant-Science/plantit-cli) may not automatically be added to `$PATH` upon installation; either update `$PATH` or use `plantit-cli`'s absolute path.

PlantIT supports both ssh password and public-key based
login. To use public-key login, leave the Password field blank. Public-key login requires the private key and a known_hosts list to be available. Plant IT expects this data to be in the following two files:

- `config/ssh/id_rsa`: The private key used for login
- `config/ssh/known_hosts`: The known_hosts file.

The easiest way to setup public-key logins is to configure the keys for login from the web server, then copy the configured `id_rsa` and `known_hosts` files from the web server user (typically in `$HOME/.ssh/`) to `config/ssh/`

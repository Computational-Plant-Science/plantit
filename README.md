<p align="center">
<img src="https://github.com/Computational-Plant-Science/plantit/blob/master/plantit/front_end/src/assets/logo.png?raw=true" />
</p>

# PlantIT

![CI](https://github.com/Computational-Plant-Science/plantit/workflows/CI/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/plantit/badge/?version=latest)](https://plantit.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/Computational-Plant-Science/plantit/badge.svg?branch=HEAD)](https://coveralls.io/github/Computational-Plant-Science/plantit)

Plant science workflow automation in the browser.

**This project is in open alpha and is not yet stable**.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Contents**

- [Requirements](#requirements)
- [Installation](#installation)
  - [Development](#development)
    - [Tests](#tests)
  - [Production](#production)
    - [SSL Certificates](#ssl-certificates)
- [Environment variables](#environment-variables)
- [Deployment targets](#deployment-targets)

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

To set up a new (or restore a clean) development environment, run `scripts/bootstrap.sh` from the project root (you may need to use `chmod +x` first). You can use the `-n` option to disable the Docker build cache. This command will:

- Stop and remove project containers and networks
- If an `.env` file (to configure environment variables) does not exist, generate one with default values
- Rebuild containers
- Run migrations
- If a Django superuser does not exist, create one (username and password specified in `.env`)
- Configure a sandbox container to act as a test deployment target (creates a public/private keypair in `config/ssh` if one does not exist, then configures SSH key authentication between the web application container and the sandbox environment)
- Build the Vue front end

Bring everything up with `docker-compose -f docker-compose.dev.yml up` (`-d` for detached mode).

This will start a number of containers:

- `plantit`: Django web application (`http://localhost:3000`)
- `postgres`: PostgreSQL database
- `rabbitmq`: RabbitMQ message broker (admin UI at `http://localhost:15672`)
- `celery`: Celery worker
- `sandbox`: test deployment target

The Django admin interface is at `http://localhost:3000/admin/`. To use it, you'll need to log into PlantIT at least once with CyVerse (this will create a Django account for you), then shell into the `plantit` container, run `./manage.py shell`, and update your profile with staff/superuser privileges. For instance:

```python
from django.contrib.auth.models import User
user = User.objects.get(username=<your CyVerse username>)
user.is_staff = True
user.is_superuser = True
user.save()
```

#### Tests

Tests can be run with `docker-compose -f docker-compose.dev.yml exec plantit ./manage.py test`.

### Production

In production configuration:

- Django runs behind Gunicorn (both in the same container) which runs behind NGINX (in a separate container)
- Postgres stores data in a persistent volume
- NGINX serves static assets and acts as a reverse proxy

To configure PlantIT for deployment, first clone the repo, then run `./scripts/deploy.sh <host IP or FQDN> <admin email address>` from the root directory. This script is idempotent and may safely be triggered to run by e.g., a CI/CD server. This will:

- Bring containers down
- Fetch the latest version of the project
- Pull the latest versions of Docker containers
- Build the Vue front end
- Collect static files
- Configure NGINX (replace `localhost` in `config/ngnix/conf.d/local.conf` with the host's IP or FQDN)
- Configure environment variables (disable debugging, enable SSL and secure cookies, etc)
- Bring containers up
- Run migrations
- Create a superuser (if one does not already exist)
- Configure the `sandbox` deployment target (if not already configured)

At this point the following containers should be running:

- `plantit`: Django web application (`http://localhost:80`)
- `postgres`: PostgreSQL database
- `rabbitmq`: RabbitMQ message broker (admin UI at `http://localhost:15672`)
- `celery`: Celery worker
- `sandbox`: sandbox deployment target
- `nginx`: NGINX reverse proxy

#### SSL Certificates

PlantIT uses [Let's Encrypt](https://letsencrypt.org/) and [Certbot](https://certbot.eff.org/) for SSL certification. The production configuration includes a `certbot` container which can be used to request new or renew existing certificates from Let's Encrypt. Standard certificates last 90 days. To request a new certificate, run:

```shell
docker-compose -f docker-compose.prod.yml run certbot
```

To renew an existing certificate, use the `renew` command, then restart all containers:

```shell
docker-compose -f docker-compose.prod.yml run certbot renew
docker-compose -f docker-compose.prod.yml restart
```

Use the `--dry-run` flag with any command to test without writing anything to disk.

## Environment variables

Docker will read environment variables in the following format from a file named `.env` in the project root directory (if the file exists):

```
key=value
key=value
...
```

`bootstrap.sh` will generate an `.env` file like the following if one does not exist:

```
VUE_APP_TITLE=plantit
MAPBOX_TOKEN=<your Mapbox token>
MAPBOX_FEATURE_REFRESH_MINUTES=60
CYVERSE_REDIRECT_URL=http://localhost:3000/apis/v1/idp/cyverse_handle_temporary_code/
CYVERSE_CLIENT_ID=<your cyverse client id>
CYVERSE_CLIENT_SECRET=<your cyverse client secret>
CVVERSE_USERNAME=<your cyverse username>
CYVERSE_PASSWORD=<your cyverse password>
CYVERSE_TOKEN_REFRESH_MINUTES=60
NODE_ENV=development
DJANGO_SETTINGS_MODULE=plantit.settings
DJANGO_SECRET_KEY=<your django secret key>
DJANGO_DEBUG=True
DJANGO_FIELD_ENCRYPTION_KEY=<your django field encryption key>
DJANGO_API_URL=http://plantit:3000/apis/v1/
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False
DJANGO_ALLOWED_HOSTS=*
DJANGO_ADMIN_USERNAME=<your django admin username>
DJANGO_ADMIN_PASSWORD=<your django admin password>
DJANGO_ADMIN_EMAIL=<your django admin email>
CELERY_TEMPLATE_LOCAL_RUN_SCRIPT=/code/scripts/template_local_run.sh
CELERY_TEMPLATE_SLURM_RUN_SCRIPT=/code/scripts/template_slurm_run.sh
USERS_CACHE=/code/users.json
USERS_REFRESH_MINUTES=60
USERS_STATS_REFRESH_MINUTES=10
MORE_USERS=/code/more_users.json
AGENT_KEYS=/code/agent_keys
WORKFLOWS_CACHE=/code/workflows.json
WORKFLOWS_REFRESH_MINUTES=60
SESSIONS_LOGS=/code/sessions
TASKS_LOGS=/code/logs
RUNS_TIMEOUT_MULTIPLIER=2
LAUNCHER_SCRIPT_NAME=launch
SQL_ENGINE=django.db.backends.postgresql
SQL_HOST=postgres
SQL_PORT=5432
SQL_NAME=postgres
SQL_USER=postgres
SQL_PASSWORD=$sql_password
GITHUB_AUTH_URI=https://github.com/login/oauth/authorize
GITHUB_REDIRECT_URI=http://localhost:3000/apis/v1/users/github_handle_temporary_code/
GITHUB_KEY=<your github key>
GITHUB_SECRET=<your github secret>
GITHUB_CLIENT_ID=d15df2f5710e9597290f
DOCKER_USERNAME=<your docker username>
DOCKER_PASSWORD=<your docker password>
NO_PREVIEW_THUMBNAIL=/code/plantit/front_end/src/assets/no_preview_thumbnail.png
AWS_ACCESS_KEY=<your AWS access key>
AWS_SECRET_KEY=<your AWS secret key>
AWS_REGION=<your AWS region>
AWS_FEEDBACK_ARN=<your AWS feedback ARN>
```

Note that `CYVERSE_CLIENT_ID`, `CYVERSE_CLIENT_SECRET`, `CVVERSE_USERNAME`, `CYVERSE_PASSWORD`, `GITHUB_KEY`, and `GITHUB_SECRET` must be supplied manually, while `DJANGO_SECRET_KEY`, `DJANGO_FIELD_ENCRYPTION_KEY`, and ``DJANGO_ADMIN_PASSWORD`` will be auto-generated by `scripts/bootstrap.sh` in a clean (empty) install directory.

The following variables must be reconfigured for production environments (`scripts/deploy` will automatically do so):

- `NODE_ENV` should be set to `production`
- `DJANGO_DEBUG` should be set to `False`
- `DJANGO_SECURE_SSL_REDIRECT` should be set to `True`
- `DJANGO_API_URL` should point to the host's IP or FQDN

## Deployment targets

Deployment targets may be configured via the Django admin interface. Note that [`plantit-cli`](https://github.com/Computational-Plant-Science/plantit-cli) must be installed on the target. In some environments, [`plantit-cli`](https://github.com/Computational-Plant-Science/plantit-cli) may not automatically be added to `$PATH` upon installation; either update `$PATH` or use `plantit-cli`'s absolute path.

PlantIT uses `paramiko` to orchestrate workflows on deployment targets over SSH. Password and public-key authentication are supported; to use a key, leave the `password` field blank and provide the `plantit` container with a key and fingerprint in `config/ssh/`:

- `config/ssh/id_rsa`
- `config/ssh/known_hosts`

Key authentication is configured for the `sandbox` deployment target when bootstrapping or deploying PlantIT; refer to `scripts/bootstrap.sh` or `scripts/deploy` for more detail.
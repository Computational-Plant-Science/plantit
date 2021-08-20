<p align="center">
<img src="https://github.com/Computational-Plant-Science/plantit/blob/master/plantit/front_end/src/assets/logo.png?raw=true" />
</p>

# PlantIT

Plant phenotyping automation in the browser.

![commit](https://github.com/Computational-Plant-Science/plantit/workflows/commit/badge.svg)
![release](https://github.com/Computational-Plant-Science/plantit/workflows/release/badge.svg)
[![Documentation Status](https://readthedocs.org/projects/plantit/badge/?version=latest)](https://plantit.readthedocs.io/en/latest/?badge=latest)
[![Coverage Status](https://coveralls.io/repos/github/Computational-Plant-Science/plantit/badge.svg?branch=HEAD)](https://coveralls.io/github/Computational-Plant-Science/plantit)

**This project is in open beta and is not yet stable**.

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
- Build the Vue front end
- Build Docker images
- Run migrations

Then bring everything up with `docker-compose -f docker-compose.dev.yml up` (`-d` for detached mode).

This will start a number of containers:

- `plantit`: Django web application (`http://localhost:3000`)
- `postgres`: PostgreSQL database
- `celery`: Celery worker
- `redis`: Redis server (used as cache and Celery message broker)
- `sandbox`: an Ubuntu environment for testing workflows

The Django admin interface is at `http://localhost:3000/admin/`. To use it, you'll need to log into PlantIT at least once with CyVerse (this will create a Django account for you), then shell into the `plantit` container, run `./manage.py shell`, and update your profile with staff/superuser privileges. For instance:

```python
from django.contrib.auth.models import User
user = User.objects.get(username=<your CyVerse username>)
user.is_staff = True
user.is_superuser = True
user.save()
```

Note that the bootstrap script will not clear migrations. To restore to a totally clean database state, you will need to remove all `*.py` files from the `plantit/plantit/migrations` directory (except for `__init__.py`).

#### Tests

Once the containers are up, tests can be run with `docker-compose -f docker-compose.dev.yml exec plantit ./manage.py test`.

### Production

In production configuration, NGINX servers static assets and reverse-proxies the back-end. Django also runs behind Gunicorn (both in the same container).

To configure PlantIT for deployment, first clone the repo, then, from the root directory, run:

```
chmod +x /scripts/deploy.sh
./scripts/deploy.sh <configuration ('rc' or 'prod')> <host IP or FQDN> <admin email address>
```

This script is idempotent and may safely be triggered to run by e.g., a CI/CD server. This will:

- Bring containers down
- Fetch the latest version of the project
- Pull the latest versions of Docker containers
- Build the Vue front end
- Collect static files
- Configure NGINX (replace `localhost` in `config/ngnix/conf.d/local.conf` with the host's IP or FQDN, configured via environment variable)
- Update environment variables (disable debugging, enable SSL and secure cookies, etc)
- Bring containers up
- Run migrations

At this point the following containers should be running:

- `plantit`: Django web application (`http://localhost:80`)
- `postgres`: PostgreSQL database
- `redis`: Redis server
- `celery`: Celery worker
- `sandbox`: an Ubuntu environment for testing workflows
- `nginx`: NGINX server/reverse proxy

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
TASKS_TEMPLATE_SCRIPT_LOCAL=/code/scripts/template_local_run.sh
TASKS_TEMPLATE_SCRIPT_SLURM=/code/scripts/template_slurm_run.sh
USERS_CACHE=/code/users.json
USERS_REFRESH_MINUTES=60
USERS_STATS_REFRESH_MINUTES=10
MORE_USERS=/code/more_users.json
AGENT_KEYS=/code/agent_keys
WORKFLOWS_CACHE=/code/workflows.json
WORKFLOWS_REFRESH_MINUTES=60
TASKS_LOGS=/code/logs
TASKS_TIMEOUT_MULTIPLIER=2
LAUNCHER_SCRIPT_NAME=launch
SQL_ENGINE=django.db.backends.postgresql
SQL_HOST=postgres
SQL_PORT=5432
SQL_NAME=postgres
SQL_USER=postgres
SQL_PASSWORD=<your database password>
GITHUB_AUTH_URI=https://github.com/login/oauth/authorize
GITHUB_REDIRECT_URI=http://localhost:3000/apis/v1/users/github_handle_temporary_code/
GITHUB_SECRET=<your github secret>
GITHUB_CLIENT_ID=<your github client ID>
DOCKER_USERNAME=<your docker username>
DOCKER_PASSWORD=<your docker password>
NO_PREVIEW_THUMBNAIL=/code/plantit/front_end/src/assets/no_preview_thumbnail.png
AWS_ACCESS_KEY=<your AWS access key>
AWS_SECRET_KEY=<your AWS secret key>
AWS_REGION=<your AWS region>
AWS_FEEDBACK_ARN=<your AWS feedback ARN>
TUTORIALS_FILE=/code/tutorials.pdf
FEEDBACK_FILE=/code/feedback.pdf
```

Note that the following environment variables must be supplied manually:

- `MAPBOX_TOKEN`
- `CYVERSE_CLIENT_ID`
- `CYVERSE_CLIENT_SECRET`
- `CVVERSE_USERNAME`
- `CYVERSE_PASSWORD`
- `GITHUB_CLIENT_ID`
- `GITHUB_SECRET`
- `AWS_ACCESS_KEY`
- `AWS_SECRET_KEY`
- `AWS_REGION`
- `AWS_FEEDBACK_ARN`
  
Several others will be auto-generated by `scripts/bootstrap.sh` in a clean install directory:

- `DJANGO_SECRET_KEY`
- `DJANGO_FIELD_ENCRYPTION_KEY`
- `DJANGO_ADMIN_PASSWORD`

Some variables must be reconfigured for production environments (`scripts/deploy` will automatically do so):

- `NODE_ENV` should be set to `production`
- `DJANGO_DEBUG` should be set to `False`
- `DJANGO_SECURE_SSL_REDIRECT` should be set to `True`
- `DJANGO_API_URL` should point to the host's IP or FQDN

## Deployment targets

Deployment targets may be configured via the Django admin interface or directly via the UI. The [`plantit-cli`](https://github.com/Computational-Plant-Science/plantit-cli) package must be installed and invokable on deployment targets. In some environments, [`plantit-cli`](https://github.com/Computational-Plant-Science/plantit-cli) may not automatically be added to `$PATH` upon installation; either update `$PATH` or use `plantit-cli`'s absolute path.

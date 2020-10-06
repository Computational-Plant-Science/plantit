<p align="center">
<img src="https://github.com/Computational-Plant-Science/plantit/blob/master/plantit/front_end/src/assets/logo.png?raw=true" />
</p>

# PlantIT

[![Build Status](https://travis-ci.com/Computational-Plant-Science/plantit.svg?branch=master)](https://travis-ci.com/Computational-Plant-Science/plantit)
[![Coverage Status](https://coveralls.io/repos/github/Computational-Plant-Science/plantit/badge.svg?branch=HEAD)](https://coveralls.io/github/Computational-Plant-Science/plantit?branch=HEAD)

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
- [Environment variables](#environment-variables)
- [Compute targets](#compute-targets)

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

- `plantit`: Django web application (`http://localhost:80`)
- `rabbitmq`: RabbitMQ message broker (admin UI at `http://localhost:15672`)
- `celery`: Celery worker
- `sandbox`: test deployment target

To bypass KeyCloak login and log directly into Django as superuser, browse to `http://localhost/accounts/login/` and use the values for `DJANGO_ADMIN_USERNAME` and `DJANGO_ADMIN_PASSWORD` configured in `.env`.

The Django admin interface is at `http://localhost/admin/`.

#### Tests

Tests can be run with `docker-compose -f docker-compose.dev.yml run plantit ./manage.py test`.

### Production

In production configuration:

- Django runs behind Gunicorn (both in the same container) which runs behind NGINX (in a separate container)
- NGINX serves static assets and acts as a reverse proxy

To configure PlantIT for deployment, first clone the repo, then run `./scripts/deploy.sh <host IP or FQDN>` from the root directory. This script is idempotent and may safely be triggered to run by e.g., a CI/CD server. This will:

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
- `rabbitmq`: RabbitMQ message broker (admin UI at `http://localhost:15672`)
- `celery`: Celery worker
- `sandbox`: sandbox deployment target
- `nginx`: NGINX reverse proxy

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
VUE_APP_CYVERSE_REDIRECT_URL=http://localhost:3000/apis/v1/users/cyverse_handle_temporary_code/
VUE_APP_CYVERSE_CLIENT_ID=some_cyverse_client_id
VUE_APP_CYVERSE_CLIENT_SECRET=some_cyverse_client_secret
NODE_ENV=development
DJANGO_SETTINGS_MODULE=plantit.settings
DJANGO_SECRET_KEY=some_key
DJANGO_DEBUG=True
DJANGO_FIELD_ENCRYPTION_KEY=$field_encryption_key
DJANGO_API_URL=http://plantit/apis/v1/
DJANGO_ALLOWED_HOSTS=*
DJANGO_ADMIN_USERNAME=admin
DJANGO_ADMIN_EMAIL=admin@example.com
DJANGO_ADMIN_PASSWORD=some_password
DJANGO_SECURE_SSL_REDIRECT=False
DJANGO_SESSION_COOKIE_SECURE=False
DJANGO_CSRF_COOKIE_SECURE=False
SQL_ENGINE=django.db.backends.sqlite3
GITHUB_AUTH_URI=https://github.com/login/oauth/authorize
GITHUB_REDIRECT_URI=http://<host>/apis/v1/users/github_handle_temporary_code/
GITHUB_KEY=d15df2f5710e9597290f
GITHUB_SECRET=some_secret
```

Note that `DJANGO_SECRET_KEY`, `DJANGO_FIELD_ENCRYPTION_KEY`, and `SQL_PASSWORD` are given dummy values above. Executing `scripts/bootstrap.sh` in a clean (empty) install directory will generate secure values.

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
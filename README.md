# Requirements

The following must be installed to develop/run `plantit`:

- Unix shell
- Docker
- Python 3
- npm

# Documentation

Full documentation can be found [here](https://computational-plant-science.github.io/DIRT2_Webplatform/build/html/index.html).

# Installation

First, clone the repository:

```bash
git clone git@github.com:Computational-Plant-Science/DIRT2_Webplatform.git
```



## Configure `plantit` for development

To set up a `plantit` development environment, you'll need to:

1. configure environment variables with `.env`; then
2. bootstrap with `dev/bootstrap.sh`.

### Configure environment variables

Docker reads environment variables in the following format from a file named `.env` in the `plantit` root directory:

```
key=value
key=value
...
```

Here is a sample `.env` file containing all variables required to develop `plantit`:

```
VUE_APP_TITLE=plantit
NODE_ENV=development
DJANGO_SETTINGS_MODULE=plantit.settings
DJANGO_SECRET_KEY=<your DJANGO_SECRET_KEY>
DJANGO_DEBUG=True
DJANGO_FIELD_ENCRYPTION_KEY=<your DJANGO_FIELD_ENCRYPTION_KEY
DJANGO_API_URL=http://localhost/apis/v1/
DJANGO_ALLOWED_HOSTS=*
SQL_ENGINE=django.db.backends.postgresql
SQL_HOST=postgres
SQL_PORT=5432
SQL_NAME=postgres
SQL_USER=postgres
SQL_PASSWORD=<your SQL_PASSWORD>
```

Django keys can be generated in any Python 3 environment:

```python
# DJANGO_SECRET_KEY
import random
print("DJANGO_SECRET_KEY: %s" % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))

# DJANGO_FIELD_ENCRYPTION_KEY
import cryptography.fernet
print("DJANGO_FIELD_ENCRYPTION_KEY: %s" % cryptography.fernet.Fernet.generate_key())
```

### Bootstrap `plantit`

Before running the project, execute `dev/bootstrap.sh` from the root directory. This script initializes (and can also be used to restore) the repository to a fresh state by:

- Stopping and removing containers and networks
- Removing Django migrations and stored files
- Rebuilding containers
- Running Django migrations
- Creating a Django admin user with `/django/files` permissions
- Configuring a mock IRODS server and cluster
- Building the Vue front end

### Run `plantit`

Run `plantit` from the repository root with:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This will build and start a number of containers.

- `djangoapp`: Django web application (`http://localhost:80`)
- `celery`: Celery worker
- `rabbitmq`: RabbitMQ message broker
- `postgres`: PostgreSQL database
- `flower`: Celery monitoring UI (`http://localhost:5555`)
- `adminer`: PostgreSQL admin UI (`http://localhost:8080`)
- `irods`: mock IRODS server
- `ssh`: mock SSH connection (e.g., to cluster)

To bypass CAS login and log directly into Django as superuser, browse to `http://localhost/accounts/login/` and enter username `admin` and password `admin` (superuser access is configured in `dev/setup_defaults.py`).

The default Django interface is at `http://localhost/admin/`.

### Vue UI

Front-end code lives in `django/front_end`. It can be built from that directory with `npm run build` (or instructed to rebuild whenever a change is detected with `npm run watch`).

## Configure `plantit` for production

`plantit` runs somewhat differently in production:

- Django runs behind Gunicorn, which sits behind NGINX
- NGINX serves static assets and acts as a reverse proxy
- Postgres stores data in a persistent volume
- Graylog consumes and stores application logs
- Google Analytics are enabled by [`vue-analytics`](https://github.com/MatteoGabriele/vue-analytics)
- [Sentry](https://sentry.io/welcome/) provides Vue monitoring and error tracking

### Configure environment variables

In addition to the environment variables listed for development, the following are required to run `plantit` in production:

- `VUE_APP_ANALYTICS_ID`: provided by Google Analytics
- `VUE_APP_SENTRY_IO_KEY`: provided by Sentry
- `VUE_APP_SENTRY_IO_PROJECT`: provided by Sentry
- `GRAYLOG_PASSWORD_SECRET`: you provide (at least 16 characters)
- `GRAYLOG_ROOT_PASSWORD_SHA2`: see below
- `GRAYLOG_HTTP_EXTERNAL_URI`: location of the Graylog REST API (`<host>:9000`)

Once you have chosen a password for the Graylog admin user (note that this is *not* the same as `GRAYLOG_PASSWORD_SECRET`), `GRAYLOG_ROOT_PASSWORD_SHA2` can be generated with the following:

```bash
echo -n "Enter Password: " && head -1 </dev/stdin | tr -d '\n' | sha256sum | cut -d" " -f1
```

Note also that `NODE_ENV` should be set to `production`, `DJANGO_DEBUG` to `False`, and `DJANGO_API_URL` to `http://<host>/apis/v1/`.

### Configure NGINX

Set `server_name` in `config/ngnix/conf.d/local.conf` to match the host's IP or FQDN (when set to `localhost`, NGINX will refuse to serve non-local clients).

### Suggested build procedure

First, build the Vue UI with `npm run build` from the `django/front_end` directory. Then build containers:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
```

Collect static files so NGINX can serve them:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run djangoapp ./manage.py collectstatic --no-input
```

Run database migrations:

```bash
find . -path "./django/**/migrations/*.py" -not -name "__init__.py" -delete
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run djangoapp /code/dev/wait-for-postgres.sh postgres ./manage.py makemigrations
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run djangoapp ./manage.py migrate
```

Configure Django superuser:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run djangoapp ./manage.py createsuperuser
```

Run `plantit` in production mode:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

This will start the following containers:

- `djangoapp`: Django web application (`http://<host>:80`)
- `celery`: Celery worker
- `rabbitmq`: RabbitMQ message broker
- `postgres`: PostgreSQL database
- `nginx`: NGINX server
- `graylog`: Graylog server (`http://<host>:9000`)
- `mongo`: MongoDB database (for Graylog)
- `elasticsearch`: Elasticsearch node (for Graylog)

## Shared steps

You'll want to do the following no matter whether you're configuring a development environment or production deployment.

### Install workflows
Workflows created with the [Plant IT workflow template](https://github.com/Computational-Plant-Science/cookiecutter_PlantIT) can be plugged into the web platform by placing workflow repositories in the `django/workflows` directory.

Note that the `djangoapp` and `celery` containers must be restarted to load newly added workflows:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart djangoapp
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart celery
```

Note also that the workflow directory name must be identical to the `app_name` configured when the workflow was created (this can also be edited later in the `WORKFLOW_CONFIG` dictionary in `workflow.py`.

### Configure clusters

See [ClusterSide README](https://github.com/Computational-Plant-Science/DIRT2_ClusterSide) for information
on installation and configuration of required remote Plant IT code on cluster.

Clusters are added via the admin interface `(/admin/)`. Choose Clusters->Add Cluster. Fill in the commands
accordingly.

Typically, the submit commands will include `clusterside submit`. They may also include loading packages necessary to run clusterside, for example, loading python3.

For Sapelo2 (UGA's cluster), the submit command is:

```bash
ml Python/3.6.4-foss-2018a; /home/cotter/.local/bin/clusterside submit
```

Note that on some types of ssh connections, installation does not put clusterside in the path. If the cluster throwing a "clusterside not found" error when submitting jobs. Try using the whole path of clusterside for submitting. This can be found by logging in to the cluster as the user PlantIT uses to submit the jobs and executing which clusterside

#### Cluster login configuration

Plant IT supports both ssh password and public-key based
login. To use public-key login, leave the Password field blank. Public-key login requires the private key and a known_hosts list to be available. Plant IT expects this data to be in the following two files:

- `config/ssh/id_rsa`: The private key used for login
- `config/ssh/known_hosts`: The known_hosts file.

The easiest way to setup public-key logins is to configure the keys for login from the web server, then copy the configured `id_rsa` and `known_hosts` files from the web server user (typically in `$HOME/.ssh/`) to `config/ssh/`

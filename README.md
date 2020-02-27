# Requirements

The following must be installed to run `plantit`:

- A Unix shell
- [Docker](https://www.docker.com/)

To develop the project, you'll also need:
- Python 3
- [npm](https://www.npmjs.com/get-npm)

# Documentation

Documentation can be found [here](https://computational-plant-science.github.io/DIRT2_Webplatform/build/html/index.html).

# Installation

First, clone the repository:

```bash
git clone git@github.com:Computational-Plant-Science/DIRT2_Webplatform.git
```

### Configure environment variables

`plantit` requires the following environment variables:

```
VUE_APP_TITLE
NODE_ENV
DJANGO_SETTINGS_MODULE
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_FIELD_ENCRYPTION_KEY
DJANGO_API_URL
DJANGO_ALLOWED_HOSTS
SQL_ENGINE
SQL_HOST
SQL_PORT
SQL_NAME
SQL_USER
SQL_PASSWORD
```

In a development environment, Docker will read variables in the following format from a file named `.env` in the `plantit` root directory:

```
key=value
key=value
...
```

Here is a sample `.env` file:

```
VUE_APP_TITLE=plantit
NODE_ENV=development
DJANGO_SETTINGS_MODULE=plantit.settings
DJANGO_SECRET_KEY=<your DJANGO_SECRET_KEY>
DJANGO_DEBUG=True
DJANGO_FIELD_ENCRYPTION_KEY=<your DJANGO_FIELD_ENCRYPTION_KEY
DJANGO_API_URL=http://djangoapp/apis/v1/
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

### Configure an object store

`plantit` looks for object storage configurations in `django/filesystems.py`. The development environment includes a mock IRODS server. To plug it in, create `django/filesystems.py` and add:

```python
from plantit.file_manager.filesystems.irods import IRODS
from plantit.file_manager.filesystems import registrar

registrar.register(IRODS(name = "irods",
                         username = "rods",
                         password = "rods",
                         port = 1247,
                         hostname = "irods",
                         zone = "tempZone"),
                    lambda user: "/tempZone/home/rods/")
```

### Run `plantit` in development mode

Before running the project, execute `dev/reset.sh` from the root directory. This script restores the repository to a fresh state by:

   - stopping and removing containers and networks
   - removing Django migrations and stored files
   - rebuilding containers
   - running Django migrations
   - creating a Django admin user with `/django/files` permissions
   - configuring a mock IRODS server
   - building the Vue front end

You should now be able to run `plantit` from the repository root:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

This will build and start a number of containers. Some are shared between development and production configurations:

- `djangoapp`: Django web application at `http://localhost:8000`
- `celery`: Celery worker
- `rabbitmq`: RabbitMQ message broker
- `postgres`: PostgreSQL database

Some run only in development mode:

- `flower`: Celery monitoring UI at `http://localhost:5555`
- `adminer`: PostgreSQL admin UI at `http://localhost:8080`
- `irods`: mock IRODS server
- `ssh`: mock SSH connection (e.g., to cluster)

To bypass CAS login and log directly into Django, browse to `http://localhost/accounts/login/` and enter username `admin` and password `admin`.

The default Django interface is at `http://localhost/admin/`.

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

#### Cluster ssh login configuration.
Plant IT supports both ssh password and public-key based
login. To use public-key login, leave the Password field blank. Public-key login requires the private key and a known_hosts list to be available. Plant IT expects this data to be in the following two files:

- `config/ssh/id_rsa`: The private key used for login
- `config/ssh/known_hosts`: The known_hosts file.

The easiest way to setup public-key logins is to configure the keys for login from the web server, then copy the configured `id_rsa` and `known_hosts` files from the web server user (typically in `$HOME/.ssh/`) to `config/ssh/`

### Develop with Vue

Front-end code lives in `django/front_end`. It can be built from that directory with `npm run build` (or instructed to rebuild whenever a change is detected with `npm run watch`).

When in django's development mode, django will automatically load the new front_end after running `npm run build` or `npm run watch`.

See README-PRODUCTION.md for information on building the front end for production use.

### Run `plantit` in production
The website can be run in production mode using a different docker-compose config:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

This will start the shared containers (listed above), as well as:

- `nginx`: NGINX server
- `graylog`: Graylog server
- `mongo`: MongoDB database (for Graylog)
- `elasticsearch`: Elasticsearch node (for Graylog)

The production configuration:
- Uses gunicorn for WSGI to Django
- Saves PostgreSQL database files to a persistent volume
- Configures Graylog logging

For more info on setting up the production enviroment, see `README-PRODUCTION.md`.


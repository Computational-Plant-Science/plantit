# Requirements

The following are required to run `DIRT2_Webplatform`:

- A Unix shell
- [Docker](https://www.docker.com/)
- [npm](https://www.npmjs.com/get-npm)
- Python 3

# Documentation

Full documentation can be found [here](https://computational-plant-science.github.io/DIRT2_Webplatform/build/html/index.html).

# Installation

First, clone the repository:

```bash
git clone git@github.com:Computational-Plant-Science/DIRT2_Webplatform.git
```

## Development

To set up a new (or restore a clean) development environment, run `dev/bootstrap.dev.sh` from the project root (you may need to use `chmod +x` first). This will:

- Stop and remove project containers and networks
- If an `.env` file (to configure environment variables) does not exist, generate one with default values
- Remove migrations and stored files
- Rebuild containers
- Run migrations
- Create a Django superuser (username `admin`, password `admin`)
- Configure a mock IRODS server and cluster
- Build the Vue front end

Then bring the project up with `docker-compose -f docker-compose.yml -f docker-compose.dev.yml up`.

This will start a number of containers:

- `plantit`: Django web application (`http://localhost:80`)
- `celery`: Celery worker
- `rabbitmq`: RabbitMQ message broker
- `postgres`: PostgreSQL database
- `flower`: Celery monitoring UI (`http://localhost:5555`)
- `adminer`: PostgreSQL admin UI (`http://localhost:8080`)
- `irods`: mock IRODS server
- `ssh`: mock SSH connection (e.g., to cluster)

To bypass CAS login and log directly into Django as superuser, browse to `http://localhost/accounts/login/` and enter username `admin` and password `admin`.

The default Django interface is at `http://localhost/admin/`.

### Environment variables

In a development environment, Docker reads environment variables in the following format from a file named `.env` in the `DIRT2_Webplatform` root directory:

```
key=value
key=value
...
```

`bootstrap.dev.sh` will generate an `.env` file like the following if one does not exist:

```
VUE_APP_TITLE=plantit
NODE_ENV=development
DJANGO_SETTINGS_MODULE=plantit.settings
DJANGO_SECRET_KEY=some_secret_key
DJANGO_DEBUG=True
DJANGO_FIELD_ENCRYPTION_KEY=some_encryption_key
DJANGO_API_URL=http://localhost/apis/v1/
DJANGO_ALLOWED_HOSTS=*
SQL_ENGINE=django.db.backends.postgresql
SQL_HOST=postgres
SQL_PORT=5432
SQL_NAME=postgres
SQL_USER=postgres
SQL_PASSWORD=some_password
```

You can generate Django keys with:

```python
import random
print("DJANGO_SECRET_KEY: %s" % ''.join(random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))

import cryptography.fernet
print("DJANGO_FIELD_ENCRYPTION_KEY: %s" % cryptography.fernet.Fernet.generate_key())
```

## Production

The production configuration is somewhat different:

- Django runs behind Gunicorn which runs behind NGINX
- NGINX serves static assets and acts as a reverse proxy
- Postgres stores data in a persistent volume
- Graylog consumes and stores container logs
- Google Analytics are enabled via [`vue-analytics`](https://github.com/MatteoGabriele/vue-analytics)
- [Sentry](https://sentry.io/welcome/) provides Vue monitoring and error tracking

Before running `DIRT2_Webplatform` in production, you must:

1) Configure production-specific environment variables
2) Build the Vue front end
3) Collect static files and configure NGINX to serve them
4) Run migrations
5) Create a Django superuser, if one does not exist
6) If deploying for the first time, Graylog must be configured to consume input from other containers once they have all been brought up

Executing `dev/bootstrap.prod.sh` from the project root will run steps 2-5.

### Environment variables

In addition to the environment variables listed for development, the following are required to run `DIRT2_Webplatform` in production:

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

Note also that `NODE_ENV` should be set to `production`, `DJANGO_DEBUG` to `False`, `DJANGO_API_URL` should point to the host's IP or FQDN, and various key/password/secret fields should be configured appropriately.

### Vue

Front-end code lives in `plantit/front_end`. It can be built from that directory with `npm run build`.

#### Static files

Static files can be collected with:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run plantit ./manage.py collectstatic --no-input
```

### Configure NGINX

Set `server_name` in `config/ngnix/conf.d/local.conf` to match the host's IP or FQDN, and make sure NGINX knows where to find the files to serve:

```
location /assets/ {
  alias /opt/plantit/static/;
}

location /public/ {
  alias /opt/plantit/public/;
}
```

### Run migrations

Run migrations with:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run plantit /code/dev/wait-for-postgres.sh postgres ./manage.py makemigrations
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run plantit ./manage.py migrate
```

### Create superuser

Create a superuser (substitute your own values for username, password, and email address):

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run plantit /code/dev/create-django-superuser.sh -u "<username>" -p "<password>" -e "<email address>"
```

### Running in production

Containers can be brought up with:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

This will start the following:

- `plantit`: Django web application (`http://<host>:80`)
- `celery`: Celery worker
- `rabbitmq`: RabbitMQ message broker
- `postgres`: PostgreSQL database
- `nginx`: NGINX server
- `graylog`: Graylog server (`http://<host>:9000`)
- `mongo`: MongoDB database (for Graylog)
- `elasticsearch`: Elasticsearch node (for Graylog)

## Workflows

Workflows created with the [Plant IT workflow template](https://github.com/Computational-Plant-Science/cookiecutter_PlantIT) can be plugged into the web platform by placing workflow repositories in the `django/workflows` directory.

Note that the `plantit` and `celery` containers must be restarted to reload workflows:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart plantit
docker-compose -f docker-compose.yml -f docker-compose.dev.yml restart celery
```

Note also that the workflow directory name must be identical to the `app_name` configured when the workflow was created (this can also be edited later in the `WORKFLOW_CONFIG` dictionary in `workflow.py`.

## Clusters

See [ClusterSide README](https://github.com/Computational-Plant-Science/DIRT2_ClusterSide) for information on installation and configuration of required remote Plant IT code on cluster.

Clusters are added via the admin interface `(/admin/)`. Choose Clusters->Add Cluster. Fill in the commands
accordingly.

Typically, the submit commands will include `clusterside submit`. They may also include loading packages necessary to run clusterside, for example, loading python3.

For Sapelo2 (UGA's cluster), the submit command is:

```bash
ml Python/3.6.4-foss-2018a; /home/cotter/.local/bin/clusterside submit
```

Note that on some types of ssh connections, installation does not put DIRT2_Clusterside in the path. If the cluster throwing a "clusterside not found" error when submitting jobs. Try using the whole path of clusterside for submitting. This can be found by logging in to the cluster as the user PlantIT uses to submit the jobs and executing which clusterside

#### Cluster login configuration

Plant IT supports both ssh password and public-key based
login. To use public-key login, leave the Password field blank. Public-key login requires the private key and a known_hosts list to be available. Plant IT expects this data to be in the following two files:

- `config/ssh/id_rsa`: The private key used for login
- `config/ssh/known_hosts`: The known_hosts file.

The easiest way to setup public-key logins is to configure the keys for login from the web server, then copy the configured `id_rsa` and `known_hosts` files from the web server user (typically in `$HOME/.ssh/`) to `config/ssh/`

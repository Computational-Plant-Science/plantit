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

Then run `dev/reset.sh` from the root directory. This script restores the repository to a fresh state by:

   - stopping and removing containers and networks
   - removing Django migrations and stored files
   - rebuilding containers
   - running Django migrations
   - creating a Django admin user with `/django/files` permissions
   - configuring a mock IRODS server
   - building the Vue front end

Run `plantit` from the repository root:

```bash
docker-compose -f docker-compose.yml -f compose-dev.yml up
```

This will build and start the following containers:

- `djangoapp`: Django web application at `http://localhost:80`
- `celery`: Celery worker
- `flower`: Celery monitoring UI at `http://localhost:5555`
- `rabbitmq`: RabbitMQ message broker
- `db-dev`: PostgreSQL database
- `adminer`: Database admin UI at `http://localhost:8081`

To bypass CAS login and log directly into Django: `http://localhost/accounts/login/` with `username: admin` and `password: admin`.

The default Django interface is at `http://localhost/admin/`.

### Object storage

`plantit` looks for storage configurations in `django/filesystems.py`. The development environment includes a mock IRODS server. To plug it in, create `django/filesystems.py` and add:

```
from plantit.file_manager.filesystems.irods import IRods
from plantit.file_manager.filesystems import registrar

registrar.register(IRODS(name = "irods",
                         username = "rods",
                         password = "rods",
                         port = 1247,
                         hostname = "irods",
                         zone = "tempZone"),
                    lambda user: "/tempZone/home/rods/")
```  

If you edit this file while `plantit` is running, restart `djangoapp` and `celery` with:

```
docker-compose -f docker-compose.yml -f compose-dev.yml restart djangoapp
docker-compose -f docker-compose.yml -f compose-dev.yml restart celery
```

### Configuration

`plantit` requires the following environment variables:

```
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_FIELD_ENCRYPTION_KEY
DJANGO_API_URL
DJANGO_ALLOWED_HOSTS
POSTGRES_USER
POSTGRES_NAME
POSTGRES_HOST
POSTGRES_PASSWORD
```

In a development environment, Docker will read variables in the following format from a file named `.env` in the `plantit` root directory:

```
DJANGO_SECRET_KEY=value
DJANGO_DEBUG=value
...
```

### Installing Workflows
Workflows created using the [Plant IT workflow template](https://github.com/Computational-Plant-Science/cookiecutter_PlantIT) can be integrated into the web platform by cloning the repository (or copying the code) into the django/workflows directory.

The web server and celery processes must be restarted to load new workflows.

#### Workflow install example:
```
  cd django/workflows/
  git clone git@github.com:Computational-Plant-Science/DIRT2D_Workflow.git dirt2d #<- see note below
```

__NOTE:__ The workflow folder name (inside django/workflows/) must be the same
as the workflow app_name set in the workflow's WORKFLOW_CONFIG.

### Adding Clusters

#### Installation
See [ClusterSide README](https://github.com/Computational-Plant-Science/DIRT2_ClusterSide) for information
on installation and configuration of required remote Plant IT code on cluster

#### Adding Cluster to Plant IT backend.
Clusters are added via the admin interface `(/admin/)`. Choose Clusters->Add Cluster. Fill in the commands
accordingly.

Typically, the submit commands will include `clusterside submit`. They may also include loading packages necessary to run clusterside, for example, loading python3.

For Sapelo2 (UGA's cluster), the submit command is:

```
ml Python/3.6.4-foss-2018a; /home/cotter/.local/bin/clusterside submit
```

##### Note:
On some types of ssh connections, installation does not put clusterside in the path. If the cluster throwing a "clusterside not found" error when submitting jobs. Try using the whole path of clusterside for submitting. This can be found by logging in to the cluster as the user PlantIT uses to submit the jobs and executing which clusterside

#### Cluster ssh login configuration.
Plant IT supports both ssh password and public-key based
login. To use public-key login, leave the Password field blank. Public-key login requires the private key and a known_hosts list to be available. Plant IT expects this data to be in the following two files:

- `config/ssh/id_rsa`: The private key used for login
- `config/ssh/known_hosts`: The known_hosts file.

The easiest way to setup public-key logins is to configure the keys for login from the web server, then copy the configured `id_rsa` and `known_hosts` files from the web server user (typically in `$HOME/.ssh/`) to `config/ssh/`

# Front End Code
The front end code is in django/front_end. It is built atop Vue.js. In development mode, it can be built using:

```
cd django/front_end
npm run build
```

Or to continually watch for changes and rebuild as needed:

```
cd django/front_end
npm run watch
```

When in django's development mode, django will automatically load the new front_end after running `npm run build` or `npm run watch`.

See README-PRODUCTION.md for information on building the front end for production use.

# Production
The website can be run in production mode using a different docker-compose config:

```bash
docker-compose -f docker-compose.yml -f compose-prod.yml up
```

The production configuration:
- Uses the nginx web server and gunicorn for wsgi to django
- Saves the database files outside the docker container.

For more info on setting up the production enviroment, see README-PRODUCTION.md

__NOTE:__ Production environments and dev environments use different
containers for the database server. This will cause problems if you try to
to run both environments on the same code base. The django database migrations will not be synced. See README-PRODUCTION.md for more details.

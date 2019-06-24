# Requirements

The following must be installed to run PlantIT:

* [Docker](https://www.docker.com/)
* [npm](https://www.npmjs.com/get-npm)
* Python 3
* A unix based shell

# Documentation

[Full Documentation](https://computational-plant-science.github.io/DIRT2_Webplatform/build/html/index.html)

# Installation

```bash
git clone git@github.com:Computational-Plant-Science/DIRT2_Webplatform.git
```

The processes are contained within docker containers, the full website can be run using docker-compose from the root of the repository:

```bash
dev/reset.sh #Initialize databases, builds front end, and some other default values

docker-compose -f docker-compose.yml -f compose-dev.yml up
```

**ATTENTION:** By default, dev/reset.sh deletes ALL local docker containers and volumes.   

Once the containers have started, the website is available at http://localhost

To bypass CAS login, instead logging directly into django, use: `http://localhost/accounts/login/`

reset.sh adds the __user__: _admin_ with __password:__ _admin_

The default django interface is at http://localhost/admin/


### Adding filesystems
PlantIT looks for file-system configurations in django/filesystems.py. The development environment includes a test irods server in a docker container to use for testing. To add it as a filesystem, create `django/filesystems.py` and add:

__django/filesystems.py__:
```
from plantit.file_manager.filesystems.irods import IRods
from plantit.file_manager.filesystems import registrar

registrar.register(IRods(name = "irods",
                         username = "rods",
                         password = "rods",
                         port = 1247,
                         hostname = "irods",
                         zone = "tempZone"),
                    lambda user: "/tempZone/home/rods/")
```  

The web server and celery process will need to be restarted after adding a new filesystem.

```
docker-compose -f docker-compose.yml -f compose-dev.yml restart djangoapp
docker-compose -f docker-compose.yml -f compose-dev.yml restart celery
```

### Environment specific configuration
If present, PlantIT loads `django/settings.py` as part of django's settings.py file. This can be used for any environment specific configuration that should not be committed to the repository.

Values set in `django/settings.py` override any PlantIT default settings.

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


# Resetting an installation
```bash
dev/reset.sh
```

dev/reset.sh can also be used to resets everything back to a "Fresh" install. Running dev/reset.sh does the following:

   - rebuilds all docker images
   - deletes all docker volumes
   - removes all Django migrations

then it

   - rebuilds the images
   - runs initial Django migration
   - creates an admin user
      - gives admin user file access permissions to ./django/files
   - adds test cluster

**ATTENTION:** By default, dev/reset.sh deletes ALL local docker containers and volumes.   

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

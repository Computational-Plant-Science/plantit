# Installation

Individual workflows are linked to the web platform via git submodules. use `--recursive-submodules` when cloning to download the workflows.

```bash
git clone --recurisve-submodules git@github.com:cottersci/DIRT2_Webplatform.git
```

__The submodules are required for the website to work__. You can learn more
about Git submodules [here](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

The processes are contained within docker containers, the full website can be run using docker-compose from the root of the repository:

```bash
dev/reset.sh #Initialize databases and some other default values
docker-compose -f docker-compose.yml -f compose-dev.yml up
```

reset.sh adds the __user__: _admin_ with __password:__ _admin_

# Installing Workflows
Workflows created using the [Plant IT workflow template](https://github.com/Computational-Plant-Science/cookiecutter_PlantIT) can be integrated into the web platform by cloning the repository (or copying the code) into the django/workflows directory.

The web server must be restarted to load new workflows.

__NOTE:__ The workflow folder name (inside django/workflows/) must be the same
as the workflow app_name set in the workflow's WORKFLOW_CONFIG.

# Resetting an installation
```bash
sudo dev/reset.sh
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

sudo is required to remove files added to ./django/files by the webserver.

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

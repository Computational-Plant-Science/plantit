Server Configuration
====================

Environment Specific Django Settings
-------------------------------------
If present, PlantIT loads `django/settings.py` as part of django's `settings.py`
file. This can be used for any environment specific configuration that should
not be committed to the repository.

Values set in `django/settings.py` override any PlantIT default settings.

.. _configuration-docker:

Docker
-------

Plant IT is packaged within docker containers using
`docker-compose <https://docs.docker.com/compose/>`_. There are two
docker-compose configurations: dev and prod. They share `./docker-compose.yml`
as a common docker-compose configuration file as well as independent
configuration files.

Development (dev)
^^^^^^^^^^^^^^^^^

Configuration file: `./compose-dev.yml`

The development configuration runs django in development mode (debug on,
auto restart on file changes, etc.) and includes docker containers for
a test cluster (`ssh` docker-compose service) and test irods server
(`irods` docker-compose service).

The development environment loads `django/plantit/settings_dev.py` as the
root django settings file.

The development environment can be started using:

.. code-block:: bash

  docker-compose -f docker-compose.yml -f compose-dev.yml up

Production (prod)
^^^^^^^^^^^^^^^^^^^

Configuration file: `./compose-prod.yml`

The production configuration runs django in production mode within, utilizing
`gunicorn <https://gunicorn.org/>`_ as a WSGI HTTP server
and `nginx <https://www.nginx.com/>`_ as the web server.

All logs are configured to be sent to a GELF server via udp at
udp://localhost:12201 (Eg. sent to a `graylog <https://www.graylog.org/>_`
instance).

The production environment loads `django/plantit/settings_prod.py` as the
root django settings file.

The production environment can be started using:

.. code-block:: bash

  docker-compose -f docker-compose.yml -f compose-prod.yml up -d

.. _configuration-filesystems:

Filesystems
------------

Plant IT looks for file-system configurations in `django/filesystems.py`. Since
this file is specific to each Plant IT installation, it is not included in the
git repository. It must be created.

Filesystems that extend
:class:`plantit.file_manager.filesystems.storage.AbstractStorageType` can be
registered with Plant IT within the `filesystems.py` folder as follows:

.. code-block:: python
  :caption: django/filesystems.py

  from plantit.file_manager.filesystems import registrar

  registrar.register(
    #file system instance
  )

Replacing `file system instance` with a instance of a class that extends
:class:`~plantit.file_manager.filesystems.storage.AbstractStorageType`.

.. Attention::
  The web server and celery process will need to be restarted
  after adding a new filesystem.

Example
^^^^^^^

The development environment includes a test irods server in a docker container
to use for testing. To add it as a filesystem, create `django/filesystems.py` and add:

.. code-block:: python
  :caption: django/filesystems.py

  from plantit.file_manager.filesystems.irods import IRods
  from plantit.file_manager.filesystems import registrar

  registrar.register(IRods(name = "irods",
                           username = "rods",
                           password = "rods",
                           port = 1247,
                           hostname = "irods",
                           zone = "tempZone"),
                      lambda user: "/tempZone/home/rods/")

the dev systems can then be restarted using:

.. code-block:: bash

  docker-compose -f docker-compose.yml -f compose-dev.yml restart djangoapp
  docker-compose -f docker-compose.yml -f compose-dev.yml restart celery

.. _configuration-installing-workflows:

Installing Workflows
---------------------
Workflows created using the
`Plant IT workflow template <https://github.com/Computational-Plant-Science/cookiecutter_PlantIT>`_
can be integrated into the web platform by cloning the repository
(or copying the code) into the `django/workflows` directory.

.. Attention::
  The web server and celery processes must be restarted to load new workflows.
  If running the website in production mode, collectstatic will also need
  to be rerun after the restart to collect any new workflow icons.

Once restarted, the Plant IT server will automatically find and register
the new workflow.

.. Note::
  Some assertions are checked on loading the workflows, if these assertions
  fail, the web server will not start. Check the logs for deatails of what
  assertion failed.

Example
^^^^^^^^
  .. code-block:: bash

    cd django/workflows/
    git clone git@github.com:Computational-Plant-Science/DIRT2D_Workflow.git dirt2d #<- see note below

.. Note::
  The workflow folder name (inside django/workflows/) must be the same as the
  workflow app_name set in the workflow's WORKFLOW_CONFIG.

Adding Clusters
----------------

Installing Plant IT Cluster-side Code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See `ClusterSide README <https://github.com/Computational-Plant-Science/DIRT2_ClusterSide>`_
for information on installation and configuration of required remote Plant IT code on cluster.

Adding Cluster to Plant IT backend.
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Clusters are added via the admin interface (/admin/).
Choose Clusters->Add Cluster. Fill in the commands accordingly.

Typically, the submit commands will include clusterside submit.
They may also include loading packages necessary to run clusterside,
for example, loading python3.

For Sapelo2 (UGA's cluster), the submit command is:

.. code-block:: bash

  ml Python/3.6.4-foss-2018a; /home/cotter/.local/bin/clusterside submit

.. Note::
  On some types of ssh connections, installation does not put clusterside in the
  path. If the cluster throwing a "clusterside not found" error when submitting
  jobs. Try using the whole path of clusterside for submitting.
  This can be found by logging in to the cluster as the user PlantIT uses
  to submit the jobs and executing `which clusterside`

.. _configuration-clusters-ssh-config:

Cluster ssh login configuration.
"""""""""""""""""""""""""""""""""

Plant IT supports both ssh password and public-key based login.
To use public-key login, leave the Password field blank.
Public-key login requires the private key and a known_hosts list to be
available. Plant IT expects this data to be in the following two files:

- `config/ssh/id_rsa`: The private key used for login
- `config/ssh/known_hosts`: The known_hosts file.

The easiest way to setup public-key logins is to configure the keys for
login from the web server, then copy the configured id_rsa and known_hosts
files from the web server user (typically in `$HOME/.ssh/`) to `config/ssh/`

'''
    Workflows are modular code provided by 3rd parties to analyze
    samples within collections. Plant IT automatically
    applies the workflow's analysis code to all samples withing a collection.

    See https://plant-it-workflows.readthedocs.io/en/latest/ for more details
    on creating workflows.

    Workflows created using the Plant IT workflow cookiecutter template can be
    integrated into the web platform by cloning the repository (
    or copying the code) into the django/workflows directory.

    On initialization of django, plant it automatically initializes an instance
    of the workflow registrar (:class:`plantit.workflows.Registrar`) at
    :attr:`plantit.workflows.registrar` and searches attempts to register
    each folder in `django/workflows` as a Plant IT workflow. Assert checks
    are performed for typical workflow errors. These asserts will stop
    the web server from starting correctly if they fail.

    Autoinitilization code can be found in `plantit.workflows.__init__.py`

    Once automatically registered, workflows are ready to be used within Plant IT.

    Note:
        The web server and celery processes must be restarted to load
        new workflows.

    **Workflow Install Example:**

    .. code-block:: bash

        cd django/workflows/
        git clone git@github.com:Computational-Plant-Science/DIRT2D_Workflow.git dirt2d #<- see note below

    Note:
        The workflow folder name (inside django/workflows/) must be the same
        as the workflow app_name set in the workflow's WORKFLOW_CONFIG.

'''
from os import listdir
from os.path import isdir, isfile, join
from shutil import copyfile
from django.conf import settings
import importlib

class Registrar():
    """
        Workflows are register with the server via this class.

        Registration is automatically performed for workflows in `django/workflows`

        Manual registration is not recommended or supported.

        An instance of this class is automatically created by Plant IT
        at :attr:`plantit.workflows.registrar`. You should not need to use
        the :class:`plantit.workflows.Registrar` class directly.
    """
    list = {}

    def register(self,config):
        """
            Register a workflow with the server

            **Icons:**

            If a workflow icon exists at <workflow_folder>/static/icon.png, it
            will be copied to plantit/static/workflow_icons to be accessed
            by the front end.

            Icons must be 200x200 pixels.

            Args:
                config (dict): The workflow configuration, containing:
                    name (str): Human readable name of the workflow
                    description (str): Workflow description, up to 250
                            characters
                    app_name (str): name of app, as registed with django
                            settings.py
                    singulairty_url (str): url to the workflow
                            singularity container
                    api_version (float): api version to use
        """
        config['app_url_pattern'] = "workflows:%s:analyze" % (config['app_name'],)

        icon_path = join(folder_path,'static','icon.png')
        if(isfile(icon_path)):
            copyfile(icon_path,'plantit/static/workflow_icons/' + config['app_name'] + '.png')
            config['icon_url'] = '/assets/workflow_icons/' + config['app_name'] + '.png'

        self.list[config['app_name']] = config

registrar = Registrar()

basepath = settings.WORKFLOW_DIR
folders = [f for f in listdir(basepath) if isdir(join(basepath,f))]

for folder in folders:
    if folder == "__pycache__":
        continue

    folder_path = join(basepath,folder)
    files = [f for f in listdir(folder_path) if isfile(join(folder_path,f))]

    assert "process.py" in files, "No process.py file in workflow %s"%(folder_path)
    assert "workflow.py" in files, "No workflow.py file in workflow %s"%(folder_path)
    assert "__init__.py" in files, "Workflow folder must be a module, add __init__.py to %s" % (folder)

    WORKFLOW_CONFIG = importlib.import_module('workflows.' + folder + '.workflow',
                                            package=None).WORKFLOW_CONFIG

    assert WORKFLOW_CONFIG['app_name'] == folder, ("Workflow folder name (\"%s\")"
        " must be the same as the workflow app name (\"%s\"). "
        "Change folder name to \"%s\"") % (WORKFLOW_CONFIG['app_name'],folder, WORKFLOW_CONFIG['app_name'])

    registrar.register(WORKFLOW_CONFIG)

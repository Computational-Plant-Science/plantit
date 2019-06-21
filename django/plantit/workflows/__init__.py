from os import listdir
from os.path import isdir, isfile, join
from shutil import copyfile
import importlib
import logging

class Registrar():
    """
        Workflows are register with the server via this class.

        It is recommended that the registration is performed in the admin.py
        file of the workflow.

        Example:
            admin.py:
                from workflows import registrar

                admin.site.register(Defaults)

                name = "DIRT"
                description = "Up to 250 character description"
                icon_loc = "workflows/dirt2d/static/icon.png"
                registrar.register(name,description,"dirt2d",icon_loc)
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
        else:
            logger = logging.getLogger("plantit")
            logger.warning("No workflow icon found for workflow \"%s\" at path \"%s\""%(config['app_name'],icon_path))

        self.list[config['app_name']] = config

registrar = Registrar()

basepath = "./workflows/"
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

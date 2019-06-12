from os import listdir
from os.path import isdir, isfile, join
import importlib

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

            Args:
                config (dict): The workflow configuration, containing:
                    name (str): Human readable name of the workflow
                    description (str): Workflow description, up to 250
                            characters
                    app_name (str): name of app, as registed with django
                            settings.py
                    icon (str): path to workflow icon, relative to STATIC_ROOT.
                            icon size should be 200x200px
                    singulairty_url (str): url to the workflow
                            singularity container
                    api_versin (float): api version to use

            Attention:
                the icon path must be within a folder available to the
                STATIC_ROOT. Suggest placing the icon in the workflow app's
                static folder: django/workflows/[workflow_app_name]/static/workflows/[workflow_app_name]/icon.png
                then the icon path would be: workflows/[workflow_app_name]/icon.png

        """
        config['app_url_pattern'] = "workflows:%s:analyze" % (config['app_name'],)

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

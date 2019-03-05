class Registrar():
    """
        Workflows are registed with the server via this classs.

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

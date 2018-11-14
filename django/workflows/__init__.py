class Registrar():
    list = {}

    def register(self,name,description,app_name):
        app_url_pattern = "workflows:%s:analyze" % (app_name,)
        self.list[name] = {"description": description,
                           "app_url_pattern": app_url_pattern}

registrar = Registrar()

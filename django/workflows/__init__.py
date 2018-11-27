class Registrar():
    list = {}

    def register(self,name,description,app_name):
        app_url_pattern = "workflows:%s:analyze" % (app_name,)
        self.list[name] = {"description": description,
                           "app_url_pattern": app_url_pattern}

registrar = Registrar()

description = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Aenean blandit, nisl eget varius porta, enim libero lacinia libero, bibendum accumsan neque enim eget ligula. Vestibulum eleifend suscipit sapien vel condimentum. Vivamus laoreet ullamcorper rhoncus. Integer massa lorem, ultricies id neque."
registrar.register("Fake1",description,"dirt2d")
registrar.register("Fake2",description,"dirt2d")
registrar.register("Fake3",description,"dirt2d")
registrar.register("Fake4",description,"dirt2d")

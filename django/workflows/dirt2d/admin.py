from django.contrib import admin
from .models import Defaults
from workflows import registrar

admin.site.register(Defaults)

name = "DIRT"
description = "Digital imaging of root traits (DIRT) measures traits of monocot and dicot roots from digital images. DIRT automates the extraction of root traits by making high-throughput grid computing environment available to end-users without technical training."
icon_loc = "workflows/dirt2d/icon.png"
registrar.register(name,description,"dirt2d",icon_loc)

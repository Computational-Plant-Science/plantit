from django.contrib import admin
from .permissions import Permissions, Location
from .filesystems import local, irods

admin.site.register(Permissions)
admin.site.register(Location)

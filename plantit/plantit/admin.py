from django.contrib import admin

from plantit.resources.models import Resource, ResourceAccessPolicy
from plantit.datasets.models import DatasetAccessPolicy, DatasetSession


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    pass


@admin.register(ResourceAccessPolicy)
class ResourceAccessPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(DatasetAccessPolicy)
class DatasetAccessPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(DatasetSession)
class SessionAdmin(admin.ModelAdmin):
    pass

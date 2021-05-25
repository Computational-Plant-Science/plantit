from django.contrib import admin

from plantit.agents.models import Agent, AgentAccessPolicy
from plantit.datasets.models import DatasetAccessPolicy, DatasetSession


@admin.register(Agent)
class ResourceAdmin(admin.ModelAdmin):
    pass


@admin.register(AgentAccessPolicy)
class ResourceAccessPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(DatasetAccessPolicy)
class DatasetAccessPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(DatasetSession)
class SessionAdmin(admin.ModelAdmin):
    pass

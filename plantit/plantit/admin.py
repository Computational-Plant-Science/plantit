from django.contrib import admin

from plantit.agents.models import Agent, AgentAccessPolicy
from plantit.datasets.models import DatasetAccessPolicy, DatasetSession
from plantit.feedback.models import Feedback
from plantit.workflows.models import Workflow


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    pass


@admin.register(AgentAccessPolicy)
class AgentAccessPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(DatasetAccessPolicy)
class DatasetAccessPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(DatasetSession)
class DatasetSessionAdmin(admin.ModelAdmin):
    pass


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    pass


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    pass

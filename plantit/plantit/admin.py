from django.contrib import admin

from plantit.agents.models import Agent, AgentAccessPolicy
from plantit.datasets.models import DatasetAccessPolicy, DatasetSession
from plantit.feedback.models import Feedback
from plantit.miappe.models import Investigation, Study


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


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    pass


# MIAPPE types

@admin.register(Investigation)
class InvestigationAdmin(admin.ModelAdmin):
    pass


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    pass

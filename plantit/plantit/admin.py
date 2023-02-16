from django.contrib import admin

from plantit.users.models import Contributor, Profile, Migration
from plantit.misc.models import NewsUpdate, MaintenanceWindow, FeaturedWorkflow
from plantit.agents.models import Agent, AgentAccessPolicy
from plantit.datasets.models import DatasetAccessPolicy
from plantit.feedback.models import Feedback
from plantit.miappe.models import Investigation, Study


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(Contributor)
class ContributorAdmin(admin.ModelAdmin):
    pass


@admin.register(Migration)
class MigrationAdmin(admin.ModelAdmin):
    pass


@admin.register(NewsUpdate)
class NewsUpdateAdmin(admin.ModelAdmin):
    pass


@admin.register(MaintenanceWindow)
class MaintenanceWindowAdmin(admin.ModelAdmin):
    pass


@admin.register(FeaturedWorkflow)
class FeaturedWorkflowAdmin(admin.ModelAdmin):
    pass


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    pass


@admin.register(AgentAccessPolicy)
class AgentAccessPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(DatasetAccessPolicy)
class DatasetAccessPolicyAdmin(admin.ModelAdmin):
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

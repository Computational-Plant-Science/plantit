from django.contrib import admin

from plantit.clusters.models import Cluster, ClusterAccessPolicy
from plantit.collections.models import CollectionAccessPolicy
from plantit.sessions.models import Session


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    pass


@admin.register(ClusterAccessPolicy)
class ClusterAccessPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(CollectionAccessPolicy)
class CollectionAccessPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    pass

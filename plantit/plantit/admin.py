from django.contrib import admin

from plantit.clusters.models import Cluster, ClusterAccessPolicy
from plantit.collections.models import CollectionAccessPolicy, CollectionSession


@admin.register(Cluster)
class ClusterAdmin(admin.ModelAdmin):
    pass


@admin.register(ClusterAccessPolicy)
class ClusterAccessPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(CollectionAccessPolicy)
class CollectionAccessPolicyAdmin(admin.ModelAdmin):
    pass


@admin.register(CollectionSession)
class SessionAdmin(admin.ModelAdmin):
    pass

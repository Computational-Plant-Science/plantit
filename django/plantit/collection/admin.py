from django.contrib import admin
from .models import Collection, Sample

class SampleInline(admin.StackedInline):
    model = Sample
    extra = 0

class CollectionAdmin(admin.ModelAdmin):
    model = Collection
    inlines = [
        SampleInline
    ]

admin.site.register(Collection,CollectionAdmin)

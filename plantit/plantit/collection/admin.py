from django.contrib import admin
from .models import Collection


class CollectionAdmin(admin.ModelAdmin):
    model = Collection


admin.site.register(Collection, CollectionAdmin)

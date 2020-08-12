from django.contrib import admin
from .models import Dataset


class CollectionAdmin(admin.ModelAdmin):
    model = Dataset


admin.site.register(Dataset, CollectionAdmin)

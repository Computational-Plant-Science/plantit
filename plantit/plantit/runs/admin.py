from django.contrib import admin
from django.forms import ModelForm, PasswordInput

from .models.cluster import Cluster


class ClusterForm(ModelForm):
    class Meta:
        model = Cluster
        fields = '__all__'
        widgets = {
            'password': PasswordInput(),
        }


class ClusterAdmin(admin.ModelAdmin):
    form = ClusterForm


admin.site.register(Cluster, ClusterAdmin)

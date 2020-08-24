from django.contrib import admin
from django.forms import ModelForm, PasswordInput

from plantit.targets.models import Target


class ClusterForm(ModelForm):
    class Meta:
        model = Target
        fields = '__all__'
        widgets = {
            'password': PasswordInput(),
        }


class ClusterAdmin(admin.ModelAdmin):
    form = ClusterForm


admin.site.register(Target, ClusterAdmin)

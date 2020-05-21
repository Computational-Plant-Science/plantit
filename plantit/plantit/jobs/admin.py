from django.contrib import admin
from django.forms import ModelForm, PasswordInput
from django.utils import timezone

from .models.cluster import Cluster
from .models.job import Job
from .models.status import Status


class StatusInline(admin.StackedInline):
    readonly_fields = ['state', 'date', 'description']
    can_delete = False
    model = Status
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False


class JobAdmin(admin.ModelAdmin):
    readonly_fields = ['token', 'created', 'submission_id']
    inlines = [StatusInline]

    def save_model(self, request, obj, form, change):
        super(JobAdmin, self).save_model(request, obj, form, change)

        if not obj.status_set.all():
            obj.status_set.create(job=obj,
                     state=Status.CREATED,
                     date=timezone.now(),
                     description="Job Created")


class ClusterForm(ModelForm):
    class Meta:
        model = Cluster
        fields = '__all__'
        widgets = {
            'password': PasswordInput(),
        }

class ClusterAdmin(admin.ModelAdmin):
    form = ClusterForm

admin.site.register(Job, JobAdmin)
admin.site.register(Cluster, ClusterAdmin)

from django.contrib import admin
from django import forms

# Register your models here.
from .models import Cluster,Job,Executor,File,Status
from django.utils import timezone
from job_manager import tasks
from django.forms import ModelForm, PasswordInput


class StatusInline(admin.StackedInline):
    readonly_fields = ['state', 'date', 'description']
    can_delete = False
    model = Status
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

class JobAdmin(admin.ModelAdmin):
    readonly_fields = ['auth_token', 'date_created', 'submission_id']
    inlines = [StatusInline]

    def save_model(self, request, obj, form, change):
        super(JobAdmin, self).save_model(request, obj, form, change)

        if(not obj.status_set.all()):
            obj.status_set.create(job=obj,
                     state=Status.CREATED,
                     date=timezone.now(),
                     description="Job Created")

class FileAdmin(admin.ModelAdmin):
    exclude = ("file_name",)
    def save_model(self, request, obj, form, change):
        obj.file_name = str(obj.content)
        obj.save()

class ClusterForm(ModelForm):
    class Meta:
        model = Cluster
        fields = '__all__'
        widgets = {
            'password': PasswordInput(),
        }

class ClusterAdmin(admin.ModelAdmin):
    form = ClusterForm

admin.site.register(Executor)
admin.site.register(Job,JobAdmin)
admin.site.register(Cluster, ClusterAdmin)
admin.site.register(File, FileAdmin)

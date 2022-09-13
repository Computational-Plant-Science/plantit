from django.contrib import admin
from django.forms import ModelForm

from plantit_web.miappe.models import *


class InvestigationForm(ModelForm):
    class Meta:
        model = Investigation
        fields = '__all__'


class InvestigationAdmin(admin.ModelAdmin):
    form = InvestigationForm


class StudyForm(ModelForm):
    class Meta:
        model = Study
        fields = '__all__'


class StudyAdmin(admin.ModelAdmin):
    form = StudyForm


class RoleForm(ModelForm):
    class Meta:
        model = Role
        fields = '__all__'


class RoleAdmin(admin.ModelAdmin):
    form = RoleForm


class FileForm(ModelForm):
    class Meta:
        model = DataFile
        fields = '__all__'


class FileAdmin(admin.ModelAdmin):
    form = FileForm


class BiologicalMaterialForm(ModelForm):
    class Meta:
        model = BiologicalMaterial
        fields = '__all__'


class BiologicalMaterialAdmin(admin.ModelAdmin):
    form = BiologicalMaterialForm


class EnvironmentParameterForm(ModelForm):
    class Meta:
        model = EnvironmentParameter
        fields = '__all__'


class EnvironmentParameterAdmin(admin.ModelAdmin):
    form = EnvironmentParameterForm


class ExperimentalFactorForm(ModelForm):
    class Meta:
        model = ExperimentalFactor
        fields = '__all__'


class ExperimentalFactorAdmin(admin.ModelAdmin):
    form = ExperimentalFactorForm


class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = '__all__'


class EventAdmin(admin.ModelAdmin):
    form = EventForm


class ObservationUnitForm(ModelForm):
    class Meta:
        model = ObservationUnit
        fields = '__all__'


class ObservationUnitAdmin(admin.ModelAdmin):
    form = ObservationUnitForm


class SampleForm(ModelForm):
    class Meta:
        model = Sample
        fields = '__all__'


class SampleAdmin(admin.ModelAdmin):
    form = SampleForm


class ObservedVariableForm(ModelForm):
    class Meta:
        model = ObservedVariable
        fields = '__all__'


class ObservedVariableAdmin(admin.ModelAdmin):
    form = ObservedVariableForm


admin.site.register(Investigation, InvestigationAdmin)
admin.site.register(Study, StudyAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(DataFile, FileAdmin)
admin.site.register(BiologicalMaterial, BiologicalMaterialAdmin)
admin.site.register(EnvironmentParameter, EnvironmentParameterAdmin)
admin.site.register(ExperimentalFactor, ExperimentalFactorAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(ObservationUnit, ObservationUnitAdmin)
admin.site.register(Sample, SampleAdmin)
admin.site.register(ObservedVariable, ObservedVariableAdmin)
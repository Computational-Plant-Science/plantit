from django.contrib import admin

from plantit.targets.models import Target


class TargetInline(admin.StackedInline):
    model = Target
    can_delete = True


class TargetAdmin(admin.ModelAdmin):
    inlines = (TargetInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(TargetAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(Target)
admin.site.register(Target, TargetAdmin)

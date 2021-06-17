from django.contrib import admin
from django.urls import re_path, include
from django.views.generic import TemplateView

from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

urlpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    re_path(r'^ping/', (lambda x: HttpResponse("pong"))),
    re_path(r'^admin/', admin.site.urls),
    # re_path(r'^accounts/', include('django.contrib.auth.urls')),
    re_path(r'^apis/v1/', include('plantit.urls')),
    # defer all other patterns to the Vue router
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]

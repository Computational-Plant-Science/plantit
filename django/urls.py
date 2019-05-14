"""dirt2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import re_path, include
from django.views.generic import TemplateView

from django.conf import settings
from django.conf.urls.static import static

from django_cas_ng import views

urlpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
        re_path(r'^admin/', admin.site.urls),
        re_path(r'^login/', views.LoginView.as_view(), name="cas_ng_login"),
        re_path(r'^logout/', views.LogoutView.as_view(), name="cas_ng_logout"),
        re_path(r'^apis/v1/', include('apis.urls')),
        #Send all other urls (besides what is listed above) to the vue router
        re_path(r'^.*$',  TemplateView.as_view(template_name='index.html')),
    ]

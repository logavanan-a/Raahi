"""
URL configuration for Raahi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import include, re_path as url, path
from django.conf import settings
from django.views.static import serve
from .views import *
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('master_data.urls')),
    path('', include('sims.urls')),
    path('', include('dashboard.urls')),
    path('', login_view, name="login"),
    path('', include('reports.urls', namespace='reports')),
    path('login/', login_view, name="login"),
    path('logout/', logout_view, name="logout"),
    path('sidebar/', sidebar_view, name="sidebar"),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # path('dashboard/', dashboard, name="dashboard"),
    path('form_validate/', form_validate, name="form_validate"),
    path('send_login_email/', send_login_email, name="send_login_email"),
    url(r'^media/(?P<path>.*)$', serve,
        {'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,
        {'document_root': settings.STATIC_ROOT}),

    
]

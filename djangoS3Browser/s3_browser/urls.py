"""s3_browser URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.urls import include, re_path
    3. Add a URL to urlpatterns:  re_path(r'^blog/', include(blog_urls))
"""
from django.conf.urls.static import static
from django.urls import re_path

from djangoS3Browser.s3_browser import settings
from djangoS3Browser.s3_browser import views

urlpatterns = [
                  re_path(r'^get_folder_items/(?P<main_folder>.+)/(?P<sort_a_z>.+)/$',
                          views.get_folder_items, name='get_folder_items'),
                  re_path(r'^upload/$', views.upload, name='upload'),
                  re_path(r'^create_folder/$', views.create_folder, name='create_folder'),
                  re_path(r'^download/$', views.download, name='download'),
                  re_path(r'^rename_file/$', views.rename_file, name='rename_file'),
                  re_path(r'^paste_file/$', views.paste_file, name='paste_file'),
                  re_path(r'^move_file/$', views.move_file, name='move_file'),
                  re_path(r'^delete_file/$', views.delete_file, name='delete_file'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

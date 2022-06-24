"""deployProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include, re_path
from web.views import server, project, deploy


urlpatterns = [
    # path('admin/', admin.site.urls),
    path(r'app01', include('app01.urls')),
    re_path("server/list/$", server.server_list, name='server_list'),
    re_path("server/add/$", server.server_add, name='server_add'),
    re_path("server/edit/(?P<sid>\d+)/$", server.server_edit, name='server_edit'),
    re_path("server/del/(?P<sid>\d+)/$", server.server_del, name='server_del'),

    re_path("project/list/$", project.project_list, name='project_list'),
    re_path("project/add/$", project.project_add, name='project_add'),
    re_path("project/edit/(?P<sid>\d+)/$", project.project_edit, name='project_edit'),
    re_path("project/del/(?P<sid>\d+)/$", project.project_del, name='sproject_del'),

    re_path("task/list/(?P<pid>\d+)/$", deploy.task_list, name='task_list'),
    re_path("task/add/(?P<pid>\d+)/$", deploy.task_add, name='task_add'),
    re_path("hook/template/(?P<tid>\d+)/$", deploy.hook_template, name='hook_template'),


    re_path("deploy/(?P<task_id>\d+)/$", deploy.deploy, name='deploy'),


]


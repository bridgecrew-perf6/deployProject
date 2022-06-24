
from django.urls import path, re_path
from app01 import views


urlpatterns = [
    path('/', views.home),
    path('/index/', views.index),
    path('/demo/', views.demo),

    re_path('/sendmsg/$', views.send_msg, name="send_msg"),
    re_path('/getmsg/$', views.get_msg, name='get_msg'),


]

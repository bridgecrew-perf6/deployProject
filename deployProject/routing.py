# @Time : 2022/6/3 19:52 
# @Author : kongsh
# @File : routing.py
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path, re_path
from app01 import consumers
from web.consumers import PublishConsumer


application = ProtocolTypeRouter({
    'websocket': URLRouter([
        # 这里些websocket相关的url与视图函数对应关系
        re_path('chat/$', consumers.ChatConsumer),
        re_path('publish/(?P<task_id>\d+)/$', PublishConsumer)

    ])
})
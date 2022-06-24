# @Time : 2022/6/4 9:22 
# @Author : kongsh
# @File : consumers.py

from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer

consumer_object_list = []


class ChatConsumer(WebsocketConsumer):

    def websocket_connect(self, message):
        """
        请求websocket链接时自动触发
        :param message:
        :return:
        """
        # 与客户端建立链接
        self.accept()
        consumer_object_list.append(self)

    def websocket_receive(self, message):
        """
        客户端发送消息时自动触发
        :param message:
        :return:
        """
        print("客户端消息：", message)
        text = message.get('text')
        # 给当前客户端发送消息【单发】
        # self.send(text_data=text)
        # 给所有客户端发送消息【群发】
        for obj in consumer_object_list:
            obj.send(text_data=text)

    def websocket_disconnect(self, message):
        """断开websocket链接时触发"""
        consumer_object_list.remove(self)
        raise StopConsumer


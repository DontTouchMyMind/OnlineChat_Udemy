from django.conf.urls import re_path

from .consumers import ChatConsumer, GroupChatConsumer


websocket_urls = [
    re_path(r'^ws/groups/$', GroupChatConsumer),
    re_path(r'^ws/chat/(?P<group_id>\d+)/$', ChatConsumer)
]

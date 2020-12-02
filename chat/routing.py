from django.conf.urls import url

from .consumers import ChatConsumer, GroupChatConsumer


websocket_urls = [
    url(r'^ws/groups/$', GroupChatConsumer),
    url(r'^ws/chat/(?P<group_id>\d+)/$', ChatConsumer)
]

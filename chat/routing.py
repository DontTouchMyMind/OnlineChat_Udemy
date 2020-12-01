from django.conf.urls import url

from .consumers import ChatConsumer, GroupChatConsumer


websocket_urls = [
    url(r'^ws/groups/$', GroupChatConsumer.as_asgi()),
    url(r'^ws/chat/(?P<group_id>\d+)/$', ChatConsumer.as_asgi())
]

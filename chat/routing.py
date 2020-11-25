from django.conf.urls import url

from .consumers import ChatConsumer, AsyncChatConsumer, BaseSyncConsumer, AsyncBaseSyncConsumer, ChatJsonConsumer, ChatAsyncJsonConsumer, MyChatConsumer, MyAsyncChatConsumer


websocket_urls = [
    url(r'^ws/chat/$', ChatConsumer.as_asgi()),
    url(r'^ws/async_chat/$', AsyncChatConsumer.as_asgi()),
    url(r'^ws/base_sync_chat/$', BaseSyncConsumer.as_asgi()),
    url(r'^ws/base_async_chat/$', AsyncBaseSyncConsumer.as_asgi()),
    url(r'^ws/json_chat/$', ChatJsonConsumer.as_asgi()),
    url(r'^ws/async_json_chat/$', ChatAsyncJsonConsumer.as_asgi()),
    url(r'^ws/chat/(?P<room_name>\w+)/$', MyChatConsumer.as_asgi()),
    url(r'^ws/async_chat/(?P<room_name>\w+)/$', MyAsyncChatConsumer.as_asgi()),
]
